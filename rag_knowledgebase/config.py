from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    atlas_model_api_key: str = os.getenv("ATLAS_MODEL_API_KEY", "")
    voyage_api_key: str = os.getenv("VOYAGE_API_KEY", "")
    mongodb_uri: str = os.getenv("MONGODB_URI", "")
    mongodb_db: str = os.getenv("MONGODB_DB", "rag_knowledgebase")
    vector_collection: str = os.getenv("VECTOR_COLLECTION", "legal_documents")
    graph_collection: str = os.getenv("GRAPH_COLLECTION", "legal_graph")
    relations_collection: str = os.getenv("RELATIONS_COLLECTION", "legal_relations")
    vector_index_name: str = os.getenv("VECTOR_INDEX_NAME", "legal_vector_index")
    search_index_name: str = os.getenv("SEARCH_INDEX_NAME", "legal_search_index")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "voyage-4-large")
    embedding_dims: int = int(os.getenv("EMBEDDING_DIMS", "1024"))
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    top_k: int = int(os.getenv("TOP_K", "5"))
    dataset_path: Path = Path(os.getenv("DATASET_PATH", "data/legal_docs.jsonl"))
    relations_path: Path = Path(os.getenv("RELATIONS_PATH", "data/legal_relations.jsonl"))
    ontology_path: Path = Path(os.getenv("ONTOLOGY_PATH", "data/legal_ontology.ttl"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
