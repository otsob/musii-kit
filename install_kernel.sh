#!/bin/sh
poetry install -vv --no-interaction --without dev $1
python -m ipykernel install --user --name=musii-kit-0.5
