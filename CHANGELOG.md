# Changelog

Additive fields (a new field with a default) are **backward-compatible** and do **not** bump the
version — old files still load, new files still open in older builds (unknown keys are ignored).
They are listed under v1 with the date they were added.

## v2

Written by Cesure from 2026-10 on; every reader keeps reading v1 ([v1.md](v1.md)).

- **The notes move into a compact notation**: each voice of each measure is one string
  (`"5.3.4 (0.1 2.2).8 r.2"`) instead of an array of objects — about four times fewer tokens for an
  agent. The notation is modelled on alphaTab's AlphaTex but defined and frozen in this
  specification. Every measure states its own durations.
- **Structure for what comes later**: a measure holds staves, a staff holds voices — Cesure writes
  one staff and at most two voices. Beat properties `lyrics` and `ch` (chord symbol) and notes
  written as a pitch are reserved forms. A reader keeps what it does not represent, in the skeleton
  as in the notation, and writes it back.
- **Harmonics** are note properties: `nh`, `ah n`, `th n`, `ph n`, `sh n`, `fh n`.
- **Ghost notes** are the note property `g`, alphaTab's (added 2026-10-04, no new version: a v2
  reader that does not know it keeps it on its note and writes it back).
- **A note may be written by its pitch** (`E4`, `(0.1 C4).2`), the reserved form put to use: the
  reader places it on the track's tuning and capo, by Cesure's rules, the whole track around it;
  a note written as `fret.string` never moves, and a writer writes the string and fret chosen.
  What it cannot place is refused by name (added 2026-10-05, no new version).
- **Drum notes** are a reserved form: `p` and the General MIDI key of the piece struck, from `p0`
  to `p127` — `p42.8`, `(p36 p42).8` (added 2026-10-05, no new version: a v2 reader that does not
  know it keeps it on its beat and writes it back; a key past 127 is an error).
- **A note written as a pitch takes two accidentals**: `##` or `x`, `bb` (`C##4`, `Dx5`, `Ebb4`),
  as alphaTab writes them, and the grammar of a pitch is written down; a pitch is the sounding one
  (added 2026-10-05, no new version).
- **The tempo is a number**, of the score as of each tempo change: `92.5` is kept, played and
  written back as it is, and a whole tempo is still written as an integer (added 2026-10-05, no new
  version: every file read before reads the same; a reader that takes the tempo as an integer
  refuses a file whose tempo is not whole, and Cesure writes one only when it read one).
- **Double-dotted beats** are the beat property `dd`, alphaTab's: the value × 1.75 (added
  2026-10-05, no new version: a v2 reader that does not know it keeps it on its beat and writes it
  back). A beat carries `d` or `dd`, never both; a reader that finds both reads two dots.
- **The numerator stops at 128** (`maximum` in the schema, added 2026-10-05, no new version): no
  metre counts more beats, and a reader builds a measure beat by beat, so an unbounded numerator
  was the size of an allocation a file chose. Cesure reads a value outside 1 to 128 as 4, as it
  reads a denominator outside its list.
- **A document nests at most 64 levels** (added 2026-10-05, no new version): Cesure refuses a file
  whose JSON nests deeper as damaged, before reading it; no file it writes goes past a dozen.
- **Repeats** (`Score.repeats`, by measure id: start, close ×n, alternative endings) and a **second
  voice** per staff, new in the model.
- **Durations go down to the sixty-fourth** (`64`); v1 stops at the thirty-second.
- **Tempo changes are named by measure id** (`measure`) instead of a measure index, so that they
  stay on their measure when measures are inserted or deleted.
- The note's hand (the A/B "voices" of a piano part in v1, `TabNote.voice`) is the note property
  `hand`.
- The schema's `$id` is `https://cesure.app/format/schema/v2.json`, where it is served.

## v1

### Reader contract

- **An unknown enum value costs only its field** — added 2026-09-24. A reader used to fail on the
  whole file as soon as one enum value was unknown to it, so any value added to the format made
  every file the newer build wrote unreadable to the older ones — the same account on two devices.
  On an **optional** field (`Track.instrument`, `TabNote.voice`, an element of `TabNote.techniques`)
  the reader now drops the value from its model, keeps it verbatim and writes it back — unless the
  user sets that field, whose choice then replaces the kept value (a voice toggled or reset). On a
  **required** one (`Beat.duration`, `Note.note`) it refuses the file by naming the field and the
  value, as it refuses an unknown `version`: guessing would change the rhythm or the tuning. Growing
  `Duration` or the pitch classes of `Note` therefore bumps the version; the other enums may grow
  within v1. See *Versioning policy → Unknown enum values*.

