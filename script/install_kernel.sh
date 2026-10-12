#!/bin/sh
poetry install -vv
poetry run python -m ipykernel install --user --name=musii-kit-0.1.0
