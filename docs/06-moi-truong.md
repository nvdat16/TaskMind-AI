# Cấu hình môi trường

## 1. Development
- Frontend chạy local tại `http://localhost:3000`.
- Backend chạy local tại `http://localhost:8000`.
- Database chạy bằng Docker Compose hoặc PostgreSQL local.
- Dùng file `.env` sao chép từ `.env.example`.

## 2. Staging
- Dùng database riêng cho staging.
- Dùng API key LLM riêng nếu cần.
- Bật logging chi tiết hơn production để test trước release.
- Domain ví dụ:
  - Frontend: `staging.your-domain.com`
  - Backend: `staging-api.your-domain.com`

## 3. Production
- Dùng database managed riêng.
- Không bật debug.
- Dùng secret manager hoặc biến môi trường từ nền tảng deploy.
- Bật monitoring và backup database.

## 4. Biến môi trường tối thiểu
- `APP_ENV`
- `NEXT_PUBLIC_API_BASE_URL`
- `DATABASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `CORS_ORIGINS`

## 5. Quy ước môi trường
- `development`: dev local.
- `staging`: test gần production.
- `production`: môi trường thật.
