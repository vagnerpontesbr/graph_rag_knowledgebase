from __future__ import annotations

import json
import sys

import streamlit as st

from rag_knowledgebase.config import get_settings
from rag_knowledgebase.dataset import generate_legal_dataset
from rag_knowledgebase.db_setup import ensure_database_objects
from rag_knowledgebase.rag_pipeline import (
    ingest_graph_documents,
    ingest_vector_documents,
    legal_rag_answer,
)


st.set_page_config(page_title="Graph RAG Knowledgebase", layout="wide")

REQUIRED_PYTHON = "3.14.3"
CURRENT_PYTHON = ".".join(map(str, sys.version_info[:3]))
if CURRENT_PYTHON != REQUIRED_PYTHON:
    st.error(
        f"Versão de Python inválida: {CURRENT_PYTHON}. "
        f"Esta aplicação requer Python {REQUIRED_PYTHON}."
    )
    st.stop()

settings = get_settings()


def _validate_required_env() -> list[str]:
    required = {
        "ATLAS_MODEL_API_KEY (or VOYAGE_API_KEY)": settings.atlas_model_api_key or settings.voyage_api_key,
        "OPENAI_API_KEY": settings.openai_api_key,
        "MONGODB_URI": settings.mongodb_uri,
    }
    missing: list[str] = []
    for key, value in required.items():
        if not value or "<" in value:
            missing.append(key)
    return missing


missing_env = _validate_required_env()
if missing_env:
    st.error(
        "Erro de configuração: variáveis de ambiente obrigatórias não configuradas: "
        + ", ".join(missing_env)
    )
    st.info("Configure o arquivo .env e reinicie o app.")
    st.stop()

if "db_setup_result" not in st.session_state:
    with st.spinner("Validando estrutura do banco e criando objetos..."):
        try:
            st.session_state["db_setup_result"] = ensure_database_objects(settings)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Erro ao inicializar estrutura do banco de dados: {exc}")
            st.stop()

db_setup_result = st.session_state["db_setup_result"]
if db_setup_result.get("db_created"):
    st.success(
        "Banco de dados não encontrado. Criando os objetos em banco de dados "
        "(collections, indexes e search indexes)."
    )
elif db_setup_result.get("init_skipped"):
    st.info("Banco de dados já existe. Scripts de inicialização não foram executados.")
if db_setup_result.get("warnings"):
    for warning in db_setup_result["warnings"]:
        st.warning(warning)

MONGODB_LOGO_SVG = """
<svg width="220" height="58" viewBox="0 0 360 96" fill="none" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(20,12)">
    <path d="M22 2C17 12 8 23 8 39c0 14 8 23 14 31 6-8 14-17 14-31C36 23 27 12 22 2z" fill="#00ED64"/>
    <path d="M22 15v43" stroke="#001E2B" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M22 58c3-5 7-10 12-14" stroke="#001E2B" stroke-width="2" stroke-linecap="round"/>
  </g>
  <text x="78" y="60" fill="#001E2B" font-family="Arial, Helvetica, sans-serif" font-size="42" font-weight="700">MongoDB</text>
</svg>
"""

