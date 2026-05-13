# EcoRoute IQ

EcoRoute IQ is a full-stack carbon footprint intelligence platform built with a React + Vite frontend, a Flask REST API backend, and SQLite persistence.

## Architecture

- Frontend: React, Vite, React Router, Axios, Chart.js, Bootstrap
- Backend: Flask, Flask-CORS, pandas, SQLite
- Auth: session-based cookies with protected routes
- Storage: SQLite database with persisted analyses

## Features

- Authentication with signup, login, logout, and protected routes
- Lifestyle input for transport, electricity, diet, flights, and recycling
- Carbon footprint scoring and sustainability recommendations
- Dashboard, analytics, history, and profile pages
- SQLite-backed analysis storage

## Run locally

### Backend

```bash
cd backend
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default.

## Environment Variables

- `PORT`: Optional backend port override. Defaults to `8000`.
- `FLASK_DEBUG`: Set to `1` to enable Flask debug mode.
- `VITE_API_URL`: Optional frontend API base URL override.

## API Endpoints

- `POST /signup`
- `POST /login`
- `POST /logout`
- `POST /analyze`
- `GET /history`
- `GET /profile`
- `GET /health`

## Project Structure

- `backend/app.py`: Flask API and SQLite bootstrap
- `backend/utils/analyzer.py`: carbon scoring engine
- `frontend/src/pages`: application pages
- `frontend/src/components`: shared UI components
- `frontend/src/context`: auth and toast state
- `frontend/src/services/api.js`: Axios client
