#!/usr/bin/env bash
export CURRENT_DIR=$(realpath $(dirname $0))

if ! [ -f "${CURRENT_DIR}/venv/bin/activate" ]; then
	uv venv "${CURRENT_DIR}/venv"
	source "${CURRENT_DIR}/venv/bin/activate"
	uv pip install pydantic
else
	source "${CURRENT_DIR}/venv/bin/activate"
fi

exec ${CURRENT_DIR}/sway-status.py
