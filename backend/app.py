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
from werkzeug.security import check_password_hash, generate_password_hash

from utils.analyzer import analyze_lifestyle


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ecoroute-iq-dev-secret")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.permanent_session_lifetime = timedelta(days=7)

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173", "http://127.0.0.1:4173"],
)


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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
    user = connection.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
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


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    connection = get_db()
    existing = connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        connection.close()
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    cursor = connection.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, created_at),
    )
    connection.commit()
    user_id = cursor.lastrowid
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
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    connection = get_db()
    user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    connection.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return jsonify({
        "message": "Login successful.",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"], "created_at": user["created_at"]},
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
        value = data.get(field)
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
    connection.execute(
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
    connection.commit()
    connection.close()

    return jsonify({"message": "Analysis completed.", "analysis": result, "created_at": created_at})


@app.route("/history", methods=["GET"])
@require_auth
def history():
    connection = get_db()
    rows = connection.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY datetime(created_at) DESC",
        (session["user_id"],),
    ).fetchall()
    connection.close()
    return jsonify({"history": [serialize_analysis(row) for row in rows]})


@app.route("/profile", methods=["GET"])
@require_auth
def profile():
    user = get_current_user()
    connection = get_db()
    analyses = connection.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY datetime(created_at) DESC",
        (session["user_id"],),
    ).fetchall()
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
        port=int(os.environ.get("PORT", 8000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )