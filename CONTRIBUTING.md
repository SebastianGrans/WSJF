# Contribution instructions and guidelines

## Development installation

For ease of development, install it as editable:

```bash
uv pip install -e . --group dev
```

or with `pip` (requires [`pip>=25.1`](https://pip.pypa.io/en/stable/news/#v25-1)):

```bash
pip install -e . --group dev
```

This installs additional type checking and linting tools (`ruff` and `pyright`)

## Code standards

Before making a PR, run `ruff` and `pyright` and make sure they pass.

```bash
uv run ruff check src/ tests/ examples/
```

```bash
uv run pyright src/ tests/ examples/
```