- **Unknown fields are preserved, not dropped** — added 2026-08-18. A reader must keep the keys it
  does not recognise and write them back unchanged at the level it read them. Ignoring them on read
  was already required; forgetting them turned every save into silent data loss, which cost the
  `license` / `attribution` credit of catalog pieces opened by an older build. `$defs` objects are
  therefore `additionalProperties: true`; the root object stays closed, since a key placed there
  belongs to no object of the model. See *Versioning policy → Unknown fields must be preserved*.

### Additive fields (backward-compatible, no version bump)

- **`Measure.id`** *(string | `null`, default `null`, at most 64 characters)* — added 2026-09-29.
  The stable identity of a measure's column, shared by measure *i* of every track: what names a
  measure from outside the file when a measure number would change with every insertion. A file
  without ids reads with positional ids `p1`..`pN`; a build that predates the field keeps the ids
  through its unknown-field bag and writes measures it inserts without one, which the next reader
  fills. See the *Measure* section.

- **`TabNote.tied`** *(boolean, default `false`)* + **`Beat.tuplet`** *(`Tuplet` | `null`, default
  `null`)* — added 2026-09-03. A tied note is not attacked again: it prolongs the previous note on
  the same string for its own beat's length, which is how a duration that no single note value
  writes, or a note held across a bar line, is notated. A tuplet is `count` beats in the time of
  `inTimeOf` (triplet = 3 in 2); every beat of the group carries it and its effective length is
  the written value × `inTimeOf` / `count`. Before these fields, an imported tie was
  re-attacked (MusicXML) or turned into a rest (Guitar Pro), and a triplet eighth was read as a
  plain eighth. A file written before them reads as untied and
  untupleted, exactly as before.

- **`Score.license`** *(string, default `""`)* + **`Score.attribution`** *(string, default `""`)*
  — added 2026-08-15 for the public-domain catalog. `license` names the license of the published
  work (`Public Domain`, `CC BY 4.0`, …); `attribution` credits the edition, year and source URL
  included. They live in the **file**, not in a page or a database, because CC-BY requires the
  attribution to follow the work when someone keeps a copy. Empty (the default, and the state of
  every user-authored score) means the file says nothing.

- **`Track.volume`** *(number 0..1, default 1)* + **`Track.instrument`**
  *(`GUITAR` | `BASS` | `PIANO` | `null`, default `null`)* — the track's place in the mix. Both are
  **arrangement data**, like `capo`: imported from Guitar Pro (MIDI channel volume and General
  MIDI program) and saved. A file written before these fields reads as full-scale, with no
  timbre imposed — exactly how it used to sound. `instrument` is deliberately narrow: it lists only
  what a player can actually render, rather than promising timbres that would silently fall back.
  **Absent is not `GUITAR`** — it means the file says nothing about the timbre, and a player should
  apply its own sound preference. Writing a default would silently override a user's choice.

- **`Score.tempoChanges`** *(TempoChange[], default [])* — mid-song tempo changes. Each
  entry sets the tempo from the start of a measure until the next one; `Score.tempo` becomes the
  *initial* tempo. Empty means constant tempo, which is exactly how every file written before this
  field reads. Tempo belongs to the score, not to a track, as in MIDI.
- **`Track.capo`** *(integer, default 0)* — capo position in frets. Tab numbers stay
  relative to the capo; only the sounding pitch shifts.
- **`TabNote.techniques`** *(TabTechnique[], default [])* + **`TabNote.bendSemitones`**
  *(integer, default 2)* — playing techniques hammer/pull, slide, bend, vibrato, tapping.
- **`TabNote.voice`** *(TabVoice | null, default null)* — voice A / B for two-hand or duet parts.
  `null` means *automatic*: the voice is derived from the register against a split point
  that belongs to the reader, not to the file. An explicit value always wins, so moving the split
  point never erases a manual assignment.

### Initial release

- `Score`: title, artist, album, tempo, tracks
- `Track`: name, tuning, measures
- `Measure`: beats, numerator, denominator
- `Beat`: duration, notes, isDotted
- `TabNote`: string, fret (0 = open, -1 = muted)
- `Duration`: WHOLE, HALF, QUARTER, EIGHTH, SIXTEENTH, THIRTY_SECOND
- Dotted notes via `isDotted: true`
