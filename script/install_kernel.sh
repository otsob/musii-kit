#!/bin/sh
poetry install -vv --no-interaction --no-cache --without dev
python -m ipykernel install --user --name=musii-kit-0.1
