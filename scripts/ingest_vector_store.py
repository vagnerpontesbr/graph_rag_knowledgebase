#!/usr/bin/env python3
import sys
from pathlib import Path

REQUIRED_PYTHON = (3, 14, 3)
if sys.version_info[:3] != REQUIRED_PYTHON:
    current = ".".join(map(str, sys.version_info[:3]))
    raise SystemExit(f"[error] Python 3.14.3 é obrigatório. Versão atual: {current}")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag_knowledgebase.config import get_settings
from rag_knowledgebase.rag_pipeline import ingest_vector_documents


def main() -> None:
    settings = get_settings()
    count = ingest_vector_documents(settings)
    print(f"[ok] Vector store ingest completed. Documents: {count}")


if __name__ == "__main__":
    main()
