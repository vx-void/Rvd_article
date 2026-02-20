import csv
import json
from pathlib import Path


def read_csv_with_fallback(filepath):
    """Читает CSV с автоматическим определением кодировки и возвращает список строк"""
    encodings_to_try = ['utf-8', 'windows-1251', 'cp1251', 'koi8-r', 'latin-1']

    for enc in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                content = f.read()
                from io import StringIO
                return list(csv.DictReader(StringIO(content))), enc
        except (UnicodeDecodeError, UnicodeError, csv.Error):
            continue

    with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
        content = f.read()
        from io import StringIO
        return list(csv.DictReader(StringIO(content))), 'latin-1 (with ignore)'


def load_references():
    """Загрузка справочников"""
    refs = {}

    # Стандарты
    rows, enc = read_csv_with_fallback('ref_standard_rows.csv')
    print(f"  ref_standard_rows.csv: {enc} ({len(rows)} строк)")
    refs['standards'] = {row['id']: row['name'] for row in rows}

    # Резьбы
    rows, enc = read_csv_with_fallback('ref_thread_rows.csv')
    print(f"  ref_thread_rows.csv: {enc} ({len(rows)} строк)")
    refs['threads'] = {}
    for row in rows:
        thread_val = row['thread']
        if '_' in thread_val:
            parts = thread_val.split('_')
            if len(parts) == 2:
                thread_val = f"M{parts[0]}x{parts[1]}"
            elif len(parts) == 3:
                thread_val = f"M{parts[0]}x{parts[1]}.{parts[2]}"
        refs['threads'][row['id']] = thread_val

    # Типы (арматура)
    rows, enc = read_csv_with_fallback('ref_armature_rows.csv')
    print(f"  ref_armature_rows.csv: {enc} ({len(rows)} строк)")
    refs['armature'] = {}
    for row in rows:
        refs['armature'][row['id']] = {
            'name': row['name'],
            'abbr': row['abbriveature'],
            'type': 'female' if 'гайка' in row['name'].lower() else
            'male' if 'штуцер' in row['name'].lower() else
            'interlock' if 'interlock' in row['name'].lower() else None
        }

    # Углы
    rows, enc = read_csv_with_fallback('ref_angle_rows.csv')
    print(f"  ref_angle_rows.csv: {enc} ({len(rows)} строк)")
    refs['angles'] = {row['id']: int(row['value']) for row in rows}

    # Серии
    rows, enc = read_csv_with_fallback('ref_seria_rows.csv')
    print(f"  ref_seria_rows.csv: {enc} ({len(rows)} строк)")
    refs['seria'] = {row['id']: row['name'] for row in rows}

    return refs


