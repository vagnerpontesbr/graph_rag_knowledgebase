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
from rag_knowledgebase.dataset import generate_legal_dataset


def main() -> None:
    settings = get_settings()
    docs_count, rel_count = generate_legal_dataset(
        dataset_path=settings.dataset_path,
        relations_path=settings.relations_path,
        ontology_path=settings.ontology_path,
    )
    print(f"[ok] Generated dataset: {docs_count} docs, {rel_count} relations")


if __name__ == "__main__":
    main()
