# app.py
import streamlit as st
import pandas as pd
from modules import utils, analysis, visualization

# --- 1. Cấu hình trang (Page Configuration) ---
st.set_page_config(
    page_title="Phát hiện Điểm Bất thường",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Giao diện Sidebar (Khu vực điều khiển) ---
with st.sidebar:
    st.header("⚙️ Cấu hình & Tải tệp")
    st.markdown("---")

    # Chọn loại dữ liệu để phân tích
    analysis_type = st.selectbox(
        "Chọn loại dữ liệu:",
        ("Điểm thành phần", "Điểm tổng hợp"),
        help="Chọn 'Điểm thành phần' để phân tích chi tiết các cột điểm (TX, GK, CK). Chọn 'Điểm tổng hợp' để phân tích điểm trung bình các môn học."
    )

    # Tải tệp lên
    uploaded_file = st.file_uploader(
        "Tải lên tệp CSV hoặc Excel:",
        type=["csv", "xlsx"]
    )

    st.markdown("---")

    # Tùy chỉnh tham số phát hiện
    st.subheader("Tham số phát hiện")
    z_score_threshold = st.slider(
        "Ngưỡng Z-score:",
        min_value=1.0, max_value=4.0, value=2.5, step=0.1,
        help="Một điểm được xem là bất thường nếu độ lệch của nó so với trung bình (tính bằng Z-score) lớn hơn ngưỡng này. Giá trị càng cao, độ nhạy càng thấp."
    )

# --- 3. Giao diện chính (Main Interface) ---
st.title("🔎 Ứng dụng hỗ trợ phân tích và phát hiện điểm số bất thường của học sinh")
st.write("""
    Công cụ này giúp giáo viên và nhà trường nhanh chóng xác định các trường hợp
    học sinh có điểm số bất thường, hỗ trợ việc can thiệp và theo dõi kịp thời.
""")

# --- 4. Xử lý và Hiển thị kết quả ---
if uploaded_file is not None:
    df = utils.load_data(uploaded_file)

    if df is not None:
        df_anomalies = pd.DataFrame()
        score_cols = []

        # Chạy phân tích dựa trên lựa chọn của người dùng
        with st.spinner(f'Đang phân tích dữ liệu "{analysis_type}"...'):
            if analysis_type == "Điểm thành phần":
                df_anomalies = analysis.run_component_analysis(df, z_score_threshold)
                score_cols = [col for col in ['TX1', 'TX2', 'TX3', 'GK', 'CK'] if col in df.columns]
            else: # Điểm tổng hợp
                df_anomalies = analysis.run_summary_analysis(df, z_score_threshold)
                score_cols = [col for col in ['Toan', 'Van', 'Ly', 'Hoa', 'Ngoaingu', 'Su', 'Tin', 'Sinh', 'Dia'] if col in df.columns]

        st.header("📊 Kết quả Phân tích")

        if df_anomalies.empty:
            st.success("🎉 Hoan hô! Không phát hiện thấy điểm bất thường nào với các tham số đã chọn.")
        else:
            # Hiển thị các chỉ số tổng quan
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng số bất thường", f"{len(df_anomalies)}")
            col2.metric("Số HS có bất thường", f"{df_anomalies['MaHS'].nunique()}")
            col3.metric("Số Lớp có bất thường", f"{df_anomalies['lop'].nunique()}")

            st.markdown("---")
            
            # --- Bộ lọc dữ liệu ---
            st.subheader("Lọc và Tra cứu kết quả")
            
            # Tạo các cột để đặt bộ lọc
            filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])

            # Lọc theo lớp
            unique_classes = sorted(df_anomalies['lop'].unique())
            selected_classes = filter_col1.multiselect("Lọc theo Lớp:", options=unique_classes, default=unique_classes)
            
            # Lọc theo loại bất thường
            unique_types = sorted(df_anomalies['LoaiBatThuong'].unique())
            selected_types = filter_col2.multiselect("Lọc theo Loại bất thường:", options=unique_types, default=unique_types)
            
            # Lọc theo Mức độ
            unique_severities = sorted(df_anomalies['MucDo'].unique(), key=lambda x: ['Thấp', 'Trung bình', 'Cao'].index(x))
            selected_severities = filter_col3.multiselect("Lọc theo Mức độ:", options=unique_severities, default=unique_severities)

            # Áp dụng bộ lọc
            filtered_anomalies = df_anomalies[
                (df_anomalies['lop'].isin(selected_classes)) &
                (df_anomalies['LoaiBatThuong'].isin(selected_types)) &
                (df_anomalies['MucDo'].isin(selected_severities))
            ]

            # --- Hiển thị kết quả trong các Tab ---
            tab1, tab2, tab3 = st.tabs(["📑 Bảng chi tiết", "📈 Trực quan hóa tổng quan", "🔥 Heatmap chi tiết"])

            with tab1:
                st.write(f"Hiển thị {len(filtered_anomalies)} trên {len(df_anomalies)} kết quả.")
                st.dataframe(filtered_anomalies, use_container_width=True)
                
                # --- Chức năng Xuất báo cáo ---
                st.subheader("Tải về Báo cáo")
                
                # Chuẩn bị dữ liệu cho file Excel
                excel_data = utils.prepare_excel_download({
                    "Bất thường đã lọc": filtered_anomalies,
                    "Tất cả bất thường": df_anomalies,
                    "Dữ liệu gốc": df
                })
                
                st.download_button(
                    label="📥 Tải Báo cáo Excel",
                    data=excel_data,
                    file_name=f"BaoCao_BatThuong_{analysis_type.replace(' ', '')}.xlsx"
                )

            with tab2:
                st.plotly_chart(visualization.plot_anomalies_by_class(filtered_anomalies), use_container_width=True)
                st.plotly_chart(visualization.plot_anomaly_types(filtered_anomalies), use_container_width=True)
                
                selected_column_for_dist = st.selectbox("Chọn cột điểm để xem phân bố:", score_cols)
                if selected_column_for_dist:
                    st.plotly_chart(visualization.plot_score_distribution(df, selected_column_for_dist), use_container_width=True)

            with tab3:
                st.info("Heatmap hiển thị toàn bộ bảng điểm. Các ô có dấu 🔥 là vị trí của các điểm bất thường đã được phát hiện (trước khi lọc).")
                fig_heatmap = visualization.plot_anomalies_heatmap(df, df_anomalies, score_cols)
                st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    # --- Màn hình chào mừng và Hướng dẫn ---
    st.info("Vui lòng tải tệp lên từ thanh công cụ bên trái để bắt đầu phân tích.")
    
    with st.expander("📖 Hướng dẫn và Tải file mẫu"):
        st.write("""
            1.  **Chuẩn bị tệp:** Dữ liệu của bạn cần có định dạng tương tự như tệp mẫu.
            2.  **Tải tệp mẫu:** Nhấn vào các nút bên dưới để tải về tệp CSV mẫu.
            3.  **Cấu hình:** Chọn loại dữ liệu và điều chỉnh ngưỡng Z-score ở thanh bên.
            4.  **Tải lên:** Kéo thả hoặc chọn tệp của bạn vào ô "Tải lên".
            5.  **Xem kết quả:** Kết quả phân tích sẽ tự động hiển thị.
        """)
        
        try:
            with open("assets/diemthanhphan_mau.csv", "rb") as file:
                st.download_button(
                    label="📥 Tải file mẫu Điểm Thành Phần (CSV)",
                    data=file,
                    file_name="diemthanhphan_mau.csv",
                    mime="text/csv"
                )
        except FileNotFoundError:
            st.error("Lỗi: Không tìm thấy tệp 'diemthanhphan_mau.csv'. Vui lòng đảm bảo tệp tồn tại trong thư mục 'assets'.")

        try:
            with open("assets/diemtonghop_mau.csv", "rb") as file:
                st.download_button(
                    label="📥 Tải file mẫu Điểm Tổng Hợp (CSV)",
                    data=file,
                    file_name="diemtonghop_mau.csv",
                    mime="text/csv"
                )
        except FileNotFoundError:
            st.error("Lỗi: Không tìm thấy tệp 'diemtonghop_mau.csv'. Vui lòng đảm bảo tệp tồn tại trong thư mục 'assets'.")
