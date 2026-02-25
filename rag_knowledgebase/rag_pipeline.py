from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError

# LangChain still emits this warning on Python 3.14+ due to optional pydantic.v1 shims.
# Suppress only this known compatibility warning to keep logs clean.
warnings.filterwarnings(
    "ignore",
    message=r".*Core Pydantic V1 functionality isn't compatible with Python 3\.14 or greater.*",
    category=UserWarning,
)

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI

from .config import Settings
from .db_setup import ensure_database_objects
from .mongodb import get_client


class VoyageEmbeddings(Embeddings):
    atlas_embeddings_url = "https://ai.mongodb.com/v1/embeddings"

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("ATLAS_MODEL_API_KEY ou VOYAGE_API_KEY é obrigatório para embeddings")
        self.api_key = api_key
        self.model = model

    def _embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        payload = {
            "input": texts,
            "model": self.model,
            "input_type": input_type,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.atlas_embeddings_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with request.urlopen(req, timeout=60) as resp:
                response = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Atlas Embedding API error ({exc.code}): {detail}") from exc

        data = response.get("data", [])
        embeddings = [item.get("embedding") for item in data if "embedding" in item]
        if not embeddings:
            raise RuntimeError(f"No embeddings returned by Atlas API: {response}")
        return embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, input_type="document")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], input_type="query")[0]


def _load_mongodb_graph_store():
    try:
        from langchain_mongodb.graphrag.graph import MongoDBGraphStore  # type: ignore

        return MongoDBGraphStore
    except Exception as exc:
        raise ImportError(
            "MongoDBGraphStore não disponível. Instale langchain-mongodb>=0.11.0."
        ) from exc


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _build_documents(rows: list[dict[str, Any]]) -> list[Document]:
    docs: list[Document] = []
    for row in rows:
        content = (
            f"Title: {row.get('title', '')}\n"
            f"Type: {row.get('doc_type', '')}\n"
            f"Topic: {row.get('topic', '')}\n"
            f"Text: {row.get('text', '')}"
        )
        metadata = {
            "doc_id": row.get("doc_id"),
            "doc_type": row.get("doc_type"),
            "title": row.get("title"),
            "topic": row.get("topic"),
            "jurisdiction": row.get("jurisdiction"),
            "source_type": row.get("source_type"),
            "published_on": row.get("published_on"),
            "decision_date": row.get("decision_date"),
            "case_number": row.get("case_number"),
            "text": row.get("text", ""),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def _vector_store(settings: Settings) -> MongoDBAtlasVectorSearch:
    embeddings = VoyageEmbeddings(
        api_key=settings.atlas_model_api_key or settings.voyage_api_key,
        model=settings.embedding_model,
    )
    client = get_client(settings.mongodb_uri)
    collection = client[settings.mongodb_db][settings.vector_collection]

    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=settings.vector_index_name,
        text_key="text",
        embedding_key="embedding",
        relevance_score_fn="cosine",
    )


def ingest_vector_documents(settings: Settings) -> int:
    rows = _load_jsonl(settings.dataset_path)
    relations = _load_jsonl(settings.relations_path)
    if not rows:
        raise ValueError(f"Dataset file not found or empty: {settings.dataset_path}")

    ensure_database_objects(settings)
    vector_store = _vector_store(settings)
    docs = _build_documents(rows)

    client = get_client(settings.mongodb_uri)
    collection = client[settings.mongodb_db][settings.vector_collection]
    collection.delete_many({})
    if relations:
        rel_collection = client[settings.mongodb_db][settings.relations_collection]
        rel_collection.delete_many({})
        rel_collection.insert_many(relations)

    vector_store.add_documents(docs)
    return len(docs)


