#!/bin/sh

cd posemirpy
poetry install -vv --no-interaction --with dev $1
maturin develop -r
cd ..

poetry install -vv --no-interaction --without dev $1
python -m ipykernel install --user --name=musii-kit-0.4
