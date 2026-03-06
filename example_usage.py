#!/usr/bin/env python3
"""Example usage of llm-model-deprecation."""

from llm_deprecation import DeprecationChecker, DeprecationStatus

def main():
    checker = DeprecationChecker()

    print("=== Check specific models ===\n")
    for model in ["gpt-3.5-turbo-0301", "gpt-4", "claude-2.0", "text-embedding-ada-002"]:
        info = checker.get(model)
        status = checker.status(model)
        deprecated = checker.is_deprecated(model)
        print(f"  {model}")
        print(f"    status={status.value}, deprecated={deprecated}")
        if info and info.replacement:
            print(f"    replacement: {info.replacement}")
        print()

    print("=== All deprecated/retired (OpenAI) ===\n")
    for m in checker.list_deprecated(provider="openai"):
        print(f"  {m.model_id} -> {m.status.value} (use {m.replacement or 'N/A'})")

    print("\n=== Register custom entry ===\n")
    from datetime import date
    from llm_deprecation.models import ModelInfo

    checker.register(ModelInfo(
        provider="openai",
        model_id="gpt-4-custom-deprecated",
        status=DeprecationStatus.DEPRECATED,
        sunset_date=date(2026, 6, 1),
        replacement="gpt-4o",
    ))
    print("  gpt-4-custom-deprecated:", checker.status("gpt-4-custom-deprecated").value)


if __name__ == "__main__":
    main()
