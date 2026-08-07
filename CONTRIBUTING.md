# Contributing

`.cesure` is the native format of [Cesure](https://cesure.app). This repository is the **public,
authoritative specification** — the human-readable spec ([`README.md`](README.md)), the machine
schema ([`schema/v1.json`](schema/v1.json)), a [changelog](CHANGELOG.md) and runnable
[examples](examples/).

## This repository is a mirror — please open an issue, not a pull request

The specification lives inside the Cesure codebase, where it is tested against the application on
every build. **This repository is a read-only mirror of it**, republished whenever the spec changes.

That has one consequence worth stating plainly, because it would otherwise waste your time: a pull
request merged here would have its changes **overwritten at the next sync**. The commit would stay
in the history, but the file would revert. So we don't accept pull requests — not because
contributions aren't welcome, but because we can't honour them.

**Open an [issue](https://github.com/CesureApp/cesure-format/issues) instead.** Anything is useful:
a field you need, wording that reads ambiguously, a schema that rejects a file it should accept, a
missing example. Issues are read, and what comes out of them is applied upstream and lands here on
the next publication — with credit in the [changelog](CHANGELOG.md).

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
