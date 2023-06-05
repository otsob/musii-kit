# Musii-kit: Tools for interactive computational music analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![pull_request](https://github.com/otsob/musii-kit/actions/workflows/main.yaml/badge.svg)

A collection of tools for computational musicology, especially using Jupyter Notebooks for music analysis. This has been
greatly inspired by the example notebooks associated with the excellent book
[Fundamentals of Music Processing](https://www.audiolabs-erlangen.de/fau/professor/mueller/bookFMP).

## Dependencies

* Python 3.10
* Jupyter Notebook
* Poetry
* MuseScore (version 3.6 recommended) or Lilypond for visualizing scores
* Rust (for `posemirpy`)
* [Bump2version](https://pypi.org/project/bump2version/) for version bumping

The exact packages used by musii-kit are defined in the [poetry.lock](./poetry.lock) file.

## Installation

1. Activate virtual environment by running `poetry shell` at the root of this repository.
2. Run `./install_kernel.sh`

## Running in a Docker container

Musii-kit can also be run in a Docker container. The Docker images for musii-kit can be found
on [GitHub container registry](https://github.com/otsob/musii-kit/pkgs/container/musii-kit),
e.g. `ghcr.io/otsob/musii-kit:0.1`
for version `0.1.x``