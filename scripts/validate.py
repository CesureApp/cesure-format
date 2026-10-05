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
# Each version's examples against that version's schema: the current ones in examples/, the
# frozen ones of an older version in examples/vN/.
SUITES = [
    ("v2.json", os.path.join(ROOT, "examples", "*.cesure")),
    ("v1.json", os.path.join(ROOT, "examples", "v1", "*.cesure")),
]


def validate(schema_name: str, examples_glob: str) -> int:
    with open(os.path.join(ROOT, "schema", schema_name), encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    print(f"OK  schema/{schema_name} is a valid Draft 2020-12 schema")
    validator = Draft202012Validator(schema)
    examples = sorted(glob.glob(examples_glob))
    if not examples:
        print(f"No examples for schema/{schema_name} — nothing to validate", file=sys.stderr)
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
    return failures


def main() -> int:
    failures = sum(validate(schema, examples) for schema, examples in SUITES)
    if failures:
        print(f"\n{failures} failure(s)", file=sys.stderr)
        return 1
    print("\nAll examples valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
