import pandas as pd
import ast
import re
from pathlib import Path

def parse_filename(filename):
    """
    Extract parameters from filenames like:
    Random_U_10_0.5_Num_1.txt_border_CL1.xlsx
    Returns a dict with keys: customer, beta, instance, Depot
    """
    base = Path(filename).stem
    pattern = (
        r'.*?_U_(?P<customer>\d+)_'
        r'(?P<beta>[\d.]+)_Num_'
        r'(?P<instance>\d+)\.txt_'
        r'(?P<Depot>\w+)_CL\d+'
    )
    m = re.match(pattern, base)
    return m.groupdict() if m else {}

def extract_values(sheet):
    """
    Given a pandas DataFrame 'sheet' without header,
    extract from the first row (index 0):
      - Objectives: columns B (idx=1) to K (idx=10)
      - Times: list of 10 values from column L (idx=11) using ast.literal_eval
      - Solutions: list of 10 (sub)lists from column M (idx=12) using ast.literal_eval
    Returns three lists of length 10.
    """
    # Objectives (10 values)
    objectives = sheet.iloc[0, 1:11].tolist()
    n = len(objectives)
    
    # Times: parse Python-list string in L1
    time_cell = sheet.iloc[0, 11]
    if isinstance(time_cell, str):
        times = ast.literal_eval(time_cell)
    elif isinstance(time_cell, (list, tuple)):
        times = list(time_cell)
    else:
        times = [float(time_cell)] * n
    
    # Solutions: parse Python-list-of-lists string in M1
    sol_cell = sheet.iloc[0, 12]
    if isinstance(sol_cell, str):
        solutions = ast.literal_eval(sol_cell)
    elif isinstance(sol_cell, (list, tuple)):
        solutions = list(sol_cell)
    else:
        solutions = [sol_cell] * n
    
    # Truncate or pad để độ dài = n
    times = (times + times[-1:]*(n - len(times)))[:n]
    solutions = (solutions + solutions[-1:]*(n - len(solutions)))[:n]
    
    return objectives, times, solutions

def process_file(filepath):
    params = parse_filename(filepath.name)
    sheet = pd.read_excel(filepath, header=None, engine='openpyxl')
    objectives, times, solutions = extract_values(sheet)

    # Build DataFrame cho file này
    df = pd.DataFrame({
        'customer': int(params.get('customer', 0)),
        'beta': float(params.get('beta', 0)),
        'instance': int(params.get('instance', 0)),
        'Depot': params.get('Depot', ''),
        'Objective': objectives,
        'Time': times,
        'Solution': solutions
    })
    return df

def main():
    data_dir = Path('Result_20250717/excel-results-summary')  # Thay đổi nếu cần
    all_dfs = []

    for file in data_dir.glob('*.xlsx'):
        all_dfs.append(process_file(file))

    result = pd.concat(all_dfs, ignore_index=True)
    output_file = 'Result_20250717/analysis_results.xlsx'
    result.to_excel(output_file, index=False)
    print(f"Saved aggregated results to: {output_file}")

if __name__ == "__main__":
    main()
