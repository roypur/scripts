#!/usr/bin/env bash
export CURRENT_DIR=$(realpath $(dirname $0))

if ! [ -f "${CURRENT_DIR}/venv/bin/activate" ]; then
	python -m venv "${CURRENT_DIR}/venv"
	source "${CURRENT_DIR}/venv/bin/activate"
	pip install --upgrade pip
	pip install evdev
else
	source "${CURRENT_DIR}/venv/bin/activate"
fi

exec ${CURRENT_DIR}/spam_enter.py
