#!/bin/sh
set -e
poetry install -vv --no-interaction --without dev $1
poetry run python -m ipykernel install --user --name=musii-kit-0.6
