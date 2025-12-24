import pandas as pd
import os
from datetime import datetime


class ExcelService:
    def __init__(self, filename=None):
        if filename:
            self._filename = filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._filename = f"results_{timestamp}.xlsx"

    @property
    def filename(self):
        return self._filename

    def write(self, query: str, name: str, article: str, quantity: int = 1):
        """
        Args:
            query: Поисковый запрос
            name: Наименование компонента
            article: Артикул
            quantity: Количество
        """
        data = {
            "Запрос": [query],
            "Наименование": [name],
            "Артикул": [article],
            "Количество": [quantity],
        }
        df = pd.DataFrame(data)

        if os.path.exists(self._filename):
            existing_df = pd.read_excel(self._filename)
            result_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            result_df = df

        result_df.to_excel(self._filename, index=False)
        return self._filename