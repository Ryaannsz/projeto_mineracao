from __future__ import annotations

import json
import os
import time
from pathlib import Path

from pymongo import ASCENDING, MongoClient, ReplaceOne


DATA_DIR = Path(os.getenv("DATA_DIR", "/dados"))
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "petshop_feira")


def read_json(filename: str) -> list[dict]:
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        return json.load(source)


def connect() -> MongoClient:
    deadline = time.monotonic() + 60
    while True:
        try:
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5_000)
            client.admin.command("ping")
            return client
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(2)


def upsert_documents(database, collection_name: str, documents: list[dict], keys: list[str]) -> None:
    collection = database[collection_name]
    collection.create_index([(key, ASCENDING) for key in keys], unique=True)
    operations = [
        ReplaceOne({key: document[key] for key in keys}, document, upsert=True)
        for document in documents
    ]

    if operations:
        collection.bulk_write(operations, ordered=False)
    print(f"{collection_name}: {len(documents)} documentos carregados")


def main() -> None:
    client = connect()
    try:
        database = client[DATABASE_NAME]
        upsert_documents(
            database,
            "clientes",
            read_json("05_Feira_Clientes.json"),
            ["id_cliente"],
        )
        upsert_documents(
            database,
            "produtos",
            read_json("06_Feira_Produtos.json"),
            ["id_produto"],
        )
        upsert_documents(
            database,
            "pedidos",
            read_json("07_Feira_pedidos.json"),
            ["id_pedido"],
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
