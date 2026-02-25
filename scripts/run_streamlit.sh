#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REQUIRED_PYTHON="3.14.3"
PYTHON_BIN="python3.14"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[error] python3.14 não encontrado. Instale Python ${REQUIRED_PYTHON}." >&2
  exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
if [[ "$PYTHON_VERSION" != "$REQUIRED_PYTHON" ]]; then
  echo "[error] Versão inválida: ${PYTHON_VERSION}. Requerido: ${REQUIRED_PYTHON}." >&2
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[info] Created .env from .env.example"
fi

streamlit run app.py
