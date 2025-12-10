from backend.data.repositories.entity import Entity
from typing import Optional


class Fitting(Entity):
    def __init__(self,
                 standard: Optional[str] = None,
                 thread: Optional[str] = None,
                 dy: int = None,
                 angle: Optional[int] = None,
                 armature: str = 'штуцер',
                 seria: Optional[str] = None,
                 d_out: Optional[int] = None,
                 s_key: Optional[str] = None,
                 usit: bool = False,
                 o_ring: bool = False):
        super().__init__()
        self.standard = standard
        self.thread = thread
        self.dy = dy
        self.angle = angle
        self.armature = armature
        self.seria = seria
        self.d_out = d_out
        self.s_key = s_key
        self.usit = usit
        self.o_ring = o_ring

    def get_query(self) -> str:
        sql_query = self.base_query + 'fittings WHERE '
        conditions = []

        attributes = self.to_dict()

        for attr, value in attributes.items():
            if value is not None:
                if isinstance(value, bool):
                    conditions.append(f"{attr} = {str(value).upper()}")
                elif isinstance(value, str):
                    if attr == 's_key':
                        conditions.append(f"{attr} LIKE '%{value}%'")
                    else:
                        conditions.append(f"{attr} = '{value}'")
                else:
                    conditions.append(f"{attr} = {value}")

        if conditions:
            sql_query += ' AND '.join(conditions)
        else:
            sql_query += '1=1'

        return sql_query

    @classmethod
    def from_filters(cls, **filters):
        return cls(**filters)


if __name__ == "__main__":
    print("=== Тестирование создания SQL запросов ===")


    print("\n1. Базовый запрос:")
    fitting1 = Fitting(standard='BSP', thread='3/4', dy=20)
    query1 = fitting1.get_query()
    print(f"Параметры: standard='BSP', thread='3/4', Dy=20")
    print(f"SQL: {query1}")


    print("\n2. Запрос с булевыми значениями:")
    fitting2 = Fitting(standard='BSP', usit=True, o_ring=False)
    query2 = fitting2.get_query()
    print(f"Параметры: standard='BSP', usit=True, o_ring=False")
    print(f"SQL: {query2}")

    # Тест 3: Запрос с поиском по s_key (LIKE)
    print("\n3. Запрос с поиском по ключу:")
    fitting3 = Fitting(s_key='BSP', armature='штуцер')
    query3 = fitting3.get_query()
    print(f"Параметры: s_key='BSP', armature='штуцер'")
    print(f"SQL: {query3}")


    print("\n4. Запрос без параметров:")
    fitting4 = Fitting()
    query4 = fitting4.get_query()
    print(f"Параметры: нет")
    print(f"SQL: {query4}")


    print("\n5. Запрос с числовыми значениями:")
    fitting5 = Fitting(angle=90, d_out=25)
    query5 = fitting5.get_query()
    print(f"Параметры: angle=90, d_out=25")
    print(f"SQL: {query5}")


    print("\n6. Запрос через from_filters:")
    filters = {
        'standard': 'BSP',
        'thread': '1/2',
        'angle': 45,
        'usit': True
    }
    fitting6 = Fitting.from_filters(**filters)
    query6 = fitting6.get_query()
    print(f"Параметры: {filters}")
    print(f"SQL: {query6}")


    print("\n7. Проверка метода to_dict():")
    fitting7 = Fitting(standard='BSP', thread='1/2', usit=True)
    dict_repr = fitting7.to_dict()
    print(f"Объект: standard='BSP', thread='1/2', usit=True")
    print(f"to_dict(): {dict_repr}")

    print("\n=== Тестирование завершено ===")