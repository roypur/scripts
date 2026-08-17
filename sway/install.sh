#!/usr/bin/env bash
export CURRENT_DIR=$(realpath $(dirname $0))
export UV_PROJECT_ENVIRONMENT="${CURRENT_DIR}/venv"
export VIRTUAL_ENV="${UV_PROJECT_ENVIRONMENT}"
uv sync
