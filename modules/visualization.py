# modules/visualization.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_score_distribution(df: pd.DataFrame, column: str):
    """
    Tạo biểu đồ histogram để hiển thị phân bố điểm của một cột điểm được chọn.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu.
        column (str): Tên cột điểm cần vẽ biểu đồ.

    Returns:
        go.Figure: Đối tượng biểu đồ Plotly.
    """
    if column not in df.columns:
        return go.Figure().update_layout(title_text=f"Cột '{column}' không tồn tại.")

    # Chuyển đổi cột sang dạng số, bỏ qua lỗi
    scores = pd.to_numeric(df[column], errors='coerce').dropna()

    if scores.empty:
        return go.Figure().update_layout(title_text=f"Không có dữ liệu hợp lệ trong cột '{column}'.")

    fig = px.histogram(
        scores,
        x=column,
        nbins=20,  # Số lượng cột trong biểu đồ
        title=f"Phân bố điểm của cột '{column}'",
        labels={column: "Điểm số"},
        marginal="box", # Thêm box plot ở trên để xem Q1, Q3, median
    )

    # Thêm đường thẳng đứng chỉ giá trị trung bình
    mean_value = scores.mean()
    fig.add_vline(
        x=mean_value,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Trung bình: {mean_value:.2f}",
        annotation_position="top right"
    )

    fig.update_layout(
        xaxis_title="Điểm số",
        yaxis_title="Số lượng học sinh",
        title_x=0.5, # Căn giữa tiêu đề
    )
    return fig

def plot_anomalies_by_class(df_anomalies: pd.DataFrame):
    """
    Tạo biểu đồ cột hiển thị số lượng bất thường được tìm thấy ở mỗi lớp.

    Args:
        df_anomalies (pd.DataFrame): DataFrame chứa thông tin các bất thường.

    Returns:
        go.Figure: Đối tượng biểu đồ Plotly.
    """
    if df_anomalies.empty or 'lop' not in df_anomalies.columns:
        return go.Figure().update_layout(title_text="Không có dữ liệu bất thường để thống kê theo lớp.")

    # Đếm số lượng bất thường theo lớp
    anomaly_counts = df_anomalies['lop'].value_counts().reset_index()
    anomaly_counts.columns = ['lop', 'count']
    
    # Sắp xếp để các lớp có nhiều bất thường nhất hiển thị trước
    anomaly_counts = anomaly_counts.sort_values('count', ascending=False)

    fig = px.bar(
        anomaly_counts,
        x='lop',
        y='count',
        title="Thống kê số lượng bất thường theo Lớp",
        labels={'lop': 'Lớp', 'count': 'Số lượng bất thường'},
        text='count' # Hiển thị số lượng trên mỗi cột
    )
    
    fig.update_layout(title_x=0.5)
    return fig

def plot_anomaly_types(df_anomalies: pd.DataFrame):
    """
    Tạo biểu đồ tròn để hiển thị tỷ lệ của các loại bất thường khác nhau.

    Args:
        df_anomalies (pd.DataFrame): DataFrame chứa thông tin các bất thường.

    Returns:
        go.Figure: Đối tượng biểu đồ Plotly.
    """
    if df_anomalies.empty or 'LoaiBatThuong' not in df_anomalies.columns:
        return go.Figure().update_layout(title_text="Không có dữ liệu để phân loại bất thường.")

    type_counts = df_anomalies['LoaiBatThuong'].value_counts().reset_index()
    type_counts.columns = ['LoaiBatThuong', 'count']

    fig = px.pie(
        type_counts,
        names='LoaiBatThuong',
        values='count',
        title="Tỷ lệ các loại bất thường",
        hole=0.3, # Tạo lỗ ở giữa cho đẹp hơn (donut chart)
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_x=0.5)
    return fig

def plot_anomalies_heatmap(df: pd.DataFrame, df_anomalies: pd.DataFrame, score_cols: list):
    """
    Tạo heatmap của bảng điểm và đánh dấu các ô có điểm bất thường.

    Args:
        df (pd.DataFrame): DataFrame gốc chứa toàn bộ điểm.
        df_anomalies (pd.DataFrame): DataFrame chỉ chứa các bất thường.
        score_cols (list): Danh sách các cột điểm để hiển thị trên heatmap.

    Returns:
        go.Figure: Đối tượng biểu đồ Plotly.
    """
    # Chuẩn bị dữ liệu cho heatmap
    df_heatmap = df.set_index('MaHS')[score_cols].apply(pd.to_numeric, errors='coerce')

    fig = go.Figure(data=go.Heatmap(
        z=df_heatmap.values,
        x=df_heatmap.columns,
        y=df_heatmap.index,
        colorscale='Viridis',
        colorbar={'title': 'Điểm'},
    ))

    # Thêm các đánh dấu cho điểm bất thường
    annotations = []
    for _, row in df_anomalies.iterrows():
        mahs = row['MaHS']
        cot_diem = row['CotDiem']
        
        # Kiểm tra xem mahs và cot_diem có trong heatmap không
        if mahs in df_heatmap.index and cot_diem in df_heatmap.columns:
             annotations.append(
                go.layout.Annotation(
                    x=cot_diem,
                    y=mahs,
                    text="🔥",  # Dùng emoji hoặc ký tự để đánh dấu
                    showarrow=False,
                    font=dict(color='white' if pd.notna(df_heatmap.loc[mahs, cot_diem]) and df_heatmap.loc[mahs, cot_diem] < 5 else 'black', size=14)
                )
            )

    fig.update_layout(
        title='Heatmap chi tiết điểm và các vị trí bất thường (🔥)',
        xaxis_title='Môn học / Cột điểm',
        yaxis_title='Mã Học Sinh',
        yaxis={'type': 'category', 'autorange': 'reversed'}, # Đảo ngược trục y để dễ nhìn
        annotations=annotations,
        title_x=0.5,
    )

    return fig