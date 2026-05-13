# EcoRoute IQ

EcoRoute IQ is a full-stack carbon footprint intelligence platform built with a React + Vite frontend, a Flask REST API backend, and SQLite persistence.

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
