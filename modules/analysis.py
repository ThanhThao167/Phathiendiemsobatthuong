# modules/analysis.py

import pandas as pd
import numpy as np

def assign_severity(z_score, threshold):
    """
    Gán nhãn mức độ bất thường (Cao, Trung bình, Thấp) dựa trên Z-score.
    """
    abs_z = abs(z_score)
    if abs_z > threshold + 1.0:
        return "Cao"
    elif abs_z > threshold + 0.5:
        return "Trung bình"
    else:
        return "Thấp"

def detect_inter_student_anomalies(df, score_cols, z_thresh):
    """
    Phát hiện các điểm bất thường bằng cách so sánh điểm của một học sinh
    với điểm trung bình của toàn bộ nhóm/lớp (Inter-student).

    Sử dụng phương pháp Z-score.
    - Z-score = (Điểm - Điểm trung bình) / Độ lệch chuẩn
    - Một điểm được coi là bất thường nếu |Z-score| > ngưỡng (z_thresh).

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu điểm.
        score_cols (list): Danh sách các cột điểm cần phân tích.
        z_thresh (float): Ngưỡng Z-score để xác định bất thường.

    Returns:
        list: Danh sách các điểm bất thường được tìm thấy.
    """
    anomalies = []
    # Chỉ xử lý trên các cột có kiểu dữ liệu số
    numeric_df = df[score_cols].apply(pd.to_numeric, errors='coerce')

    for col in score_cols:
        # Loại bỏ các giá trị NaN để tính toán thống kê
        col_data = numeric_df[col].dropna()
        if len(col_data) < 2:  # Cần ít nhất 2 điểm để tính độ lệch chuẩn
            continue

        mean = col_data.mean()
        std = col_data.std()

        # Tránh trường hợp độ lệch chuẩn bằng 0 (khi tất cả các điểm giống nhau)
        if std == 0:
            continue

        # Tính Z-score cho tất cả học sinh trong cột hiện tại
        z_scores = (numeric_df[col] - mean) / std

        # Tìm các học sinh có |Z-score| vượt ngưỡng
        outliers = df[z_scores.abs() > z_thresh]

        for i, row in outliers.iterrows():
            student_score = row[col]
            student_z_score = z_scores.loc[i]
            
            anomaly_type = "Điểm cao bất thường" if student_z_score > 0 else "Điểm thấp bất thường"
            explanation = (
                f"Điểm {student_score} ở cột '{col}' "
                f"cao hơn đáng kể so với trung bình lớp ({mean:.2f})."
            ) if student_z_score > 0 else (
                f"Điểm {student_score} ở cột '{col}' "
                f"thấp hơn đáng kể so với trung bình lớp ({mean:.2f})."
            )

            anomalies.append({
                "MaHS": row.get("MaHS", "N/A"),
                "lop": row.get("lop", "N/A"),
                "CotDiem": col,
                "DiemBatThuong": student_score,
                "LoaiBatThuong": anomaly_type,
                "MucDo": assign_severity(student_z_score, z_thresh),
                "GiaiThich": explanation
            })
            
    return anomalies

