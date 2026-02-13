#!/usr/bin/env python3
"""
Утилита для первоначальной индексации каталога.
Запускается один раз при установке.
"""

import json
import csv
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb


def index_from_csv(csv_path: Path, output_dir: Path):
    """Конвертирует CSV каталог в JSON + индексирует."""

    articles = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            articles.append({
                "article": row["article"],
                "name": row["name"],
                "description": row.get("description", ""),
                "standard": row.get("standard"),
                "thread": row.get("thread"),
                "armature": row.get("armature"),
                "angle": int(row["angle"]) if row.get("angle") else None,
                "dy": int(row["dy"]) if row.get("dy") else None,
            })

    # Сохраняем JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "articles.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Сохранено {len(articles)} артикулов в {json_path}")
    print("Запустите main.py для создания векторного индекса")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python indexer.py catalog.csv")
        sys.exit(1)

    index_from_csv(Path(sys.argv[1]), Path("data"))