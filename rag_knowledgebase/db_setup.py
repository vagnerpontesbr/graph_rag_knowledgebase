from __future__ import annotations

from typing import Any

from pymongo.operations import SearchIndexModel

from .config import Settings
from .mongodb import get_client


def _create_collections(db_target, collection_names: list[str]) -> list[str]:
    existing = set(db_target.list_collection_names())
    created: list[str] = []
    for name in collection_names:
        if name not in existing:
            db_target.create_collection(name)
            created.append(name)
    return created


def _create_standard_indexes(vector_coll, rel_coll, graph_coll) -> None:
    vector_coll.create_index([("metadata.doc_id", 1)], name="metadata_doc_id_idx", sparse=True)
    vector_coll.create_index(
        [("metadata.doc_type", 1), ("metadata.topic", 1)],
        name="metadata_type_topic_idx",
        sparse=True,
    )
    vector_coll.create_index(
        [("metadata.jurisdiction", 1)],
        name="metadata_jurisdiction_idx",
        sparse=True,
    )
    vector_coll.create_index(
        [("metadata.source_type", 1)],
        name="metadata_source_type_idx",
        sparse=True,
    )
    vector_coll.create_index(
        [("metadata.case_number", 1)],
        name="metadata_case_number_idx",
        sparse=True,
    )

    rel_coll.create_index(
        [("source", 1), ("relation", 1), ("target", 1)],
        name="relation_triplet_uq",
        unique=True,
    )
    rel_coll.create_index([("source", 1)], name="relation_source_idx")
    rel_coll.create_index([("target", 1)], name="relation_target_idx")
    rel_coll.create_index([("relation", 1)], name="relation_name_idx")

    graph_coll.create_index([("entity_id", 1)], name="graph_entity_id_idx", sparse=True)
    graph_coll.create_index(
        [("source_id", 1), ("target_id", 1)],
        name="graph_edge_source_target_idx",
        sparse=True,
    )
    graph_coll.create_index([("relation", 1)], name="graph_relation_idx", sparse=True)


def _upsert_search_index(collection, name: str, definition: dict[str, Any], index_type: str) -> str:
    existing_names = {idx.get("name") for idx in collection.list_search_indexes()}
    if name in existing_names:
        collection.update_search_index(name, definition)
        return "updated"

    model = SearchIndexModel(name=name, type=index_type, definition=definition)
    collection.create_search_index(model)
    return "created"


def ensure_database_objects(settings: Settings) -> dict[str, Any]:
    client = get_client(settings.mongodb_uri)
    db_exists = settings.mongodb_db in client.list_database_names()

    if db_exists:
        return {
            "db_existed": True,
            "db_created": False,
            "init_skipped": True,
            "created_collections": [],
            "search_actions": {},
            "warnings": [],
        }

    db_target = client[settings.mongodb_db]
    created_collections = _create_collections(
        db_target,
        [settings.vector_collection, settings.relations_collection, settings.graph_collection],
    )

    vector_coll = db_target[settings.vector_collection]
    rel_coll = db_target[settings.relations_collection]
    graph_coll = db_target[settings.graph_collection]

    _create_standard_indexes(vector_coll, rel_coll, graph_coll)

    search_definition = {
        "mappings": {
            "dynamic": False,
            "fields": {
                "text": {"type": "string"},
                "metadata": {
                    "type": "document",
                    "fields": {
                        "title": {"type": "string"},
                        "doc_type": {"type": "string"},
                        "topic": {"type": "string"},
                        "jurisdiction": {"type": "string"},
                        "source_type": {"type": "string"},
                    },
                },
            },
        }
    }

    vector_definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": settings.embedding_dims,
                "similarity": "cosine",
            },
            {"type": "filter", "path": "metadata.doc_type"},
            {"type": "filter", "path": "metadata.topic"},
            {"type": "filter", "path": "metadata.jurisdiction"},
            {"type": "filter", "path": "metadata.source_type"},
        ]
    }

    warnings: list[str] = []
    search_actions: dict[str, str] = {}
    try:
        search_actions["search"] = _upsert_search_index(
            vector_coll,
            settings.search_index_name,
            search_definition,
            "search",
        )
        search_actions["vector"] = _upsert_search_index(
            vector_coll,
            settings.vector_index_name,
            vector_definition,
            "vectorSearch",
        )
    except Exception as exc:  # noqa: BLE001
        warnings.append(
            "Não foi possível criar/atualizar índices Atlas Search automaticamente. "
            f"Detalhe: {exc}"
        )

    return {
        "db_existed": db_exists,
        "db_created": not db_exists,
        "init_skipped": False,
        "created_collections": created_collections,
        "search_actions": search_actions,
        "warnings": warnings,
    }