def clean_text(text):
    """Очистка текста от странных символов"""
    if not text:
        return text
    replacements = {
        '聽': ' ',
        '鈥': '-',
        '鈥橾': '',
        '鈥檚': "'",
        '\xa0': ' ',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def process_fittings(refs):
    """Обработка фитингов"""
    articles = []

    rows, enc = read_csv_with_fallback('fittings_rows.csv')
    print(f"  fittings_rows.csv: {enc} ({len(rows)} строк)")

    for row in rows:
        if not row.get('article'):
            continue

        raw_name = clean_text(row.get('name', ''))

        name_parts = []

        std_id = row.get('standard', '')
        standard = refs['standards'].get(std_id, '')

        arm_id = row.get('armature', '')
        armature_info = refs['armature'].get(arm_id, {})
        armature_type = armature_info.get('name', '')
        armature_code = armature_info.get('type', None)

        thread_id = row.get('thread', '')
        thread = refs['threads'].get(thread_id, '')

        angle_id = row.get('angle', '')
        angle = refs['angles'].get(angle_id, 0)

        dy = row.get('dy', '')
        series_id = row.get('seria', '')
        series = refs['seria'].get(series_id, '')

        # Формируем имя для поиска
        if standard:
            name_parts.append(standard)
        if dy and dy.strip():
            name_parts.append(f"Dy{dy}")
        if thread:
            name_parts.append(thread)
        if angle:
            angle_word = "прямой" if angle == 0 else f"угловой {angle}°"
            name_parts.append(angle_word)
        if armature_type:
            name_parts.append(armature_type)
        if series:
            name_parts.append(series)

        full_name = " ".join(name_parts)

        article = {
            'article': row['article'],
            'name': full_name,
            'description': raw_name,
            'standard': standard,
            'thread': thread,
            'armature': armature_code,  # male/female/interlock
            'angle': angle if angle != 0 else None,
            'dy': int(dy) if dy and dy.strip() and dy.isdigit() else None,
            'series': series,
            's_key': row.get('s_key'),
            'o_ring': row.get('o_ring') == 'true',
            'usit': row.get('usit'),
            'component_type': 'fitting',
        }
        articles.append(article)

    return articles


def process_adapters(refs):
    """Обработка переходников"""
    articles = []

    rows, enc = read_csv_with_fallback('../adapters_rows.csv')
    print(f"  adapters_rows.csv: {enc} ({len(rows)} строк)")

    for row in rows:
        if not row.get('article'):
            continue

        raw_name = clean_text(row.get('name', ''))

        std1 = refs['standards'].get(row.get('standard_1', ''), '')
        std2 = refs['standards'].get(row.get('standard_2', ''), '')

        thread1 = refs['threads'].get(row.get('thread_1', ''), '')
        thread2 = refs['threads'].get(row.get('thread_2', ''), '')

        arm1_info = refs['armature'].get(row.get('armature_1', ''), {})
        arm2_info = refs['armature'].get(row.get('armature_2', ''), {})

        angle_id = row.get('angle', '')
        angle = refs['angles'].get(angle_id, 0)

        # Определяем общий тип для поиска
        armature = None
        if arm1_info.get('type') == 'interlock' or arm2_info.get('type') == 'interlock':
            armature = 'interlock'
        elif arm1_info.get('type') == 'male' or arm2_info.get('type') == 'male':
            armature = 'male'
        elif arm1_info.get('type') == 'female' or arm2_info.get('type') == 'female':
            armature = 'female'

        # Формируем описание
        name_parts = ["Переходник"]
        if std1 and std2:
            name_parts.append(f"{std1} → {std2}")
        if thread1 and thread2:
            name_parts.append(f"{thread1} → {thread2}")
        if arm1_info.get('name') and arm2_info.get('name'):
            name_parts.append(f"{arm1_info['name']} → {arm2_info['name']}")
        if angle:
            angle_word = "прямой" if angle == 0 else f"угловой {angle}°"
            name_parts.append(angle_word)

        full_name = " ".join(name_parts)

        article = {
            'article': row['article'],
            'name': full_name,
            'description': raw_name,
            'standard': f"{std1}-{std2}" if std1 and std2 else std1 or std2,
            'thread': f"{thread1}-{thread2}" if thread1 and thread2 else thread1 or thread2,
            'armature': armature,
            'angle': angle if angle != 0 else None,
            'dy': None,
            's_key': row.get('s_key'),
            'component_type': 'adapter',
            'from_standard': std1,
            'to_standard': std2,
            'from_thread': thread1,
            'to_thread': thread2,
            'from_armature': arm1_info.get('name'),
            'to_armature': arm2_info.get('name'),
        }
        articles.append(article)

    return articles


def main():
    print("Загрузка справочников...")
    refs = load_references()

    # Проверка загрузки арматуры
    print("\nТипы арматуры:")
    for arm_id, arm_info in refs['armature'].items():
        print(f"  ID {arm_id}: {arm_info['name']} -> {arm_info['type']}")

    print("\nОбработка фитингов...")
    fittings = process_fittings(refs)
    print(f"Загружено {len(fittings)} фитингов")

    print("\nОбработка переходников...")
    adapters = process_adapters(refs)
    print(f"Загружено {len(adapters)} переходников")

    all_articles = fittings + adapters

    # Создаем директорию
    output_path = Path('../../raw/articles.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем в JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\nВсего сохранено {len(all_articles)} артикулов в {output_path}")

    # Статистика по типам
    if all_articles:
        male_count = sum(1 for a in all_articles if a.get('armature') == 'male')
        female_count = sum(1 for a in all_articles if a.get('armature') == 'female')
        interlock_count = sum(1 for a in all_articles if a.get('armature') == 'interlock')

        print(f"\nСтатистика по типам:")
        print(f"    штуцер: {male_count}")
        print(f"    гайка: {female_count}")
        print(f"    Interlock: {interlock_count}")

    # Показываем пример
    if all_articles:
        print("\nПример первых 3 записей:")
        for i, sample in enumerate(all_articles[:3]):
            print(f"\n  {i + 1}. {sample['article']}")
            print(f"     Наименование: {sample['name']}")
            print(f"     Тип: {sample['armature']}")
            print(f"     Описание: {sample['description'][:80]}...")


if __name__ == '__main__':
    main()