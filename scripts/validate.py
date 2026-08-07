#!/usr/bin/env python3
"""Validate the .cesure JSON Schema and every bundled example against it.

Usage:
    python3 scripts/validate.py

Exit code 0 if the schema is a valid JSON Schema and all examples conform, 1 otherwise.
Requires: jsonschema  (pip install jsonschema)
"""
import glob
import json
import os
import sys

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Missing dependency: jsonschema. Install it with `pip install jsonschema`.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, "schema", "v1.json")
EXAMPLES_GLOB = os.path.join(ROOT, "examples", "*.cesure")


def main() -> int:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    # 1. The schema must itself be a valid Draft 2020-12 schema.
    Draft202012Validator.check_schema(schema)
    print(f"OK  schema/{os.path.basename(SCHEMA_PATH)} is a valid Draft 2020-12 schema")

    # 2. Every example must conform to the schema.
    validator = Draft202012Validator(schema)
    examples = sorted(glob.glob(EXAMPLES_GLOB))
    if not examples:
        print("No examples found — nothing to validate", file=sys.stderr)
        return 1

    failures = 0
    for path in examples:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
        if errors:
            failures += 1
            print(f"FAIL {rel}")
            for err in errors:
                where = "/".join(str(p) for p in err.path) or "(root)"
                print(f"     - {where}: {err.message}")
        else:
            print(f"OK  {rel}")

    if failures:
        print(f"\n{failures} example(s) failed validation", file=sys.stderr)
        return 1
    print(f"\nAll {len(examples)} example(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
