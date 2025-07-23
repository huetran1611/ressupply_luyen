import pandas as pd
from pathlib import Path

def main():
    # Đường dẫn đến file đã tổng hợp
    data_path = 'Result/20250718_luyen_old_version/all_analysis_results.xlsx'
    
    # Đọc dữ liệu
    df = pd.read_excel(data_path)
    
    # Đảm bảo Objective là số
    df['Objective'] = pd.to_numeric(df['Objective'], errors='coerce')
    
    # Các cột cấu hình
    config_cols = ['customer', 'beta', 'instance', 'Depot']
    
    # Lấy index của bản chạy có Objective nhỏ nhất trong mỗi cấu hình
    idx_min = df.groupby(config_cols)['Objective'].idxmin()
    
    # Lọc ra DataFrame của các bản chạy tốt nhất
    best_df = df.loc[idx_min].reset_index(drop=True)
    
    # Lưu kết quả
    output_file = 'Result/20250718_luyen_old_version/best_results.xlsx'
    best_df.to_excel(output_file, index=False)
    print(f"Saved best-results per config to: {output_file}")

if __name__ == "__main__":
    main()