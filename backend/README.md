# Backend

FastAPI backend cho AI Agent quản lý công việc cá nhân.

## Chạy local
1. Tạo virtual environment.
2. Cài dependencies từ `requirements.txt`.
3. Tạo file `.env` từ `.env.example` ở root.
4. Chạy:
   - `uvicorn app.main:app --reload --port 8000`

## Endpoint test
- `GET /`
- `GET /api/v1/health`
