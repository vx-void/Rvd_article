import asyncio
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from app.core.indexer import IndexManager
from app.config import get_settings
from app.models.article import Article
import json


async def main():
    settings = get_settings()

    print(f"Файл с данными: {settings.articles_file}")
    print(f"Директория ChromaDB: {settings.chroma_persist_dir}")

    # Загружаем данные
    with open(settings.articles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = [Article(**item) for item in data]
    print(f"Загружено {len(articles)} артикулов")

    # Создаем индекс с прогрессом
    from backend.app.core.indexer import IndexManager
    from backend.app.clients.chroma_client import ChromaManager
    from backend.app.core.embeddings import EmbeddingService

    print("\nИнициализация...")
    chroma = ChromaManager()
    embeddings = EmbeddingService()

    print("Очистка существующего индекса...")
    chroma.reset()

    # Подготовка данных
    documents = []
    metadatas = []
    ids = []

    print("Подготовка документов...")
    for i, art in enumerate(tqdm(articles, desc="Подготовка")):
        documents.append(art.to_embedding_text())
        meta = {k: v for k, v in art.model_dump().items() if v is not None}
        metadatas.append(meta)
        ids.append(f"art_{art.article}_{i}")

    # Генерация эмбеддингов с прогрессом
    print("\nГенерация эмбеддингов...")
    batch_size_embed = 32
    all_embeddings = []

    for i in tqdm(range(0, len(documents), batch_size_embed), desc="Эмбеддинги"):
        batch = documents[i:i + batch_size_embed]
        batch_embeddings = embeddings.encode(batch)
        all_embeddings.extend(batch_embeddings)

    # Добавление в ChromaDB ПАКЕТАМИ по 1000 записей
    print("\nДобавление в ChromaDB...")
    chroma_batch_size = 1000  # ChromaDB max is 5461, используем 1000 для надежности

    for i in tqdm(range(0, len(documents), chroma_batch_size), desc="Добавление в ChromaDB"):
        batch_end = min(i + chroma_batch_size, len(documents))

        batch_docs = documents[i:batch_end]
        batch_embs = all_embeddings[i:batch_end]
        batch_metas = metadatas[i:batch_end]
        batch_ids = ids[i:batch_end]

        print(f"  Пакет {i // chroma_batch_size + 1}: {len(batch_docs)} записей")

        await chroma.add(
            documents=batch_docs,
            embeddings=batch_embs,
            metadatas=batch_metas,
            ids=batch_ids,
        )

    print(f"\n✅ Индексация завершена! Добавлено {len(articles)} записей")

    # Проверка
    count = chroma.count()
    print(f"📊 В ChromaDB сейчас {count} записей")


if __name__ == '__main__':
    asyncio.run(main())