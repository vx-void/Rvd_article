# backend/app/services/excel_service.py
import pandas as pd
import os

EXCEL_DIR = os.path.join(os.getcwd(), 'exports')
os.makedirs(EXCEL_DIR, exist_ok=True)

def generate_report(results: list, original_query: str):
    df_data = []
    for item in results:
        df_data.append({
            'запрос': original_query,
            'наименование': item.get('name'),
            'артикул': item.get('article'),
            'количество': 1  # или брать из данных
        })

    df = pd.DataFrame(df_data)
    file_path = os.path.join(EXCEL_DIR, f"report_{hash(original_query)}.xlsx")
    df.to_excel(file_path, index=False)
    return file_path
