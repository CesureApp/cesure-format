# .cesure format

Open specification for `.cesure` — the native tablature format of [Cesure](https://cesure.app).

## What it is

`.cesure` is a UTF-8 JSON file for guitar tablature. It is:

- **Lossless** — a score saved as `.cesure` re-opens identically, every time
- **Human-readable** — plain JSON, no binary encoding, no compression
- **Versioned** — an explicit `version` field with a defined migration policy
- **Simple** — no external tooling, any JSON parser is enough to read it

## Why not MusicXML, MIDI, or AlphaTex?

| Format | Human-readable | Guitar-specific | Round-trip lossless | Versioned |
|---|---|---|---|---|
| `.cesure` | ✓ | ✓ | ✓ | ✓ |
| MusicXML | ✓ | ✗ | ~ | ✗ |
| AlphaTex | ✓ | ✓ | ~ | ✗ |
| MIDI | ✗ | ✗ | ✗ | ✗ |
| GP5 | ✗ | ✓ | ~ | ✗ |

## File structure

```
score.cesure
└── (UTF-8 JSON)
    ├── version   integer
    └── score     Score
```

### Root

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | `integer` | ✓ | Format version. Current: `1`. |
| `score` | [`Score`](#score) | ✓ | The musical score. |

---

### Score

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `"Untitled"` | Song title. |
| `artist` | `string` | `""` | Artist name. |
| `album` | `string` | `""` | Album name. |
| `tempo` | `integer` | `120` | Initial tempo in BPM — in force until the first `tempoChanges` entry. |
| `tracks` | [`Track[]`](#track) | `[]` | Instrument tracks. |
| `tempoChanges` | [`TempoChange[]`](#tempochange) | `[]` | Mid-song tempo changes. Empty = constant tempo. |
| `license` | `string` | `""` | License of the published work (e.g. `Public Domain`, `CC BY 4.0`). Empty = the file says nothing — the case of every user-authored score. |
| `attribution` | `string` | `""` | Attribution of the edition — year and source URL included when applicable. It travels **with the file** because CC-BY legally requires it when a copy is kept. Empty = nothing to attribute. |

---

### TempoChange

A tempo change taking effect at the **start** of a measure and holding until the next one.

| Field | Type | Required | Description |
|---|---|---|---|
| `measureIndex` | `integer` | ✓ | 0-indexed measure at which the new tempo starts. |
| `tempo` | `integer` | ✓ | Tempo in BPM from that measure on. |

Tempo belongs to the **score**, not to a track: every track shares it, which is also how MIDI
models it (a single tempo track). The granularity is the measure — that of a tempo mark in
notation. A reader resolves the tempo at measure *m* as the last change whose `measureIndex` is
≤ *m*, falling back to `tempo`. The list needs no particular order; entries with a `measureIndex`
past the end of the score, or a non-positive `tempo`, are ignored.

---

### Track

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | `"Guitar"` | Track / instrument name. |
| `tuning` | [`Note[]`](#note) | standard tuning | String tuning, from string 1 (highest) to string N (lowest). Standard 6-string: `[E4, B3, G3, D3, A2, E2]`. |
| `measures` | [`Measure[]`](#measure) | `[]` | Ordered list of measures. |
| `capo` | `integer` | `0` | Capo position in frets (0 = none). Tab numbers stay relative to the capo; only the sounding pitch shifts up. |
| `volume` | `number` | `1` | Track volume in the mix, `0`..`1`. Arrangement data, like `capo`: imported, saved, exported. |
| `instrument` | `string` \| `null` | `null` | Timbre: `GUITAR`, `BASS` or `PIANO`. Deliberately narrow — it lists only what a player can actually render. Absent is **not** "guitar": it means the file says nothing, and a player falls back to its own sound preference. |

---

### Measure

| Field | Type | Default | Description |
|---|---|---|---|
| `beats` | [`Beat[]`](#beat) | `[]` | Ordered list of beats (notes and rests). |
| `numerator` | `integer` | `4` | Time signature numerator. |
| `denominator` | `integer` | `4` | Time signature denominator. |

---

### Beat

| Field | Type | Default | Description |
|---|---|---|---|
| `duration` | [`Duration`](#duration) | — | Note value. Required. |
| `notes` | [`TabNote[]`](#tabnote) | `[]` | Notes played simultaneously. Empty = rest. |
| `isDotted` | `boolean` | `false` | If `true`, duration × 1.5. |

---

### TabNote

| Field | Type | Default | Description |
|---|---|---|---|
| `string` | `integer` | — | 1-indexed string number. `1` = highest/thinnest (high E on standard tuning). |
| `fret` | `integer` | — | Fret number. `0` = open string. `-1` = muted / dead note. |
| `techniques` | [`TabTechnique[]`](#tabtechnique) | `[]` | Playing techniques attached to the note (unique set). |
| `bendSemitones` | `integer` | `2` | Bend amplitude in semitones; meaningful only when `techniques` include `BEND`. |
| `voice` | [`TabVoice`](#tabvoice) \| `null` | `null` | Voice explicitly assigned to the note. Absent or `null` = automatic: the voice is derived from the register (see below). |

---

### TabVoice

Serialised as a string, or `null`. Two voices played at once — left/right hand on a piano part, or
the two parts of a duet.

| Value | Meaning |
|---|---|
| `"A"` | Lower voice. |
| `"B"` | Upper voice. |
| `null` (or absent) | Automatic — the voice is **derived**, not stored: a note whose sounding pitch is below the reader's split point is voice A, otherwise voice B. Cesure uses middle C (C4) as the default split point, and the split point itself is a reader preference, **not** part of the file. |

An explicit value always wins over the automatic rule: moving the split point never erases a
manual assignment.

---

### TabTechnique

Serialised as a string. One of:

| Value | Meaning |
|---|---|
| `"HAMMER_PULL"` | Hammer-on / pull-off — a **transition** to the next note on the same string (direction read from the fret difference). |
| `"SLIDE"` | Slide — a transition to the next note on the same string. |
| `"BEND"` | Bend (amplitude in `bendSemitones`). |
| `"VIBRATO"` | Vibrato. |
| `"TAPPING"` | Tapping. |

---

### Duration

Serialised as a string. One of:

| Value | Note value | Quarter-note count |
|---|---|---|
| `"WHOLE"` | Whole note | 4.0 |
| `"HALF"` | Half note | 2.0 |
| `"QUARTER"` | Quarter note | 1.0 |
| `"EIGHTH"` | Eighth note | 0.5 |
| `"SIXTEENTH"` | Sixteenth note | 0.25 |
| `"THIRTY_SECOND"` | 32nd note | 0.125 |

When `isDotted` is `true`, multiply the quarter-note count by 1.5.

---

### Note

Represents an absolute pitch (used in `Track.tuning`).

| Field | Type | Description |
|---|---|---|
| `note` | `string` | Pitch class. One of: `"C"`, `"Cs"`, `"D"`, `"Ds"`, `"E"`, `"F"`, `"Fs"`, `"G"`, `"Gs"`, `"A"`, `"As"`, `"B"`. (`s` = sharp) |
| `octave` | `integer` | Octave number (scientific pitch notation). Middle C = `{"note":"C","octave":4}`. |

#### Standard 6-string guitar tuning

```json
[
  {"note": "E", "octave": 4},
  {"note": "B", "octave": 3},
  {"note": "G", "octave": 3},
  {"note": "D", "octave": 3},
  {"note": "A", "octave": 2},
  {"note": "E", "octave": 2}
]
```

---

## Versioning policy

The root `version` field controls compatibility.

| Change type | Action |
|---|---|
| Add a field with a default value | No version bump — backward compatible |
| Remove a field | Bump `version`, add a migration |
| Rename a field | Bump `version`, add a migration |
| Change a field type | Bump `version`, add a migration |

Parsers **must** reject files with an unknown `version` value rather than silently misreading them.

Current version: **1**.

---

## JSON Schema

A machine-readable schema is available at [`schema/v1.json`](schema/v1.json) (JSON Schema Draft
2020-12). Validate the schema and every example in [`examples/`](examples/) with:

```sh
pip install jsonschema
python3 scripts/validate.py
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) to propose a change.

---

## Examples

- [`examples/simple.cesure`](examples/simple.cesure) — single track, one measure
- [`examples/song.cesure`](examples/song.cesure) — multi-measure song with chords and rests

---

## Maintenance

The format is developed and regression-tested inside the Cesure application; this section documents
**how it stays stable** (the tooling below lives in the app repository, not here).

**A `.cesure` file that a user saved must open identically forever.** Any change to the model
(`Score` / `Track` / `Measure` / `Beat` / `TabNote` / `Duration` / `Note`) goes through this
procedure — a lost tab does not come back.

**Before changing the model:**

1. **Additive field** (new field *with a default*) → backward-compatible, **no version bump**.
   Still required: update this README table, `schema/v1.json`, `CHANGELOG.md`, and add the field to
   the frozen corpus so it is actually exercised (`CesureSerializerTest.frozenV1CorpusDeserializesToExactScore`).
2. **Remove / rename / retype a field** → **bump `CURRENT_VERSION`** in `CesureSerializer` **and add
   a migration case** that reads old files correctly (via the raw `JsonObject` for renames). Keep a
   frozen file of the *old* version — it must still load (migrated), forever.
3. **Never edit the frozen corpus JSON to make a test pass.** If `frozenV1CorpusDeserializesToExactScore`
   breaks, it means an old file no longer reads the same → that is the bug, fix it with a migration.
4. **Run the guards** every time: `./gradlew :composeApp:testDebugUnitTest --tests "*CesureSerializerTest*"`
   — round-trip (synthetic + real Guitar Pro fixtures + example files), legacy-without-field, frozen
   v1 corpus, unsupported-future-version, unknown-fields-ignored.

The drift this guards against is real: `capo`, `techniques` and `bendSemitones` were once added to
the model without updating this spec/schema (fixed 2026-07-25) — the schema even had
`additionalProperties: false`, so it would have *rejected* real files.

## The application behind the format

`.cesure` is written and read by **[Cesure](https://cesure.app)** — a guitar tablature editor and
practice toolkit that runs [in the browser](https://cesure.app), on Android and on iOS. It imports
Guitar Pro, MusicXML, MIDI and AlphaTex, transcribes audio to tablature, and plays scores back with
a tuner, a metronome and a piano roll.

That matters for this specification, and not as an advertisement: the format is exercised by the
application's test suite on every build — round-trip, migration, and a frozen corpus of real files.
A spec nobody runs drifts from the files it claims to describe. This one can't.

## License

This specification is released under the [MIT License](LICENSE).
