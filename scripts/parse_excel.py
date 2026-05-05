import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

EXCEL_PATH = r"D:\西北投资\2026-win\其他工作\制度\关于印发《中交西北投资发展有限公司规章制度汇编》的通知_32158520260324085552\附件1：中交西北投资发展有限公司规章制度框架清单（截至2026年1月） .xlsx"
OUT_PATH = r"D:\西北投资\制度助理\data\regulations.json"

df = pd.read_excel(EXCEL_PATH, header=1)
df.columns = ['module_no','module','item_no','item','reg_no','name','doc_no',
               'issued_date','suggestion','level','type','doc_type',
               'dept','status','remark']

df[['module_no','module']] = df[['module_no','module']].ffill()
df[['item_no','item']] = df[['item_no','item']].ffill()

regulations = []
for _, row in df.iterrows():
    reg_no = str(row['reg_no']).strip() if pd.notna(row['reg_no']) else ''
    name = str(row['name']).strip() if pd.notna(row['name']) else ''
    if not reg_no or reg_no == 'nan' or not name or name == 'nan':
        continue
    regulations.append({
        'id': reg_no,
        'name': name,
        'module_no': str(row['module_no']).strip() if pd.notna(row['module_no']) else '',
        'module': str(row['module']).strip() if pd.notna(row['module']) else '',
        'item_no': str(row['item_no']).strip() if pd.notna(row['item_no']) else '',
        'item': str(row['item']).strip() if pd.notna(row['item']) else '',
        'doc_no': str(row['doc_no']).strip() if pd.notna(row['doc_no']) else '',
        'issued_date': str(row['issued_date']).strip() if pd.notna(row['issued_date']) else '',
        'suggestion': str(row['suggestion']).strip() if pd.notna(row['suggestion']) else '',
        'level': str(row['level']).strip() if pd.notna(row['level']) else '',
        'type': str(row['type']).strip() if pd.notna(row['type']) else '',
        'doc_type': str(row['doc_type']).strip() if pd.notna(row['doc_type']) else '',
        'dept': str(row['dept']).strip() if pd.notna(row['dept']) else '',
        'status': str(row['status']).strip() if pd.notna(row['status']) else '',
        'remark': str(row['remark']).strip() if pd.notna(row['remark']) else '',
    })

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(regulations, f, ensure_ascii=False, indent=2)

print(f'解析完成：{len(regulations)} 条制度 → {OUT_PATH}')
