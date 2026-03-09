# llm-model-deprecation

Track and check deprecation status of LLM provider models (OpenAI, Anthropic, Gemini, etc.). Use it to warn when your app uses deprecated or retired models and to get replacement suggestions.

## Install

```bash
pip install llm-model-deprecation
```

Optional: URL loading via `requests` (otherwise stdlib `urllib` is used):

```bash
pip install "llm-model-deprecation[fetch]"
```

## Library usage

Data is loaded from the default registry (online with built-in fallback). No config needed.

```python
from llm_deprecation import DeprecationChecker, DeprecationStatus

checker = DeprecationChecker()

# Check by model id (searches all providers)
checker.is_deprecated("gpt-3.5-turbo-0301")   # True
checker.is_retired("gpt-3.5-turbo-0301")     # True
checker.status("gpt-4")                       # DeprecationStatus.ACTIVE

# With provider for exact match
checker.get("claude-2.0", provider="anthropic")
# -> ModelInfo(provider='anthropic', model_id='claude-2.0', status=..., replacement='...', ...)

# List deprecated models
for m in checker.list_deprecated(provider="openai"):
    print(m.model_id, m.status.value, m.replacement)
```

## Status values

- **active** — Currently supported, no deprecation.
- **legacy** — Still supported; prefer newer models.
- **deprecated** — Will be retired; migrate before sunset date.
- **retired** — No longer available.

## Add or override models in code

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

## CLI

Scan a project for deprecated or retired model references (CI, cron, or local):

```bash
llm-deprecation scan
llm-deprecation scan /path/to/project
llm-deprecation scan --fail-on-deprecated   # exit 1 if any found (for CI)
```

Example output:

```
Scanning project...
⚠ openai:gpt-3.5-turbo → deprecated soon
⚠ anthropic:claude-instant → retired
```

The scanner looks in common code and config files (`.py`, `.json`, `.yaml`, `.env`, `.ts`, etc.).

## GitHub Action

Run the same check in GitHub Actions:

```yaml
- name: Check LLM deprecations
  id: llm-check
  uses: techdevsynergy/llm-model-deprecation@v1.2.1
  with:
    fail-on-deprecated: true
```

**Inputs:** `path` (project root to scan, default `"."`), `fail-on-deprecated` (default `false`), `version` (pin package version).

**Outputs:** `report` — the scan output (findings text). Use it for Slack, job summary, or logs:

```yaml
- name: Check LLM deprecations
  id: llm-check
  uses: techdevsynergy/llm-model-deprecation@v1.2.1
  with:
    fail-on-deprecated: false

- name: Send to Slack
  if: steps.llm-check.outputs.report != ''
  run: |
    # For production, escape the report for JSON (e.g. with jq --arg) or use slackapi/slack-github-action
    curl -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"${{ steps.llm-check.outputs.report }}\"}" \
      "${{ secrets.SLACK_WEBHOOK_URL }}"
```

## Data source

Registry is loaded from the default URL ([llm-deprecation-data](https://github.com/techdevsynergy/llm-deprecation-data)); if unreachable (e.g. offline), the built-in registry in the library is used.

## Links

- [OpenAI API deprecations](https://developers.openai.com/api/docs/deprecations)
- [Anthropic model deprecations](https://docs.anthropic.com/en/docs/resources/model-deprecations)
- [deprecations.info](https://deprecations.info/)

## License

MIT
