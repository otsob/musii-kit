# MusiiKit: Musicology data analysis toolkit

A collection of tools for computational musicology.

## Dependencies

* Python 3.8
* Jupyter Notebook
* Poetry
* MuseScore (version 3.6 recommended)

The exact packages used by MusiiKit are defined in the [poetry.lock](./poetry.lock) file.

## Installation

1. Activate virtual environment by running `poetry shell` at the root of this repository.
2. Run `./script/install_kernel.sh`

Once all dependencies are installed in the virtual environment, run
`./script/update_kernel.sh` instead to avoid running full install of all dependencies.