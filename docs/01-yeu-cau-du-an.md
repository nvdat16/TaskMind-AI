# Tài liệu yêu cầu dự án

## 1. Tên dự án
AI Agent quản lý công việc cá nhân.

## 2. Mục tiêu
Xây dựng một hệ thống hỗ trợ người dùng quản lý công việc cá nhân bằng cách kết hợp quản lý task truyền thống với AI để:
- thêm công việc nhanh bằng ngôn ngữ tự nhiên,
- gợi ý ưu tiên công việc,
- nhắc việc đúng thời điểm,
- hỗ trợ lập kế hoạch trong ngày,
- tạo báo cáo cuối ngày/cuối tuần.

## 3. Vấn đề cần giải quyết
Người dùng thường gặp các khó khăn sau:
- quên việc cần làm,
- không biết ưu tiên việc nào trước,
- khó theo dõi tiến độ,
- công việc cá nhân và công việc công ty bị lẫn nhau,
- không có công cụ nhắc việc mang tính ngữ cảnh.

## 4. Đối tượng người dùng mục tiêu
### Nhóm chính
- Người đi làm cá nhân cần quản lý nhiều việc hằng ngày.

### Nhóm mở rộng
- Freelancer.
- Sinh viên.
- Người làm nhiều dự án cùng lúc.

## 5. Bài toán cốt lõi
Hệ thống cần giúp người dùng trả lời nhanh các câu hỏi sau:
- Hôm nay tôi nên làm gì trước?
- Việc nào đang gấp nhất?
- Tôi còn bao nhiêu việc chưa xong?
- Việc nào bị trễ deadline?
- Cuối ngày tôi đã làm được gì?

## 6. Yêu cầu chức năng
### 6.1. Quản lý người dùng
- Đăng ký tài khoản.
- Đăng nhập/đăng xuất.
- Cập nhật hồ sơ cơ bản.
- Thiết lập múi giờ, giờ làm việc, thời gian nhắc việc.

### 6.2. Quản lý task
- Tạo task thủ công.
- Tạo task bằng chat AI.
- Sửa task.
- Xóa task.
- Gắn deadline.
- Gắn priority.
- Gắn category/tag.
- Chia trạng thái task: todo, doing, done, snoozed, cancelled.
- Tìm kiếm và lọc task.

### 6.3. AI assistant
- Hiểu câu lệnh tiếng Việt tự nhiên.
- Trích xuất thông tin từ câu người dùng.
- Gợi ý ưu tiên.
- Gợi ý kế hoạch làm việc hôm nay.
- Trả lời câu hỏi về task hiện tại.
- Tạo tóm tắt cuối ngày.

### 6.4. Reminder và notification
- Nhắc việc theo thời gian đã đặt.
- Nhắc việc gần deadline.
- Gửi daily summary.
- Gửi weekly review.

### 6.5. Dashboard và báo cáo
- Hiển thị công việc hôm nay.
- Hiển thị việc quá hạn.
- Hiển thị việc ưu tiên cao.
- Báo cáo số việc hoàn thành mỗi ngày.
- Báo cáo tỷ lệ hoàn thành.

## 7. Yêu cầu phi chức năng
- Giao diện đơn giản, dễ dùng.
- Phản hồi nhanh cho các thao tác CRUD.
- AI trả lời rõ ràng, ngắn gọn, có hành động cụ thể.
- Hệ thống dễ mở rộng thêm tích hợp như Telegram hoặc Google Calendar.
- Dữ liệu người dùng cần được bảo vệ.

## 8. Luồng sử dụng chính
1. Người dùng đăng nhập.
2. Người dùng tạo task bằng form hoặc chat.
3. Hệ thống lưu task.
4. AI phân tích và gợi ý priority/category/reminder nếu cần.
5. Dashboard hiển thị task theo ngày và trạng thái.
6. Scheduler gửi nhắc việc.
7. Cuối ngày AI tạo tóm tắt.

## 9. Chỉ số đánh giá thành công MVP
- Người dùng tạo được task trong dưới 10 giây.
- Có thể hỏi AI “hôm nay làm gì” và nhận câu trả lời hữu ích.
- Reminder hoạt động đúng giờ.
- Daily summary tạo được nội dung ngắn, dễ hiểu.
- Toàn bộ luồng CRUD task hoạt động ổn định.

## 10. Ràng buộc và giả định
- Giai đoạn đầu ưu tiên web app.
- Chỉ cần 1 người dùng hoặc nhóm nhỏ thử nghiệm nội bộ.
- AI dùng API bên ngoài thay vì train model riêng.
- Chưa ưu tiên mobile app ở phiên bản đầu.

## 11. Rủi ro chính
- AI hiểu sai thời gian tiếng Việt.
- Priority gợi ý chưa sát thực tế.
- Reminder lệch do timezone.
- Người dùng kỳ vọng AI tự hành động quá nhiều.

## 12. Hướng xử lý rủi ro
- Xác nhận lại với thao tác quan trọng.
- Chuẩn hóa schema output của AI.
- Log prompt/output để dễ debug.
- Dùng rule-based cho các case thời gian phổ biến.