st.markdown(
    f"""
<style>
:root {{
  --mdb-dark: #001E2B;
  --mdb-green: #00ED64;
  --mdb-bg: #F7FBF9;
  --mdb-text: #0E2E22;
}}

.stApp {{
  background-color: var(--mdb-bg);
}}

[data-testid="stSidebar"] {{
  background: var(--mdb-dark);
}}
[data-testid="stSidebar"] * {{
  color: #EAF8F1 !important;
}}
.config-box {{
  background: #FFFFFF;
  border: 1px solid #C7D5DD;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 6px;
}}
.config-box pre {{
  margin: 0;
  white-space: pre-wrap;
  color: #001E2B !important;
  font-family: "Courier New", monospace;
  font-size: 0.82rem;
  line-height: 1.35;
}}

.mongo-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #E6FFF1 0%, #F7FBF9 70%);
  border: 1px solid #CDEEDD;
  border-radius: 14px;
  padding: 16px 20px;
  margin: 0 0 14px 0;
}}

.mongo-title {{
  color: var(--mdb-dark);
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 4px;
}}

.mongo-subtitle {{
  color: var(--mdb-text);
  font-size: 0.95rem;
}}

.mongo-logo {{
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 220px;
}}

div.stButton > button {{
  background: var(--mdb-green);
  color: var(--mdb-dark);
  border: 1px solid #00CF59;
  font-weight: 700;
  border-radius: 10px;
}}
div.stButton > button:hover {{
  background: #00CF59;
  color: var(--mdb-dark);
}}
</style>

<div class="mongo-header">
  <div>
    <div class="mongo-title">Graph RAG Knowledgebase - Legal Docs</div>
    <div class="mongo-subtitle">Python + LangChain + MongoDB + Streamlit</div>
  </div>
  <div class="mongo-logo">{MONGODB_LOGO_SVG}</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Configuration")
    config_text = (
        f"DB: {settings.mongodb_db}\n"
        f"Vector collection: {settings.vector_collection}\n"
        f"Graph collection: {settings.graph_collection}\n"
        f"Relations collection: {settings.relations_collection}\n"
        f"Vector index: {settings.vector_index_name}\n"
        f"Search index: {settings.search_index_name}\n"
        f"Embeddings provider: Voyage AI\n"
        f"Embedding model: {settings.embedding_model}\n"
        f"LLM: {settings.llm_model}"
    )
    st.markdown(
        f'<div class="config-box"><pre>{config_text}</pre></div>',
        unsafe_allow_html=True,
    )

    if st.button("Generate legal dataset"):
        docs_count, rel_count = generate_legal_dataset(
            dataset_path=settings.dataset_path,
            relations_path=settings.relations_path,
            ontology_path=settings.ontology_path,
        )
        st.success(f"Dataset generated: {docs_count} docs, {rel_count} relations")

    if st.button("Ingest vector store"):
        inserted = ingest_vector_documents(settings)
        st.success(f"Vector ingest completed. Documents added: {inserted}")

    if st.button("Ingest graph store (optional)"):
        try:
            ingested = ingest_graph_documents(settings)
            st.success(f"Graph ingest completed. Documents processed: {ingested}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Graph ingest failed: {exc}")

st.subheader("Ask a legal question")
question = st.text_area(
    "Question",
    value="Qual dispositivo legal fundamenta responsabilidade por dano moral?",
    height=90,
)
use_graph_rag = st.checkbox("Also run GraphRAG answer", value=True)

if st.button("Run retrieval"):
    result = legal_rag_answer(settings=settings, question=question, use_graph_rag=use_graph_rag)

    st.markdown("### Vector RAG answer")
    st.write(result["vector_answer"])

    st.markdown("### Retrieved contexts")
    for i, d in enumerate(result["retrieved_docs"], start=1):
        with st.expander(f"Context {i}: {d['title']}"):
            st.write(d["text"])
            st.json(d["metadata"])

    if use_graph_rag:
        st.markdown("### GraphRAG answer")
        if result.get("graph_answer"):
            st.write(result["graph_answer"])
            if result.get("graph_error"):
                st.warning(
                    "GraphRAG principal falhou e foi usado fallback por relações. "
                    f"Detalhe: {result['graph_error']}"
                )
        else:
            detail = result.get("graph_error", "sem detalhes")
            st.info(
                "GraphRAG answer unavailable. Check graph ingest and model credentials. "
                f"Detail: {detail}"
            )

st.markdown("---")
st.caption("Dataset files")
for p in [settings.dataset_path, settings.relations_path, settings.ontology_path]:
    if p.exists():
        st.code(str(p))

if settings.dataset_path.exists():
    preview = []
    with settings.dataset_path.open("r", encoding="utf-8") as f:
        for _ in range(3):
            line = f.readline().strip()
            if not line:
                break
            preview.append(json.loads(line))
    if preview:
        st.markdown("### Dataset preview")
        st.json(preview)
