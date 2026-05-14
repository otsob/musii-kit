# musii-kit developer notes

## Commands

- Lint: `poetry run ruff check --verbose`
- Tests: `poetry run pytest --verbose`
- Install Jupyter kernel: `poetry run ./install_kernel.sh` (registers a kernel named `musii-kit-X.Y`)

## Build and CI

- CI runs: lint -> test -> (on main: build Docker image)
- Docker image is only built on push to `main`, not on PRs. Image tag matches major.minor version (e.g., `:0.6`).
- Version bumping is automated on main after the image is pushed (via bump2version).

## Ruff excludes `posemirpy`

The `posemirpy` git submodule dependency (from https://github.com/otsob/posemir) is excluded from linting in `ruff.toml`. Do not add ruff rules that affect it.

## Version management

`bump2version` updates: `pyproject.toml`, `script/install_kernel.sh`, `.github/workflows/main.yaml`, and two example notebooks (`examples/notebook/*.ipynb`). Only bump one component at a time (patch/minor/major).

## Code style

- Line length: 120
- Indent: 4 spaces
- Quotes: single
- Target Python: 3.11

## Key packages

- `musii_kit/point_set/` - 2D pattern set data structures
- `musii_kit/pattern_data/` - pattern sets, evaluators, MIREX metrics
- `musii_kit/pattern_discovery/` - discovery algorithms
- `musii_kit/pattern_search/` - matching algorithms
- `musii_kit/display.py` - visualization helpers
- `musii_kit/point_set/visualization.py` - 2D plotting