# Phạm vi MVP

## 1. Mục tiêu MVP
Tạo phiên bản đầu tiên có thể dùng thực tế cho 1 người hoặc nhóm nhỏ, tập trung vào quản lý task và hỗ trợ AI cơ bản.

## 2. Những gì bắt buộc phải có

### 2.1. Tài khoản
- Đăng ký.
- Đăng nhập.
- Đăng xuất.

### 2.2. Quản lý task
- Tạo task.
- Sửa task.
- Xóa task.
- Đổi trạng thái task.
- Gắn deadline.
- Gắn priority.
- Gắn category.
- Xem danh sách task.
- Lọc task theo trạng thái và priority.

### 2.3. AI hỗ trợ cơ bản
- Người dùng nhập câu tự nhiên để tạo task.
- AI trích xuất title, deadline, priority, category.
- AI trả lời câu hỏi: “Hôm nay tôi nên làm gì?”
- AI tạo daily summary.

### 2.4. Reminder
- Đặt reminder cho task.
- Tự động nhắc task sắp tới hạn.

### 2.5. Dashboard
- Hiển thị task hôm nay.
- Hiển thị task overdue.
- Hiển thị task ưu tiên cao.

## 3. Những gì chưa làm trong MVP
- Mobile app.
- Tích hợp Google Calendar.
- Tích hợp Notion/Trello/Todoist.
- Voice assistant.
- AI tự động lập lịch đầy đủ nhiều ngày.
- Phân tích năng suất chuyên sâu.
- Multi-user collaboration phức tạp.

## 4. Tiêu chí hoàn thành MVP
- CRUD task chạy ổn định.
- Chat AI tạo task hoạt động được với input tiếng Việt phổ biến.
- Reminder chạy đúng logic cơ bản.
- Daily summary tạo được nội dung hữu ích.
- Có bản deploy demo dùng được.

## 5. Phạm vi release đầu tiên khuyến nghị
- 1 dashboard web.
- 1 khu vực chat AI.
- 1 backend API.
- 1 database production.
- 1 scheduler gửi reminder.

## 6. Nguyên tắc kiểm soát phạm vi
- Nếu chức năng không giúp người dùng quản lý task tốt hơn ngay trong 1 tuần đầu sử dụng, đưa ra sau MVP.
- Ưu tiên luồng: thêm việc -> xem việc -> nhắc việc -> tổng kết.
- Không thêm tính năng phức tạp nếu CRUD và reminder chưa thật ổn định.
