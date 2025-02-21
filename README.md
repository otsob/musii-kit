# Musii-kit: Tools for interactive computational music analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![pull_request](https://github.com/otsob/musii-kit/actions/workflows/main.yaml/badge.svg)

A collection of tools for computational musicology, especially using Jupyter Notebooks for music analysis. This has been
greatly inspired by the example notebooks associated with the excellent book
[Fundamentals of Music Processing](https://www.audiolabs-erlangen.de/fau/professor/mueller/bookFMP).

## Dependencies

* Python (tested with 3.11)
* Jupyter
* Poetry
* Rust (for `posemirpy`)
* [Bump2version](https://pypi.org/project/bump2version/) for version bumping

## Installation

Run `poetry run ./install_kernel.sh` to install the musii-kit jupyter kernel.

## Running in a Docker container

Musii-kit can also be run in a Docker container. The Docker images for musii-kit can be found
on [GitHub container registry](https://github.com/otsob/musii-kit/pkgs/container/musii-kit),
e.g. `ghcr.io/otsob/musii-kit:0.1`
for version `0.1.x``