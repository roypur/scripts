#!/usr/bin/env bash
export CURRENT_DIR=$(realpath $(dirname $0))
source "${CURRENT_DIR}/venv/bin/activate"
exec ${CURRENT_DIR}/sway-lock-with-dpms.py
