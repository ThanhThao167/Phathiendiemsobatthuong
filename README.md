Ứng dụng Phát hiện Điểm Bất thường 🔎
Một ứng dụng web được xây dựng bằng Streamlit để giúp giáo viên và nhà trường nhanh chóng xác định các trường hợp học sinh có điểm số bất thường, dựa trên dữ liệu điểm thành phần và điểm tổng hợp môn học.

✨ Các tính năng chính
Ứng dụng cung cấp một bộ công cụ mạnh mẽ để phân tích và trực quan hóa dữ liệu điểm:

📥 Quản lý Tệp linh hoạt:

Cho phép tải xuống tệp mẫu (CSV hoặc Excel) để người dùng hiểu rõ định dạng dữ liệu chuẩn.

Người dùng có thể điền dữ liệu thực tế và tải tệp của mình lên để phân tích.


⚙️ Cấu hình Phân tích Tùy chỉnh:

Cho phép điều chỉnh các ngưỡng phát hiện bất thường như Z-score và ngưỡng lệch điểm.

Lựa chọn giữa các phương pháp phát hiện khác nhau: Z-score, IQR, hoặc kết hợp cả hai.

🔍 Phân tích Bất thường Đa chiều:

Tự động phân loại các bất thường: điểm cao/thấp đột biến so với lớp, hoặc một môn có điểm chênh lệch lớn so với năng lực chung của chính học sinh đó.

Gán nhãn mức độ bất thường (Cao, Trung bình, Thấp) để ưu tiên xử lý.

Cung cấp bộ lọc mạnh mẽ để xem kết quả theo mức độ, lớp, hoặc học sinh cụ thể.

📊 Trực quan hóa Dữ liệu Thông minh:

Hiển thị biểu đồ phân bố điểm để xem cái nhìn tổng quan.

Thống kê số lượng bất thường theo từng lớp và từng loại.

Cung cấp Heatmap chi tiết, làm nổi bật các điểm số bất thường trong bảng dữ liệu lớn.

💾 Xuất Báo cáo Tiện lợi:

Xuất kết quả ra tệp CSV (toàn bộ dữ liệu hoặc chỉ các trường hợp bất thường).

Xuất báo cáo đầy đủ ra tệp Excel với nhiều sheet được sắp xếp khoa học (Dữ liệu gốc, Bảng bất thường, Tóm tắt).

🛠️ Công nghệ sử dụng
Ngôn ngữ: Python 3.9+

Framework: Streamlit

Thư viện xử lý dữ liệu: Pandas, NumPy

Thư viện trực quan hóa: Plotly

🚀 Cài đặt và Chạy ứng dụng tại local
Để chạy ứng dụng trên máy của bạn, hãy làm theo các bước sau:

Clone repository này về máy:

Bash

git clone https://github.com/your-username/anomalydetection.git
cd anomalydetection
Tạo và kích hoạt môi trường ảo:

Bash

# Dành cho macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Dành cho Windows
python -m venv venv
.\venv\Scripts\activate
Cài đặt các thư viện cần thiết:

Bash

pip install -r requirements.txt
Chạy ứng dụng Streamlit:

Bash

streamlit run app.py
Mở trình duyệt và truy cập vào địa chỉ http://localhost:8501.

📖 Cách sử dụng
Truy cập ứng dụng.

Tại thanh sidebar bên trái, tải tệp mẫu để xem cấu trúc dữ liệu.

Điều chỉnh các tham số phân tích như ngưỡng Z-score nếu cần.

Tải lên tệp (CSV hoặc Excel) chứa dữ liệu điểm của bạn.

Xem kết quả phân tích trong các tab: Bảng chi tiết, Trực quan hóa, và Heatmap.

Sử dụng các bộ lọc để thu hẹp phạm vi dữ liệu.

Xuất báo cáo ra tệp CSV hoặc Excel để lưu trữ và chia sẻ.