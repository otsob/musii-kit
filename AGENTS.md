# Agents

## Structure

### `musii_kit`

- `musii_kit/point_set/`: Point-set representation for Music Information Retrieval.
- `musii_kit/point_set/visualization.py`: Point-set visualization.
- `musii_kit/pattern_data/`: pattern sets, evaluators, MIREX metrics
- `musii_kit/pattern_discovery/`: pattern discovery algorithms
- `musii_kit/pattern_search/`: pattern matching algorithms
- `musii_kit/display.py`: visualization helpers

### `examples`

- `examples/notebook`: Jupyter notebook examples how to use `musii-kit`.
- `examples/data`: example data for use in notebook examples.

## Commands

- Lint: `poetry run ruff check`
- Tests: `poetry run pytest`
- By default, run both lint and tests when checking code.
- Install Jupyter kernel: `poetry run ./script/install_kernel.sh`

## Build and CI

- CI runs: lint -> test -> (on main: build Docker image)
- Docker image is only built on push to `main`, not on PRs. Image tag matches major.minor version (e.g., `:0.6`).
- Version bumping is automated on main after the image is pushed (via bump2version).

## Ruff excludes `posemirpy`

The `posemirpy` git submodule dependency (from https://github.com/otsob/posemir) is excluded from linting in
`ruff.toml`. Do not add ruff rules that affect it.

## Version management

- `bump2version` updates version numbers in all needed places.
- `bump2version` configured in `.bumpversion.cfg`.

## Code style

- Line length: 120
- Indent: 4 spaces
- Quotes: single
- Target Python: 3.12
