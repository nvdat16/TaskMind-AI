# Sơ đồ database

## 1. Danh sách bảng

### Bảng `users`
- `id` (uuid, pk)
- `email` (varchar, unique)
- `password_hash` (varchar)
- `full_name` (varchar)
- `timezone` (varchar)
- `work_start_time` (time, nullable)
- `work_end_time` (time, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Bảng `tasks`
- `id` (uuid, pk)
- `user_id` (uuid, fk -> users.id)
- `title` (varchar)
- `description` (text, nullable)
- `category` (varchar)
- `priority` (varchar)
- `status` (varchar)
- `due_at` (timestamp, nullable)
- `estimated_minutes` (integer, nullable)
- `reminder_at` (timestamp, nullable)
- `source_type` (varchar) // manual, ai_chat, import
- `ai_metadata` (jsonb, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Bảng `task_logs`
- `id` (uuid, pk)
- `task_id` (uuid, fk -> tasks.id)
- `action_type` (varchar)
- `old_value` (jsonb, nullable)
- `new_value` (jsonb, nullable)
- `created_at` (timestamp)

### Bảng `chat_messages`
- `id` (uuid, pk)
- `user_id` (uuid, fk -> users.id)
- `role` (varchar) // user, assistant, system
- `message_text` (text)
- `intent` (varchar, nullable)
- `structured_data` (jsonb, nullable)
- `created_at` (timestamp)

### Bảng `daily_reports`
- `id` (uuid, pk)
- `user_id` (uuid, fk -> users.id)
- `report_date` (date)
- `summary_text` (text)
- `total_tasks` (integer)
- `completed_tasks` (integer)
- `overdue_tasks` (integer)
- `productivity_score` (integer, nullable)
- `created_at` (timestamp)

### Bảng `notifications`
- `id` (uuid, pk)
- `user_id` (uuid, fk -> users.id)
- `task_id` (uuid, fk -> tasks.id, nullable)
- `channel` (varchar) // in_app, email, telegram
- `notification_type` (varchar) // reminder, summary, weekly_review
- `scheduled_at` (timestamp)
- `sent_at` (timestamp, nullable)
- `status` (varchar)
- `payload` (jsonb, nullable)
- `created_at` (timestamp)

## 2. Quan hệ chính
- Một `user` có nhiều `tasks`.
- Một `task` có nhiều `task_logs`.
- Một `user` có nhiều `chat_messages`.
- Một `user` có nhiều `daily_reports`.
- Một `user` có nhiều `notifications`.
- Một `task` có thể liên kết với nhiều `notifications`.

## 3. ERD dạng văn bản
```text
users 1 --- n tasks
users 1 --- n chat_messages
users 1 --- n daily_reports
users 1 --- n notifications
tasks 1 --- n task_logs
tasks 1 --- n notifications
```

## 4. Quy ước dữ liệu đề xuất
### `priority`
- `low`
- `medium`
- `high`
- `urgent`

### `status`
- `todo`
- `doing`
- `done`
- `snoozed`
- `cancelled`

### `source_type`
- `manual`
- `ai_chat`
- `import`

## 5. Gợi ý mở rộng sau MVP
- Thêm bảng `task_tags` và `tags` nếu cần gắn nhiều tag.
- Thêm bảng `integrations` cho Google Calendar/Telegram.
- Thêm bảng `weekly_reports`.
- Thêm bảng `user_preferences` nếu cần cấu hình chi tiết hơn.
