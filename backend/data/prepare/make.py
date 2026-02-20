import csv
import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

# Константы
PERSIST_DIRECTORY = Path('../chroma')
RAW_DATA_PATH = Path('../../data/raw/articles.json')


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

        # Создаем текст для эмбеддинга
        embedding_text = f"{full_name} {raw_name} {standard} {thread} {armature_type}"

        article = {
            'article': row['article'],
            'name': full_name,
            'description': raw_name,
            'standard': standard,
            'thread': thread,
            'armature': armature_code,  # male/female/interlock
            'armature_name': armature_type,
            'angle': angle if angle != 0 else None,
            'dy': int(dy) if dy and dy.strip() and dy.isdigit() else None,
            'series': series,
            's_key': row.get('s_key'),
            'o_ring': row.get('o_ring') == 'true',
            'usit': row.get('usit'),
            'component_type': 'fitting',
            'embedding_text': embedding_text
        }
        articles.append(article)

    return articles


def process_adapters(refs):
    """Обработка переходников"""
    articles = []

    rows, enc = read_csv_with_fallback('adapters_rows.csv')
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
        elif arm1_info.get('type') == 'штуцер' or arm2_info.get('type') == 'штуцер':
            armature = 'штуцер'
        elif arm1_info.get('type') == 'гайка' or arm2_info.get('type') == 'гайка':
            armature = 'гайка'

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

        # Создаем текст для эмбеддинга
        embedding_text = f"{full_name} {raw_name} {std1} {std2} {thread1} {thread2}"

        article = {
            'article': row['article'],
            'name': full_name,
            'description': raw_name,
            'standard': f"{std1}-{std2}" if std1 and std2 else std1 or std2,
            'thread': f"{thread1}-{thread2}" if thread1 and thread2 else thread1 or thread2,
            'armature': armature,
            'armature_name': f"{arm1_info.get('name', '')} → {arm2_info.get('name', '')}",
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
            'embedding_text': embedding_text
        }
        articles.append(article)

    return articles


def create_chroma_collection():
    """Создание или получение коллекции ChromaDB"""
    # Создаем директорию для персистенции
    PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Инициализация клиента ChromaDB
    client = chromadb.PersistentClient(path=str(PERSIST_DIRECTORY))

    # Используем эмбеддинги по умолчанию (all-MiniLM-L6-v2)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Удаляем коллекцию если она существует (для пересоздания)
    try:
        client.delete_collection("hydraulic_fittings")
    except:
        pass

    # Создаем коллекцию
    collection = client.create_collection(
        name="hydraulic_fittings",
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Гидравлические фитинги и переходники"}
    )

    return collection


def load_articles_from_json():
    """Загрузка статей из JSON файла"""
    if not RAW_DATA_PATH.exists():
        print(f"Файл не найден: {RAW_DATA_PATH}")
        return []

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Загружено {len(data)} записей из JSON")
    return data


def prepare_for_chromadb(articles):
    """Подготовка данных для загрузки в ChromaDB"""
    ids = []
    documents = []
    metadatas = []

    for i, article in enumerate(articles):
        # Генерируем уникальный ID
        doc_id = f"{article['article']}_{article['component_type']}_{i}"
        ids.append(doc_id)

        # Используем embedding_text для документа
        doc_text = article.get('embedding_text', article['name'])
        documents.append(doc_text)

        # Подготавливаем метаданные (убираем None значения)
        metadata = {}
        for key, value in article.items():
            if key not in ['embedding_text'] and value is not None:
                # ChromaDB требует строки для метаданных
                if isinstance(value, bool):
                    metadata[key] = str(value)
                elif isinstance(value, (int, float)):
                    metadata[key] = value
                elif value:
                    metadata[key] = str(value)

        metadatas.append(metadata)

    return ids, documents, metadatas


def load_to_chromadb(collection, articles):
    """Загрузка данных в ChromaDB"""
    ids, documents, metadatas = prepare_for_chromadb(articles)

    # Загружаем батчами по 100 записей
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"  Загружено {end_idx} из {len(ids)} записей")

    return len(ids)


def query_examples(collection):
    """Примеры запросов к базе данных"""
    print("\n" + "=" * 50)
    print("Примеры поиска в ChromaDB")
    print("=" * 50)

    # Пример 1: Поиск фитингов с резьбой 1/2"
    results = collection.query(
        query_texts=["BSP 1/2\" гайка"],
        n_results=3
    )

    print("\nПоиск: 'BSP 1/2\" гайка'")
    for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
    )):
        print(f"\n{i + 1}. Артикул: {metadata.get('article', 'N/A')}")
        print(f"   Наименование: {metadata.get('name', 'N/A')}")
        print(f"   Релевантность: {1 - distance:.4f}")

    # Пример 2: Поиск переходников
    results = collection.query(
        query_texts=["переходник BSP DKOL"],
        n_results=3
    )

    print("\nПоиск: 'переходник BSP DKOL'")
    for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
    )):
        print(f"\n{i + 1}. Артикул: {metadata.get('article', 'N/A')}")
        print(f"   Наименование: {metadata.get('name', 'N/A')}")
        print(f"   Релевантность: {1 - distance:.4f}")


def main():
    print("=" * 50)
    print("Загрузка данных в ChromaDB")
    print("=" * 50)

    # Проверяем, есть ли уже JSON файл
    if RAW_DATA_PATH.exists():
        print(f"\nЗагрузка данных из {RAW_DATA_PATH}")
        articles = load_articles_from_json()
    else:
        print("\nJSON файл не найден. Создаем данные из CSV...")

        print("Загрузка справочников...")
        refs = load_references()

        print("\nТипы арматуры:")
        for arm_id, arm_info in refs['armature'].items():
            print(f"  ID {arm_id}: {arm_info['name']} -> {arm_info['type']}")

        print("\nОбработка фитингов...")
        fittings = process_fittings(refs)
        print(f"Загружено {len(fittings)} фитингов")

        print("\nОбработка переходников...")
        adapters = process_adapters(refs)
        print(f"Загружено {len(adapters)} переходников")

        articles = fittings + adapters

        # Сохраняем в JSON для будущего использования
        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RAW_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\nДанные сохранены в {RAW_DATA_PATH}")

    print(f"\nВсего записей для загрузки: {len(articles)}")

    # Статистика по типам
    if articles:
        male_count = sum(1 for a in articles if a.get('armature') == 'male')
        female_count = sum(1 for a in articles if a.get('armature') == 'female')
        interlock_count = sum(1 for a in articles if a.get('armature') == 'interlock')

        print(f"\nСтатистика по типам:")
        print(f"    штуцер (male): {male_count}")
        print(f"    гайка (female): {female_count}")
        print(f"    Interlock: {interlock_count}")

    # Создание коллекции ChromaDB
    print(f"\nСоздание коллекции ChromaDB в {PERSIST_DIRECTORY}...")
    collection = create_chroma_collection()

    # Загрузка данных
    print("\nЗагрузка данных в ChromaDB...")
    total_loaded = load_to_chromadb(collection, articles)

    print(f"\n✅ Успешно загружено {total_loaded} записей в ChromaDB")
    print(f"📁 База данных сохранена в: {PERSIST_DIRECTORY}")

    # Статистика по коллекции
    collection_stats = collection.count()
    print(f"\nСтатистика коллекции:")
    print(f"  Всего записей: {collection_stats}")

    # Примеры поиска
    query_examples(collection)


if __name__ == '__main__':
    main()