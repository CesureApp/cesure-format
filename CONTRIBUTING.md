# Contributing

`.cesure` is the native format of [Cesure](https://cesure.app). This repository is the **public,
authoritative specification** — the human-readable spec ([`README.md`](README.md)), the machine
schema ([`schema/v1.json`](schema/v1.json)), a [changelog](CHANGELOG.md) and runnable
[examples](examples/).

## Proposing a change

The format is designed and validated inside the Cesure application, so the safest path is to
**open an issue** describing what you need (a new field, a clarification, a bug in the schema or an
example). Pull requests that fix typos, improve wording, tighten the schema, or add examples are
welcome.

Any change must keep the promise that makes the format worth using: **a file saved once must open
identically forever.** See the *Versioning policy* and *Maintenance* sections of the
[README](README.md).

## Validating locally

Validate the schema and every example yourself:

```sh
pip install jsonschema
python3 scripts/validate.py
```

It confirms that `schema/v1.json` is a valid JSON Schema (Draft 2020-12) and that every file in
`examples/` conforms to it.