def detect_intra_student_subject_deviation(df, subject_cols, z_thresh):
    """
    Phát hiện một môn học có điểm lệch bất thường so với năng lực chung
    của chính học sinh đó (Intra-student).

    Ví dụ: Một học sinh học rất đều các môn 8.0, 8.5, nhưng có một môn 3.0.

    Args:
        df (pd.DataFrame): DataFrame chứa điểm tổng hợp.
        subject_cols (list): Danh sách các cột môn học.
        z_thresh (float): Ngưỡng Z-score cá nhân để xác định bất thường.

    Returns:
        list: Danh sách các bất thường được tìm thấy.
    """
    anomalies = []
    # Chỉ xử lý trên các cột có kiểu dữ liệu số
    numeric_df = df[subject_cols].apply(pd.to_numeric, errors='coerce')

    for i, row in numeric_df.iterrows():
        # Lấy điểm của các môn mà học sinh này có
        student_scores = row.dropna()
        if len(student_scores) < 3: # Cần ít nhất 3 môn để phân tích có ý nghĩa
            continue

        mean = student_scores.mean()
        std = student_scores.std()

        if std == 0:
            continue

        # Tính Z-score cá nhân cho từng môn học của học sinh này
        personal_z_scores = (student_scores - mean) / std

        # Tìm các môn có |Z-score cá nhân| vượt ngưỡng
        outlier_subjects = personal_z_scores[personal_z_scores.abs() > z_thresh]
        
        for subject, z_score in outlier_subjects.items():
            anomaly_score = student_scores[subject]
            anomaly_type = "Môn có điểm lệch cao" if z_score > 0 else "Môn có điểm lệch thấp"
            explanation = (
                f"Điểm môn '{subject}' ({anomaly_score}) "
                f"cao hơn hẳn so với năng lực chung của học sinh này (trung bình các môn: {mean:.2f})."
            ) if z_score > 0 else (
                f"Điểm môn '{subject}' ({anomaly_score}) "
                f"thấp hơn hẳn so với năng lực chung của học sinh này (trung bình các môn: {mean:.2f})."
            )

            anomalies.append({
                "MaHS": df.loc[i].get("MaHS", "N/A"),
                "lop": df.loc[i].get("lop", "N/A"),
                "CotDiem": subject,
                "DiemBatThuong": anomaly_score,
                "LoaiBatThuong": anomaly_type,
                "MucDo": assign_severity(z_score, z_thresh),
                "GiaiThich": explanation
            })

    return anomalies

def detect_missing_values(df, score_cols):
    """
    Phát hiện các giá trị điểm bị thiếu (NaN).
    """
    anomalies = []
    for col in score_cols:
        missing_df = df[df[col].isnull()]
        for i, row in missing_df.iterrows():
            anomalies.append({
                "MaHS": row.get("MaHS", "N/A"),
                "lop": row.get("lop", "N/A"),
                "CotDiem": col,
                "DiemBatThuong": "Bị trống",
                "LoaiBatThuong": "Thiếu dữ liệu",
                "MucDo": "Cao",
                "GiaiThich": f"Học sinh này bị thiếu điểm ở cột '{col}'."
            })
    return anomalies

def run_component_analysis(df, z_thresh):
    """
    Hàm tổng hợp để chạy phân tích cho file điểm thành phần.
    """
    # Xác định các cột điểm thành phần
    score_cols = ['TX1', 'TX2', 'TX3', 'GK', 'CK']
    # Loại bỏ các cột không tồn tại trong DataFrame
    score_cols = [col for col in score_cols if col in df.columns]

    # Phát hiện bất thường so với lớp
    inter_anomalies = detect_inter_student_anomalies(df, score_cols, z_thresh)
    
    # Phát hiện thiếu dữ liệu
    missing_anomalies = detect_missing_values(df, score_cols)

    # Tổng hợp kết quả
    all_anomalies = inter_anomalies + missing_anomalies
    
    if not all_anomalies:
        return pd.DataFrame()
        
    return pd.DataFrame(all_anomalies)

def run_summary_analysis(df, z_thresh):
    """
    Hàm tổng hợp để chạy phân tích cho file điểm tổng hợp.
    """
    # Xác định các cột môn học
    subject_cols = ['Toan', 'Van', 'Ly', 'Hoa', 'Ngoaingu', 'Su', 'Tin', 'Sinh', 'Dia']
    # Loại bỏ các cột không tồn tại trong DataFrame
    subject_cols = [col for col in subject_cols if col in df.columns]

    # Bất thường 1: So sánh điểm môn với cả lớp
    inter_anomalies = detect_inter_student_anomalies(df, subject_cols, z_thresh)

    # Bất thường 2: Một môn lệch so với năng lực chung của chính HS
    intra_anomalies = detect_intra_student_subject_deviation(df, subject_cols, z_thresh)

    # Phát hiện thiếu dữ liệu
    missing_anomalies = detect_missing_values(df, subject_cols)

    # Tổng hợp kết quả
    all_anomalies = inter_anomalies + intra_anomalies + missing_anomalies

    if not all_anomalies:
        return pd.DataFrame()

    return pd.DataFrame(all_anomalies)