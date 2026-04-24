# Chốt stack công nghệ

## 1. Mục tiêu chọn stack
- Phù hợp để xây nhanh MVP.
- Dễ tích hợp AI.
- Dễ mở rộng về sau.
- Phù hợp với web app quản lý task.

## 2. Stack đề xuất

### Frontend
- `Next.js`
- `TypeScript`
- `Tailwind CSS`
- `shadcn/ui`

Lý do:
- Phát triển UI nhanh.
- Dễ tổ chức dashboard và component.
- TypeScript giúp giảm lỗi dữ liệu khi làm việc với API.

### Backend
- `FastAPI`
- `Python 3.11+`

Lý do:
- Tích hợp AI/LLM thuận tiện.
- Dễ viết service xử lý ngôn ngữ tự nhiên.
- Nhanh để xây API cho MVP.

### Database
- `PostgreSQL`

Lý do:
- Ổn định, phổ biến, phù hợp dữ liệu quan hệ.
- Hỗ trợ `jsonb` để lưu metadata AI.

### ORM / DB access
- `SQLAlchemy`
- `Alembic`

Lý do:
- Quản lý model rõ ràng.
- Hỗ trợ migration tốt.

### AI layer
- Gọi `LLM API` bên ngoài.
- Dùng structured output / JSON schema để parse kết quả.

Lý do:
- Không cần train model riêng ở giai đoạn đầu.
- Tối ưu tốc độ làm MVP.
- Dễ thay model về sau.

### Auth
- JWT-based auth cho MVP.

### Scheduler / background jobs
- `APScheduler` hoặc `Celery + Redis`

Khuyến nghị:
- MVP dùng `APScheduler` trước.
- Khi mở rộng tải lớn thì chuyển sang `Celery + Redis`.

### Notification
- In-app notification trước.
- Mở rộng email hoặc Telegram sau.

### Deployment
- Frontend: `Vercel`
- Backend: `Render` hoặc `Railway`
- Database: `Neon` hoặc `Supabase Postgres`

## 3. Kết luận stack chốt cho MVP
- Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
- Backend: FastAPI + Python
- Database: PostgreSQL
- ORM: SQLAlchemy + Alembic
- AI: external LLM API
- Scheduler: APScheduler
- Deploy: Vercel + Render/Railway + Neon/Supabase
