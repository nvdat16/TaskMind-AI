# AI-Agents

Monorepo for a personal AI task management assistant.

## Overview

This is not just a regular task app. It is an AI-powered work assistant that can understand natural-language messages and turn them into actions. Key highlights:

- **Chat to create tasks**: users can describe tasks in plain language, and the system extracts the details automatically.
- **AI action routing**: the app does more than chat; it can decide whether to create a task, list tasks, plan the day, or generate a quick daily summary.
- **Automatic reminders**: the backend includes a scheduler that processes due notifications/reminders on a recurring basis.
- **Conversation history**: both user messages and AI responses are stored for traceability and better user experience.
- **Clear data layers**: models, schemas, services, and APIs are separated to keep the codebase easy to extend.

## Requirements

- Node.js 20+ or similar
- npm or pnpm
- Python 3.12+
- PostgreSQL (can be run via Docker Compose)

## Quick Start

### 1. Prepare environment variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Fill in the real values in `.env` if needed.
3. The `.env` file is already listed in `.gitignore` so it will not be committed.

### 2. Start PostgreSQL with Docker

From the repository root:
```bash
docker compose up -d
```

### 3. Backend

Move into the backend directory:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

Test the API:
- `http://localhost:8000/`
- `http://localhost:8000/api/v1/health`

### 4. Frontend

Move into the frontend directory:
```bash
cd frontend
npm install
npm run dev
```

Open the app at:
- `http://localhost:3000`

## Project Structure

- `frontend/`: Next.js + React UI
  - `src/app/`: pages and layout
  - `src/lib/api.ts`: API helper
- `backend/`: FastAPI server
  - `backend/app/api/v1/`: routers and endpoints
  - `backend/app/core/`: config, logging, security
  - `backend/app/services/`: business logic
  - `backend/app/models/`: ORM models
  - `backend/app/schemas/`: request/response schemas
- `docs/`: project documentation

## Key Environment Variables

- `APP_ENV`
- `NEXT_PUBLIC_API_BASE_URL`
- `APP_DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_BASE_URL`
- `CORS_ORIGINS`

## Lint & Format

### Frontend
```bash
cd frontend
npm run lint
npm run format
```

### Backend
```bash
cd backend
ruff check .
black .
```

## Testing

### Backend tests
```bash
cd backend
pytest
```

