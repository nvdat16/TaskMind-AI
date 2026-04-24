# AI-Agents

Monorepo cho dự án AI Agent quản lý công việc cá nhân.

## Cấu trúc
- `frontend/`: Next.js app.
- `backend/`: FastAPI app.
- `docs/`: tài liệu phân tích, thiết kế và môi trường.

## Setup nhanh
### 1. Biến môi trường
- Sao chép `.env.example` thành `.env`.

### 2. Frontend
- Thư mục: `frontend`
- Chạy dev: `npm run dev`

### 3. Backend
- Thư mục: `backend`
- Tạo virtualenv.
- Cài dependencies từ `requirements.txt`.
- Chạy dev server: `uvicorn app.main:app --reload --port 8000`

### 4. Database
- Chạy PostgreSQL bằng `docker-compose.yml`.

## Chuẩn code
- Frontend: ESLint + Prettier.
- Backend: Ruff + Black.
- Commit message: Conventional Commits.

## Môi trường
Xem thêm tại `docs/06-moi-truong.md`.
