# Musii-kit: Tools for interactive computational music analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![pull_request](https://github.com/otsob/musii-kit/actions/workflows/pull_request.yml/badge.svg)

A collection of tools for computational musicology, especially using Jupyter Notebooks for music analysis. This has been
greatly inspired by the example notebooks associated with the excellent book
[Fundamentals of Music Processing](https://www.audiolabs-erlangen.de/fau/professor/mueller/bookFMP).

## Dependencies

* Python 3.8
* Jupyter Notebook
* Poetry
* MuseScore (version 3.6 recommended) or Lilypond for visualizing scores
* [Bump2version](https://pypi.org/project/bump2version/) for version bumping

The exact packages used by musii-kit are defined in the [poetry.lock](./poetry.lock) file.

## Installation

1. Activate virtual environment by running `poetry shell` at the root of this repository.
2. Run `./script/install_kernel.sh`

Once all dependencies are installed in the virtual environment, run
`./script/update_kernel.sh` instead to avoid running full install of all dependencies.
