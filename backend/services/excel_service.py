import pandas as pd
import os


class ExcelService:
    def __init__(self, filename="results.xlsx"):
        self._filename = filename

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

if __name__ == '__main__':
    writer = ExcelService()
    writer.write('Фитинг 234ыва', '123-ddd', '12-33-44')
    writer.write('адаптер 324234dfdfd', '333-dfsfs', '45-67-89', 2)