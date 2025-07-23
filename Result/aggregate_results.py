#!/usr/bin/env python3
"""
aggregate_all_results.py

Đọc tất cả các file JSON kết quả chạy thuật toán trong thư mục /mnt/data 
có định dạng tên:
  Results_U_<customer>_<beta>_Num_<instance>.txt_<Depot>_CL*.json

và xuất ra 1 file Excel tổng hợp với các cột:
  customer, beta, instance, Depot, Objective, Time, Solution
"""

import json
import pandas as pd
import re
from pathlib import Path

def parse_filename(stem: str) -> dict:
    """
    Tách metadata từ tên file:
    Results_U_<customer>_<beta>_Num_<instance>.txt_<Depot>_CL<...>.json
    """
    pattern = (
        r'Results_U_(?P<customer>\d+)_'
        r'(?P<beta>[\d.]+)_Num_'
        r'(?P<instance>\d+)\.txt_'
        r'(?P<Depot>\w+)_CL\d+'
    )
    m = re.match(pattern, stem)
    if not m:
        raise ValueError(f"Tên file không đúng định dạng: {stem}")
    d = m.groupdict()
    d['customer'] = int(d['customer'])
    d['beta']     = float(d['beta'])
    d['instance'] = int(d['instance'])
    return d

def load_records(json_path: Path, params: dict) -> list:
    """
    Đọc file JSON line-delimited, mỗi dòng chứa keys: best_fitness, runtime, best_solution
    Trả về list of dict, mỗi dict ghép metadata và nội dung:
      customer, beta, instance, Depot, Objective, Time, Solution
    """
    records = []
    with json_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            records.append({
                'customer':  params['customer'],
                'beta':      params['beta'],
                'instance':  params['instance'],
                'Depot':     params['Depot'],
                'Objective': entry.get('best_fitness'),
                'Time':      entry.get('runtime'),
                'Solution':  entry.get('best_solution'),
            })
    return records

def main():
    data_dir    = Path(r'D:\HueTT\prepare for Phd\problem 4_ resupply\code_final\ressupply_luyen\Result\20250718_luyen_old_version')
    output_xlsx = data_dir / 'all_analysis_results.xlsx'

    all_records = []
    for json_file in data_dir.glob('Results_U_*.json'):
        params = parse_filename(json_file.stem)
        all_records.extend(load_records(json_file, params))

    df = pd.DataFrame(all_records)
    df.to_excel(output_xlsx, index=False)
    print(f"Đã lưu file tổng hợp: {output_xlsx}")

if __name__ == "__main__":
    main()
