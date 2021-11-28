#!/bin/sh
pipenv install -vv
pyb -vv && pip install -e target/dist/musii_kit-*
python -m ipykernel install --user --name=musii-kit