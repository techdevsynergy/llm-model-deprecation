# llm-model-deprecation

A small Python library to **track and check deprecation status** of LLM provider models (OpenAI, Anthropic, etc.). Use it to warn when your app uses deprecated or retired models and to get replacement suggestions.

## Install

```bash
cd /path/to/llm-model-deprecation
pip install -e .
```

Optional: support for loading from URLs via `requests` (stdlib `urllib` works without it):

```bash
pip install -e ".[fetch]"
```

## Quick usage

The library loads data from **DEFAULT_DATA_URL** ([techdevsynergy/llm-deprecation-data](https://github.com/techdevsynergy/llm-deprecation-data)); if that fails (e.g. offline), it falls back to the built-in registry in `data.py`. No config needed.

```python
from llm_deprecation import DeprecationChecker, DeprecationStatus

checker = DeprecationChecker()  # DEFAULT_DATA_URL, then data.py fallback

# Check by model id (searches all providers)
checker.is_deprecated("gpt-3.5-turbo-0301")   # True
checker.is_retired("gpt-3.5-turbo-0301")     # True
checker.status("gpt-4")                       # DeprecationStatus.ACTIVE

# With provider for exact match
checker.get("claude-2.0", provider="anthropic")
# -> ModelInfo(provider='anthropic', model_id='claude-2.0', status=LEGACY, replacement='claude-3-sonnet or claude-3-opus', ...)

# List deprecated models
for m in checker.list_deprecated(provider="openai"):
    print(m.model_id, m.status.value, m.replacement)
```

## Status values

- **active** — Currently supported, no deprecation.
- **legacy** — Still supported; prefer newer models.
- **deprecated** — Will be retired; migrate before sunset date.
- **retired** — No longer available.

## Data source

Data is loaded in two steps only:

1. **DEFAULT_DATA_URL** — [techdevsynergy/llm-deprecation-data](https://github.com/techdevsynergy/llm-deprecation-data) (`llm_deprecation_data.json` on `main`). Tried first.
2. **Built-in** — `data.py` in the library. Used when the URL is unreachable (e.g. offline).

To export the built-in registry to JSON (e.g. for reference):

```python
from llm_deprecation.loader import export_builtin_to_json
export_builtin_to_json("config/llm-models.json")
```

**JSON schema** (each entry in the root array or under `"models"` / `"deprecations"`):

| Field            | Required | Description |
|-----------------|----------|-------------|
| `provider`      | yes      | e.g. `openai`, `anthropic`, `gemini` |
| `model_id`      | yes      | API model identifier |
| `status`        | yes      | `active`, `legacy`, `deprecated`, `retired` |
| `deprecated_date` | no    | ISO date when deprecated |
| `sunset_date`   | no       | ISO date when retired/unavailable |
| `replacement`   | no       | Suggested replacement model |
| `notes`         | no       | Free text |

See `config/llm-deprecation-models.json.example` for a minimal example.

## Extending the registry in code

You can still add or override entries programmatically:

```python
from datetime import date
from llm_deprecation import DeprecationChecker
from llm_deprecation.models import ModelInfo, DeprecationStatus

checker = DeprecationChecker()
checker.register(ModelInfo(
    provider="openai",
    model_id="gpt-4-old",
    status=DeprecationStatus.DEPRECATED,
    sunset_date=date(2026, 1, 1),
    replacement="gpt-4o",
))
```

## Testing

Run the example (loads from DEFAULT_DATA_URL, then checks a few models):

```bash
cd /path/to/llm-model-deprecation
pip install -e .
python example_usage.py
```

Run the test suite:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Tests cover: loading the registry (URL or built-in fallback), `is_deprecated` / `status`, `list_deprecated`, and `register()` overrides.

## Provider deprecation docs

For official, up-to-date lists, see:

- [OpenAI API deprecations](https://developers.openai.com/api/docs/deprecations)
- [Anthropic model deprecations](https://docs.anthropic.com/en/docs/resources/model-deprecations)
- [deprecations.info](https://deprecations.info/) — aggregated feeds (JSON/RSS)

## Publishing to PyPI

The package is **not on PyPI until you run the build and upload from your own machine** (or CI) where PyPI is reachable. The steps below must be run locally.

**1. Create a PyPI account and API token**

- Register at [pypi.org](https://pypi.org/account/register/) (and optionally [test.pypi.org](https://test.pypi.org/account/register/) for testing).
- Under your account, go to **Account settings → API tokens** and create a token (e.g. scope: entire account or just this project).

**2. Install build tools**

```bash
pip install build twine
```

**3. Build the package**

```bash
cd /path/to/llm-model-deprecation
python -m build
```

This creates `dist/llm-model-deprecation-0.1.0.tar.gz` and `dist/llm_model_deprecation-0.1.0-py3-none-any.whl`.

**4. Upload to PyPI**

```bash
twine upload dist/*
```

When prompted, use `__token__` as the username and your API token as the password. Or set env vars and use the script (recommended — uses a dedicated venv so system packages like urllib3 are untouched):

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YourApiTokenHere
bash scripts/publish.sh
```

The script creates `.venv-deploy/`, installs `build` and `twine` there, then runs build and upload. No need to change your global Python packages. Or run manually: `python3 -m build` then `twine upload dist/*`.

**5. Test first (optional)**

To try the release on Test PyPI before production:

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ llm-model-deprecation
```

**6. For future releases**

Bump `version` in `pyproject.toml`, then run `python -m build` and `twine upload dist/*` again. Do not re-upload the same version to PyPI.

## License

MIT.