def ingest_graph_documents(settings: Settings) -> int:
    rows = _load_jsonl(settings.dataset_path)
    docs = _build_documents(rows)
    if not docs:
        raise ValueError(f"Dataset file not found or empty: {settings.dataset_path}")

    graph_store_cls = _load_mongodb_graph_store()
    llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
    graph_store = graph_store_cls(
        connection_string=settings.mongodb_uri,
        database_name=settings.mongodb_db,
        collection_name=settings.graph_collection,
        entity_extraction_model=llm,
    )
    graph_store.add_documents(docs)
    return len(docs)


def _answer_with_context(settings: Settings, question: str, docs: list[Document]) -> str:
    llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)

    context = "\n\n".join(
        f"[{i}] {d.metadata.get('title')}\n{d.metadata.get('text')}"
        for i, d in enumerate(docs, start=1)
    )

    messages = [
        SystemMessage(
            content=(
                "Você é um assistente jurídico. Responda com base apenas no contexto fornecido. "
                "Se faltar base legal no contexto, diga explicitamente que não há evidência suficiente."
            )
        ),
        HumanMessage(
            content=(
                f"Pergunta:\n{question}\n\n"
                f"Contexto jurídico recuperado:\n{context}\n\n"
                "Responda em português, citando os títulos dos documentos usados."
            )
        ),
    ]

    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


def _graph_answer(settings: Settings, question: str) -> str | None:
    answer, _ = _graph_answer_with_error(settings, question)
    return answer


def _graph_answer_with_error(settings: Settings, question: str) -> tuple[str | None, str | None]:
    try:
        graph_store_cls = _load_mongodb_graph_store()
        llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
        graph_store = graph_store_cls(
            connection_string=settings.mongodb_uri,
            database_name=settings.mongodb_db,
            collection_name=settings.graph_collection,
            entity_extraction_model=llm,
        )

        result = graph_store.chat_response(question)
        if hasattr(result, "content"):
            return str(result.content), None
        return str(result), None
    except Exception as primary_exc:  # noqa: BLE001
        # Fallback using persisted relation triplets when GraphStore query fails.
        try:
            client = get_client(settings.mongodb_uri)
            rel_collection = client[settings.mongodb_db][settings.relations_collection]
            edges = list(rel_collection.find({}, {"_id": 0, "source": 1, "relation": 1, "target": 1}).limit(30))
            if not edges:
                return None, f"{type(primary_exc).__name__}: {primary_exc}"

            facts = "\n".join(
                f"- {e.get('source')} --{e.get('relation')}--> {e.get('target')}" for e in edges
            )
            llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
            prompt = (
                "Você é um assistente jurídico. Use somente os fatos de relacionamento abaixo.\n"
                f"Pergunta: {question}\n\n"
                f"Fatos:\n{facts}\n\n"
                "Responda em português e diga quando os fatos forem insuficientes."
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content if hasattr(response, "content") else str(response)
            return str(content), f"{type(primary_exc).__name__}: {primary_exc}"
        except Exception as fallback_exc:  # noqa: BLE001
            return None, (
                f"GraphStore error: {type(primary_exc).__name__}: {primary_exc}; "
                f"fallback error: {type(fallback_exc).__name__}: {fallback_exc}"
            )


def legal_rag_answer(settings: Settings, question: str, use_graph_rag: bool) -> dict[str, Any]:
    vector_store = _vector_store(settings)
    docs_with_scores = vector_store.similarity_search_with_score(question, k=settings.top_k)
    docs = [d for d, _ in docs_with_scores]

    vector_answer = _answer_with_context(settings, question, docs)

    retrieved = [
        {
            "title": d.metadata.get("title", "Untitled"),
            "text": d.metadata.get("text", d.page_content),
            "metadata": d.metadata,
        }
        for d in docs
    ]

    output: dict[str, Any] = {
        "vector_answer": vector_answer,
        "retrieved_docs": retrieved,
    }

    if use_graph_rag:
        graph_answer, graph_error = _graph_answer_with_error(settings, question)
        output["graph_answer"] = graph_answer
        if graph_error:
            output["graph_error"] = graph_error

    return output
