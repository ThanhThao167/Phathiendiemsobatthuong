# modules/utils.py

import pandas as pd
import streamlit as st
from io import BytesIO

@st.cache_data(show_spinner="Đang tải và xử lý tệp...")
def load_data(uploaded_file):
    """
    Đọc dữ liệu từ tệp CSV hoặc Excel được người dùng tải lên.
    Hàm này sử dụng cache của Streamlit để tránh việc đọc lại tệp mỗi khi có thay đổi trên giao diện.

    Args:
        uploaded_file: Đối tượng tệp được trả về từ st.file_uploader.

    Returns:
        pd.DataFrame or None: DataFrame chứa dữ liệu nếu đọc thành công, ngược lại trả về None.
    """
    if uploaded_file is None:
        return None

    try:
        # Lấy phần mở rộng của tên tệp để xác định loại tệp
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            # Đọc tệp CSV, thử các encoding phổ biến nếu utf-8 lỗi
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0) # Quay lại đầu tệp để đọc lại
                df = pd.read_csv(uploaded_file, encoding='latin1')
        elif file_extension in ['xlsx', 'xls']:
            # Đọc tệp Excel
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error(f"Lỗi: Định dạng tệp '{file_extension}' không được hỗ trợ. Vui lòng sử dụng tệp CSV hoặc Excel.")
            return None
        
        # Xử lý các cột STT, MaHS có thể bị đọc thành số thực
        if 'MaHS' in df.columns:
            df['MaHS'] = df['MaHS'].astype(str)
        if 'STT' in df.columns:
            df['STT'] = df['STT'].astype(str)
            
        return df

    except Exception as e:
        st.error(f"Đã có lỗi xảy ra khi đọc tệp: {e}")
        return None

def prepare_excel_download(df_dict: dict):
    """
    Tạo một tệp Excel trong bộ nhớ với nhiều sheet từ một dictionary các DataFrame.

    Args:
        df_dict (dict): Một dictionary trong đó key là tên sheet và value là DataFrame tương ứng.

    Returns:
        bytes: Dữ liệu bytes của tệp Excel đã được tạo, sẵn sàng để tải xuống.
    """
    # Tạo một buffer in-memory để lưu file Excel
    output = BytesIO()

    # Sử dụng Pandas ExcelWriter để ghi nhiều sheet vào buffer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            # Ghi mỗi DataFrame vào một sheet riêng
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Lấy dữ liệu từ buffer sau khi đã ghi xong
    processed_data = output.getvalue()
    return processed_data