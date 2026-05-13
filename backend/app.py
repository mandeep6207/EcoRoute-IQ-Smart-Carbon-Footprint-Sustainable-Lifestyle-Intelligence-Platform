from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request, session
from flask_cors import CORS

from config import ALLOWED_ORIGINS, AppConfig
from utils.auth import build_user_payload, hash_password, verify_password
from utils.db import execute_write, fetch_all, fetch_one
from utils.analyzer import analyze_lifestyle
from utils.sanitization import sanitize_email, sanitize_number, sanitize_text


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"

app = Flask(__name__)
config = AppConfig()
app.config["SECRET_KEY"] = config.secret_key
app.config["SESSION_COOKIE_SAMESITE"] = config.session_cookie_samesite
app.config["SESSION_COOKIE_SECURE"] = config.session_cookie_secure
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_REFRESH_EACH_REQUEST"] = True
app.permanent_session_lifetime = timedelta(days=config.permanent_session_days)

CORS(
    app,
    supports_credentials=True,
    origins=ALLOWED_ORIGINS,
)


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@app.before_request
def refresh_authenticated_session() -> None:
    if session.get("user_id"):
        session.permanent = True


def init_db() -> None:
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            result TEXT NOT NULL,
            carbon_score INTEGER NOT NULL,
            monthly_co2 REAL NOT NULL,
            sustainability_rating TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    connection.commit()
    connection.close()


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped


def get_current_user() -> sqlite3.Row | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    connection = get_db()
    user = fetch_one(connection, "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,))
    connection.close()
    return user


def serialize_analysis(row: sqlite3.Row) -> dict:
    result = json.loads(row["result"])
    payload = json.loads(row["payload"])
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "payload": payload,
        "carbon_score": row["carbon_score"],
        "monthly_co2": row["monthly_co2"],
        "sustainability_rating": row["sustainability_rating"],
        "result": result,
    }


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request.", "details": str(error)}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized.", "details": str(error)}), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found.", "details": str(error)}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error.", "details": str(error)}), 500


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = sanitize_text(data.get("name"))
    email = sanitize_email(data.get("email"))
    password = sanitize_text(data.get("password"))

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    connection = get_db()
    existing = fetch_one(connection, "SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        connection.close()
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = hash_password(password)
    created_at = datetime.utcnow().isoformat()
    user_id = execute_write(
        connection,
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, created_at),
    )
    connection.close()

    session.permanent = True
    session["user_id"] = user_id
    session["user_name"] = name

    return jsonify({
        "message": "Signup successful.",
        "user": {"id": user_id, "name": name, "email": email, "created_at": created_at},
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = sanitize_email(data.get("email"))
    password = sanitize_text(data.get("password"))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    connection = get_db()
    user = fetch_one(connection, "SELECT * FROM users WHERE email = ?", (email,))
    connection.close()

    if not user or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return jsonify({
        "message": "Login successful.",
        "user": build_user_payload(user),
    })


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})


def validate_lifestyle_payload(data: dict) -> tuple[dict | None, tuple[dict, int] | None]:
    fields = [
        "daily_car_km",
        "daily_public_transport_km",
        "monthly_electricity_kwh",
        "meat_meals_per_week",
        "flights_per_year",
        "recycling_frequency",
    ]
    parsed = {}
    for field in fields:
        value = sanitize_number(data.get(field))
        if value in (None, ""):
            return None, ({"error": f"{field} is required."}, 400)
        try:
            parsed[field] = float(value)
        except (TypeError, ValueError):
            return None, ({"error": f"{field} must be a number."}, 400)
        if parsed[field] < 0:
            return None, ({"error": f"{field} cannot be negative."}, 400)
    return parsed, None


@app.route("/analyze", methods=["POST"])
@require_auth
def analyze():
    data = request.get_json(silent=True) or {}
    parsed, error = validate_lifestyle_payload(data)
    if error:
        return jsonify(error[0]), error[1]

    result = analyze_lifestyle(parsed)
    created_at = datetime.utcnow().isoformat()

    connection = get_db()
    execute_write(
        connection,
        """
        INSERT INTO analyses (
            user_id, payload, result, carbon_score, monthly_co2, sustainability_rating, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            json.dumps(parsed),
            json.dumps(result),
            result["carbon_score"],
            result["monthly_co2"],
            result["sustainability_rating"],
            created_at,
        ),
    )
    connection.close()

    return jsonify({"message": "Analysis completed.", "analysis": result, "created_at": created_at})


@app.route("/history", methods=["GET"])
@require_auth
def history():
    connection = get_db()
    rows = fetch_all(
        connection,
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY datetime(created_at) DESC",
        (session["user_id"],),
    )
    connection.close()
    return jsonify({"history": [serialize_analysis(row) for row in rows]})


@app.route("/profile", methods=["GET"])
@require_auth
def profile():
    user = get_current_user()
    connection = get_db()
    analyses = fetch_all(
        connection,
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY datetime(created_at) DESC",
        (session["user_id"],),
    )
    connection.close()

    if analyses:
        frame = pd.DataFrame([
            {
                "carbon_score": row["carbon_score"],
                "monthly_co2": row["monthly_co2"],
                "created_at": row["created_at"],
            }
            for row in analyses
        ])
        average_monthly_emissions = round(float(frame["monthly_co2"].mean()), 2)
        average_carbon_score = round(float(frame["carbon_score"].mean()), 2)
        latest_analysis = serialize_analysis(analyses[0])
        recent_analyses = [serialize_analysis(row) for row in analyses[:6]][::-1]
    else:
        average_monthly_emissions = 0.0
        average_carbon_score = 0.0
        latest_analysis = None
        recent_analyses = []

    return jsonify({
        "user": {"id": user["id"], "name": user["name"], "email": user["email"], "created_at": user["created_at"]},
        "latest_analysis": latest_analysis,
        "recent_analyses": recent_analyses,
        "average_monthly_emissions": average_monthly_emissions,
        "average_carbon_score": average_carbon_score,
        "analysis_count": len(analyses),
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config.default_port,
        debug=config.flask_debug,
        use_reloader=False,
    )