# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.1] - 2025-03-09

### Added

- **GitHub Action** — adding retire date and deprecated date if available to the ouput

## [1.2.0] - 2025-03-09

### Added

- **GitHub Action** — `report` output: scan output (findings text) is now exposed as `steps.<id>.outputs.report` for use in Slack, job summary, or logs.

## [1.1.0] - 2025-03-07

### Added

- **CLI** — `llm-deprecation scan` to scan a project for deprecated/retired LLM model references. Use in CI, cron, or locally.
  - `llm-deprecation scan [path]` — scan current dir or given path
  - `--fail-on-deprecated` — exit with code 1 when findings exist (for CI)
  - `-q` / `--quiet` — suppress "Scanning project..." line
- **GitHub Action** — `.github/actions/llm-model-deprecation-action` to run the same check in GitHub Actions. Options: `path`, `fail-on-deprecated`, `version`.
- Scanner module (`llm_deprecation.scanner`) to search code and config files for known deprecated model IDs.

## [1.0.0] - (initial)

### Added

- Library: `DeprecationChecker`, `DeprecationStatus`, `ModelInfo` for checking LLM model deprecation status.
- Load registry from default URL with built-in fallback.
- Optional `[fetch]` extra for URL loading via `requests`.

[Unreleased]: https://github.com/techdevsynergy/llm-model-deprecation/compare/v1.2.0...HEAD
[1.2.1]: https://github.com/techdevsynergy/llm-model-deprecation/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/techdevsynergy/llm-model-deprecation/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/techdevsynergy/llm-model-deprecation/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/techdevsynergy/llm-model-deprecation/releases/tag/v1.0.0
