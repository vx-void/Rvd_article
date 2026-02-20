import json
from pathlib import Path

# Проверяем созданный файл
json_path = Path('../../raw/articles.json')

if not json_path.exists():
    print(f"Файл не найден: {json_path}")
    exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Всего записей: {len(data)}")
print("\nПервые 3 записи:")
for i, item in enumerate(data[:3]):
    print(f"\n{i+1}. Артикул: {item.get('article')}")
    print(f"   Наименование: {item.get('name')}")
    print(f"   Стандарт: {item.get('standard')}")
    print(f"   Резьба: {item.get('thread')}")
    print(f"   Тип: {item.get('armature')}")
    print(f"   Угол: {item.get('angle')}")