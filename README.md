# MusiiKit: Musicology data analysis toolkit

A collection of tools for computational musicology.

## Dependencies
* Python 3.8
* Jupyter Notebook
* Pipenv
* MuseScore (version 3.6 recommended)

The exact packages used by MusiiKit are defined in the [Pipfile.lock](./Pipfile.lock).

## Installation
1. Activate virtual environment by running `pipenv shell` at the root of this repository.
2. Run `./script/install_kernel.sh`

Once all dependencies are installed in the virtual environment, run
`./script/update_kernel.sh` instead to avoid running pipenv install.