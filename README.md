# .cesure format

Open specification for `.cesure` — the native tablature format of [Cesure](https://cesure.app).
This is **version 2**. Version 1 is frozen and described in [v1.md](v1.md); every reader keeps
reading it.

## What it is

`.cesure` is a UTF-8 text file for tablature and scores. It is:

- **Lossless** — a score saved as `.cesure` re-opens identically, every time
- **Readable and writable by hand, and by agents** — a JSON skeleton (tracks, measures, metadata)
  whose notes are written in a short text notation, one string per voice and per measure
- **Addressable** — every measure carries a stable id, so a range of measures can be read or
  replaced without counting measures
- **Versioned** — an explicit `version` field, and a reader that keeps what it does not understand
- **Validated** — a [JSON Schema](schema/v2.json) describes the skeleton, and an application reads
  and writes it on every build

## Why not MusicXML, MIDI, or AlphaTex?

| Format | Human-readable | Tablature | Round-trip lossless | Versioned |
|---|---|---|---|---|
| `.cesure` | ✓ | ✓ | ✓ | ✓ |
| MusicXML | ✓ | ~ | ~ | ✗ |
| AlphaTex | ✓ | ✓ | ~ | ✗ |
| MIDI | ✗ | ✗ | ✗ | ✗ |
| GP5 | ✗ | ✓ | ~ | ✗ |

The notes of a `.cesure` file are written in a notation modelled on the AlphaTex of alphaTab,
but **defined and frozen here**: it does not follow alphaTab's
evolutions, and what this page says is the whole of it.

## A first file

```json
{"version":2,"score":{"title":"Simple Example","tempo":96,"tracks":[{"measures":[
  {"id":"p1","staves":[{"voices":["0.1.4 1.2.4 (0.3 2.4).4 r.4"]}]},
  {"id":"p2","numerator":3,"staves":[{"voices":["3.1.8{d} 2.1.16 0.1.2","0.6.2{d}"]}]}
]}]}}
```

Two measures on a standard six-string guitar: the first in 4/4 (the default), four quarter
beats — open high E, first fret on the B string, a chord, a rest; the second in 3/4, a melody over
a bass held for the whole measure (a second voice).

## File structure

```
score.cesure
└── (UTF-8 JSON)
    ├── version   2
    └── score     Score
        ├── tracks[]         Track
        │   └── measures[]   Measure  (id, time signature)
        │       └── staves[] Staff
        │           └── voices[]  string in the compact notation
        ├── tempoChanges[]   TempoChange  (by measure id)
        └── repeats{}        Repeat       (by measure id)
```

A writer omits every field that holds its default, and a reader gives an absent field its
default. Measure *i* of every track is the same **column** of the piece: same id, played at the
same time.

### Root

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | `integer` | ✓ | Format version: `2`. A reader refuses a higher one. |
| `score` | [`Score`](#score) | ✓ | The piece. |

The root holds nothing else: a key placed there belongs to nothing a reader could keep.

---

### Score

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `"Untitled"` | Title of the piece. |
| `artist` | `string` | `""` | Composer or performer. |
| `album` | `string` | `""` | Album, when the piece comes from one. |
| `tempo` | `number` | `120` | Initial tempo in **quarter notes** per minute (20 to 400), whatever the time signature, in force until the first tempo change. Whole or not: `92.5` is kept, played and written back as it is. |
| `tempoChanges` | [`TempoChange[]`](#tempochange) | `[]` | Tempo changes. Empty = constant tempo. |
| `repeats` | `{id: Repeat}` | `{}` | Repeat signs, keyed by the id of the measure that carries them. See [Repeat](#repeat). |
| `license` | `string` | `""` | License of the published work (e.g. `Public Domain`, `CC BY 4.0`). Empty = the file says nothing. |
| `attribution` | `string` | `""` | Attribution of the edition — year and source URL included when applicable. It travels **with the file** because CC-BY requires it when a copy is kept. |
| `tracks` | [`Track[]`](#track) | `[]` | The instrument tracks. |

---

### TempoChange

| Field | Type | Required | Description |
|---|---|---|---|
| `measure` | `string` | ✓ | Id of the measure at whose **start** the tempo takes effect. |
| `tempo` | `number` | ✓ | Tempo from that measure on, quarter-note beats per minute (20 to 400), whole or not. |

Tempo belongs to the piece, not to a track, and is always counted in **quarter notes per minute**:
a 6/8 felt at 60 dotted quarters per minute has tempo 90. A change is named by the id of its
measure, so it stays on that measure when measures are inserted or deleted before it. A change
naming no measure of the piece is ignored, and not written back: a version 1 file with a change
past its last measure loses it at its first save in version 2, as is a change whose tempo is not
positive, which applies to nothing.

---

### Repeat

The repeat signs of one measure — of its column, on every track. A repeat keyed by an id no
measure carries is ignored, and not written back.

| Field | Type | Default | Description |
|---|---|---|---|
| `start` | `boolean` | `false` | A repeated section opens at the start of the measure (`|:`). |
| `end` | `integer` | — | A repeated section closes at the end of the measure (`:|`): how many times the section is played in all, 2 to 99. Absent = no close. |
| `endings` | `integer[]` | `[]` | Alternative ending (volta): the passes on which the measure is played — `[1]` first ending, `[2]` second, `[1, 2]` both. A bracket longer than one measure repeats its passes on each of them. |

Playback unrolls the repeats as in Guitar Pro and MuseScore, from the structure of the whole piece.
A section opens at a `start`, or right after the previous section, or at the first measure. Its
body runs to its close or to its first bracket. Consecutive measures with the same `endings` make
one bracket, a close ends it, and the brackets run on up to the first that does not close. On pass
*p* the body is played, then the brackets whose `endings` hold *p*; a bracket that closes sends
playback back to the start of the body while passes remain. So a `[3.` after a section played twice
is never played. A bracket carrying a `start` after other brackets opens the next section: it is
also an ending of its own section, and the start of the next section's body, when its own section
still waits for every pass it names; otherwise it is the first ending of a next section with no
body. A section that no close repeats is played once, in order, its endings not read.
Da capo, dal segno, coda and fine are not part of the format yet.

A complete example, `|: A [1. B C :| [2. |: D :| E` — a first ending two measures long, and a
second ending that opens a repeat of its own, played A B C A D D E:

```json
"repeats":{"p1":{"start":true},"p2":{"endings":[1]},"p3":{"end":2,"endings":[1]},
           "p4":{"start":true,"end":2,"endings":[2]}}
```

Limit, which no editing gesture makes audible: a section with no body whose first ending names
only passes the section before it still waits for reads as an ending of that section.

---

### Track

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | `"Guitar"` | Track name. |
| `tuning` | [`Note[]`](#note) | standard tuning | Open strings from string 1 (the highest) to string N (the lowest); its length is the number of strings. Standard 6-string: `E4 B3 G3 D3 A2 E2`. |
| `capo` | `integer` | `0` | Capo position in frets. Fret numbers stay relative to the capo; only the sounding pitch moves. |
| `volume` | `number` | `1` | Volume in the mix, `0`..`1`. |
| `instrument` | `string` \| `null` | `null` | Timbre: `GUITAR`, `BASS` or `PIANO`. Absent is **not** "guitar": the file says nothing, and a player falls back to its own preference. |
| `measures` | [`Measure[]`](#measure) | `[]` | The measures of the track, in order. |

---

### Measure

**Nothing carries over from one measure to the next**: a measure without `numerator` and
`denominator` is in 4/4, not in the time signature of the measure before it. Write them on every
measure that is not in 4/4.

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `string` | — | Stable id of the measure's column, at most 64 characters. See [Measure ids](#measure-ids). |
| `numerator` | `integer` | `4` | Beats per measure (time signature numerator), 1 to 128. Cesure reads a value outside the range as 4. |
| `denominator` | `integer` | `4` | Note value of a beat: 1, 2, 4, 8, 16 or 32. |
| `staves` | [`Staff[]`](#staff) | — | The staves of the track in this measure, top to bottom. Cesure writes one. |

### Staff

| Field | Type | Required | Description |
|---|---|---|---|
| `voices` | `string[]` | ✓ | The voices of the staff, each in the [compact notation](#the-compact-notation) and with its own rhythm: the first, then a second one (a bass under a melody) when there is one. Cesure writes at most two. |

The voices of a staff are **played at the same time**, each over the whole measure: each should
fill its time signature exactly. A voice too short or too long is shown as a wrong measure, not
refused. A voice with no beat is written as an empty string.

A pickup measure (anacrusis) is not part of the format yet: a short first measure is a wrong
measure. It is reserved as an additive key of a measure.

#### Measure ids

An id names a measure from outside the file — a saved loop, a range an agent replaces — and
survives the insertion or deletion of other measures, which a measure **number** does not. Ids are
opaque. Measure *i* of every track carries the same id, no two columns share one, and an id is
never reused for another column. A writer keeps the ids it read.

A measure written without an id gets one from the reader: a file with no id at all is read with
positional ids, `p1`..`pN`; a measure missing among identified ones takes its column's id from
another track, or one the reader derives from the file alone, so that every reader of the same
file agrees.

---

### Note

An absolute pitch, used by `Track.tuning`.

| Field | Type | Description |
|---|---|---|
| `note` | `string` | Pitch class: `"C"`, `"Cs"`, `"D"`, `"Ds"`, `"E"`, `"F"`, `"Fs"`, `"G"`, `"Gs"`, `"A"`, `"As"`, `"B"` (`s` = sharp). |
| `octave` | `integer` | Octave number (scientific pitch notation): middle C is `{"note":"C","octave":4}`. |

---

## The compact notation

Each voice of a staff, in each measure, is one string: its beats, separated by spaces.

```
voice    = [ beat { " " beat } ]
beat     = content "." duration [ props ]
content  = note | "(" note { " " note } ")" | "r"
note     = fret "." string [ props ] | pitch [ props ]
fret     = integer | "x"
duration = "1" | "2" | "4" | "8" | "16" | "32" | "64"
props    = "{" prop { " " prop } "}"
prop     = name [ " " value ]
value    = integer | quoted string | "(" value { " " value } ")"
```

- **Durations**: `1` whole, `2` half, `4` quarter, `8` eighth, `16` sixteenth, `32` thirty-second,
  `64` sixty-fourth; nothing else. **Every beat states its duration** right after a dot; a beat
  without one, a duration change (`:8`), an older form (`.8d`, `.8t`, `r16`, a chord in braces
  `{5.1 5.2}.4`, effect codes `5.3:hv`) or a value outside this list is an error, named by the
  reader. Nothing carries over from one measure to the next: a
  measure can be read, written or replaced alone.
- **Notes**: `fret.string`, strings numbered from 1 (the highest); **every note names its string**
  (`7.` or `7..4` is an error), or it is written by its **pitch** (`E4`, `F#3`, `Ebb4`, grammar
  below) and the reader chooses its string and fret. `x` as fret is a muted note. A string past the strings of the track
  is kept, not refused: the note is there, silent until the track has that string again. A
  **tie** is written like any note, its fret and string included, with the note property `t`:
  `5.3{t}` prolongs, without attacking again, the note of the previous beat it continues — the
  last beat of the previous measure when it opens a measure. The reader keeps it as written and
  guesses nothing; `-` as a fret (alphaTab's tie with no fret) is an error. A chord is its notes in
  parentheses: `(0.1 1.2 0.3).4`. A rest is `r`, with no string: `r.2`.
- **Notes written by pitch**: the reader places them on the track's tuning and capo (the pitch is
  the sounding one), with the whole track around them, by the rules Cesure places an import with;
  a note written with its string keeps it exactly, and the hand reads it. A writer then writes the
  string and fret chosen. Mixed with `fret.string` notes in a voice or a chord, they take the
  strings those leave free. Refused, by name, rather than guessed: a pitch no string of the track
  reaches; a chord that leaves it no free string; `nh` or `x` on it, a hammer or slide `h`, `sl`
  from it or aimed at it (they need the string: write them as `fret.string`); a tie `t` with no
  note of its pitch to continue in the beat before; a note every string of which the other voice
  holds at that instant. A note by pitch and the ties by pitch that continue it take one string,
  and they are read whenever a string fits them at every instant they sound — free of the notes
  struck with them, of what the other voice holds, of a hammer or slide, and on the string a tie to
  or from a `fret.string` note decides; a tie never makes a readable file unreadable, and after
  a unison each tie continues a note of its own, on its string. With a harmonic (`ah n`…), the pitch written is the one the harmonic rings;
  `b`, `v`, `g`, `lht`, `tt` and `hand` are read as on any note.
- **Properties go where they apply, and the place decides**: braces right after `fret.string` are
  the note's (`5.1{v}.4`, a vibrato on that note); braces after the duration are the beat's
  (`5.1.4{d}`, a dotted quarter). In a chord, each note carries its own: `(5.1{v} 7.2).4{d}`.
- **Tuplets**: every beat of the group carries the property, and the group is the run of beats
  that carry it: `5.1.8{tu 3} 7.1.8{tu 3} 8.1.8{tu 3}` is three triplet eighths, the time of one
  quarter. A beat's length is its value × `m` / `n` for `tu (n m)`.

| Beat property | Meaning |
|---|---|
| `d` | Dotted: the duration × 1.5. |
| `dd` | Double-dotted: the duration × 1.75. Written alone, never with `d`; a beat that carries both is double-dotted. |
| `tu 3` | Triplet: three beats in the time of two of the same value. |
| `tu (n m)` | Tuplet: *n* beats in the time of *m* — `tu (5 4)` a quintuplet. |
| `tt` | Every note of the beat is tapped. |

| Note property | Meaning |
|---|---|
| `h` | Hammer-on or pull-off **to the next note on the same string** (which one follows from the frets). |
| `sl` | Slide to the next note on the same string. |
| `b (0 n)` | Bend of *n* quarter tones (`b (0 4)` is a whole tone), *n* even and read as written, negative included. Any other shape (`b (0 3)`, `b (0 4 0)`, `be`) is an error: the model holds whole semitones. |
| `v` | Vibrato. |
| `lht` | Tapped note. |
| `t` | Tied to the note it continues (see above). |
| `g` | Ghost note: played very softly (Cesure strikes it at half the loudness of the same note played full) and drawn in parentheses, `(5)`. A tied note is as soft as the note it continues. |
| `ba n` | A bend amplitude of *n* semitones kept on a note whose bend was taken off: no bend is played. |
| `kept "…"` | Everything a reader keeps on that beat or note and has no property for — the keys of a version 1 file, a technique or a hand it cannot name — as percent-encoded JSON. Write it back as it is. |
| `nh` | Natural harmonic: the open string touched over the note's own fret (12 an octave up, 7 an octave and a fifth, 5 two octaves); on a fret that rings none, the octave, as in alphaTab. |
| `ah n`, `th n`, `ph n`, `sh n`, `fh n` | Artificial, tapped, pinched, semi and feedback harmonic: the node touched *n* frets above the fretted note, a whole number (`ah 12` an octave up, `ah 7` an octave and a fifth); `ah` alone is `ah 0`. The pitch a node rings is alphaTab's. |
| `hand A` / `hand B` | The note is set to the low (`A`) or high (`B`) hand of a two-hand part. Absent = derived by the reader, not stored: the simplest rule puts a note below a split point in `A` (Cesure's default is middle C, C4); Cesure also offers the most playable hand, worked out over the whole track. The rule and its split point are reader preferences, never part of the file, and a written hand always wins over them. |

Examples: `5.3.4` (fret 5 on string 3, a quarter); `(3.6 2.5 0.4).2{d}` (a dotted half chord);
`7.2{b (0 2)}.8` (a half-tone bend, an eighth); `5.1.8{tu 3} 7.1.8{tu 3} 8.1.8{tu 3}` (a triplet of
eighths); `x.6.16` (a muted note).

### Reserved forms

These forms are part of the grammar so that they can be added later without a new version. A
reader that does not represent them keeps them as written (see below); Cesure writes none today.
The grammar of a pitch, which a note by pitch and a tuning share the octave of, and of a drum note:

```
pitch = letter [ accidental ] octave
letter = "A" | … | "G" | "a" | … | "g"
accidental = "#" | "##" | "x" | "b" | "bb"
octave = [ "-" ] integer
drum = "p" integer
```

A pitch is the **sounding** pitch, as a tuning is (scientific pitch notation: middle C is `C4`);
`##` and `x` are a double sharp, `bb` a double flat, so `C##4`, `Cx4` and `Ebb4` are all D4. A
drum note takes a place among the notes of a beat or a chord, with its own properties, and a beat
holding only such notes is silent for a reader that does not represent them.

| Form | Meaning |
|---|---|
| `{lyrics "text"}` on a beat | The syllable sung on that beat. |
| `{ch "Am7"}` on a beat | The chord symbol shown above that beat. |
| a drum note, `p42`, `(p36 p42).8` | A drum or percussion strike, by its General MIDI key from `p0` to `p127` (`p36` a bass drum, `p42` a closed hi-hat). A key past 127 is an error. |
| `Staff` past the first, `voices` past the second | More staves and voices than Cesure shows. |

## What a reader does not understand, it keeps

A reader **must keep what it does not recognise and write it back unchanged**, at the place it read
it — in the skeleton as in the notation:

- an unknown key of any object is kept with that object. One whose name, once its leading `{` are
  taken off, is a field version 2 gave that object in place of version 1's (`measure` on a tempo
  change, `staves` on a measure, `repeats` on the score) is written with one `{` more, and read
  with one less: `{measure` on a tempo change is the unknown key `measure`, `{{measure` the unknown
  key `{measure`;
- an unknown beat property is kept on its beat, an unknown note property on its note — including
  alphaTab properties the model does not hold, even those that change the rhythm (`gr`, `tr`,
  `tempo`) — and a note in a reserved form the reader does not represent stays on its beat;
- staves and voices beyond those a reader shows are kept with their measure;
- an unknown value of an **optional** field (`instrument`, `hand`) is kept and written back,
  until the user sets that field.

What cannot be kept is refused: an unknown **duration**, an unknown pitch class in a tuning, or a
beat or note the grammar cannot read, or a document whose JSON nests more than 64 levels deep. The
reader then refuses the file by naming what it could not read — guessing would change the rhythm or
the tuning.

This is what lets one account use an older and a newer build at once, and an agent add what a
build does not know yet, without either ever silently losing a part of the piece.

## For agents: working on a range of measures

- **Name measures by id.** A range is a list of ids, or a first and a last id; it survives edits
  elsewhere in the piece, where measure numbers do not.
- **Replace a range as a whole**: the measures of every track for those ids, with their time
  signatures, staves and voices. Keep the ids of the measures you keep; leave out the id of a
  measure you insert — the reader gives it one — and never reuse an id for another measure.
- **Each measure stands alone**: its durations are all written, and its voices should fill its
  time signature. A tempo change or a repeat named by the id of a measure you keep stays on it.
- **The revision is not in the file.** Whoever stores the file keeps a revision number beside it;
  an agent says which revision it read when it writes, and a write over a newer revision is
  refused, so that nobody overwrites what they have not seen.
- **Validate the skeleton** with [the JSON Schema](schema/v2.json) before writing; the notation is
  checked by the reader, which names the beat it cannot read.

## Transport

A `.cesure` file is plain text that compresses about five times over: a server **should**
compress it in transit (`Content-Encoding: gzip` or `br`), and a client should accept it so. The
file itself is never compressed.

## Versioning policy

| Change | Action |
|---|---|
| A field with a default, a beat or note property, a [reserved form](#reserved-forms) put to use | No new version: a reader that does not know it keeps it |
| A value added to an optional enum (`instrument`) | No new version: kept by a reader that cannot name it |
| A new duration, a new pitch class, a removed, renamed or retyped field | New version, with a migration from every older one |

The durations of version 2 go down to the sixty-fourth (`64`): version 1 stopped at the
thirty-second. The tempo became a number within version 2: every file read before reads the same,
and a reader that still takes it as an integer refuses only a file whose tempo is not whole.

A reader **refuses** a file whose `version` is above the ones it reads, rather than misread it.
Version 1 files ([v1.md](v1.md)) are read forever and migrated in memory; nothing writes them.
A key that a version 1 file held on a beat or a note, unknown to the reader, is kept: saved in
version 2, it goes into the `kept` property of that beat or note, its name and value unchanged —
a name opening with `{` included: read back, a key of `kept` is kept exactly as the same key of the
file would be. A `kept` whose value is not percent-encoded JSON (`%+1`, `%FF` alone, a value that
is not an object) is an error, named by the reader. A key that a version 1 file held on another
object keeps its name the same way, including a name version 2 gives a field of that object
(`measure` on a tempo change, `staves` on a measure, `repeats` on the score): it is written
`{measure`, and read back as the key `measure`, never as the field. A version 1 file escaped
nothing and is read as written: its key `{repeats` is the key `{repeats`, saved as `{{repeats`.

## JSON Schema

[`schema/v2.json`](schema/v2.json) (JSON Schema Draft 2020-12), served at
`https://cesure.app/format/schema/v2.json`, describes the skeleton; the version 1 schema stays at
[`schema/v1.json`](schema/v1.json). Validate the schemas and every example with:

```sh
pip install jsonschema
python3 scripts/validate.py
```

## Examples

- [`examples/simple.cesure`](examples/simple.cesure) — one track, two measures, a second voice
- [`examples/song.cesure`](examples/song.cesure) — several measures with chords, rests, a repeat
- [`examples/band.cesure`](examples/band.cesure) — a guitar and a drum part written by General MIDI
  key, at a tempo that is not whole
- [`examples/v1/`](examples/v1/) — the version 1 examples, as they were

## Maintenance

The format is developed and regression-tested inside the Cesure application; this section documents
**how it stays stable** (the tooling lives in the app repository, not here).

**A `.cesure` file that a user saved must open identically forever.** Before changing the model or
the notation:

1. **Additive** (a field with a default, a property, a reserved form put to use) → no new version.
   Update this README, `schema/v2.json` and `CHANGELOG.md`, and add the addition to a file of the
   corpus so that it is actually exercised.
2. **Structural** (see the table above) → raise `CURRENT_VERSION` in `CesureSerializer`, add the
   migration, and keep a frozen file of every older version: it must still load.
3. **Never edit a frozen file to make a test pass**: an old file that no longer reads the same is
   the bug.
4. **Run the guards** — all in `:score`: `./gradlew :score:jvmTest`. They hold the schema against
   the model, the round trip of every example and catalog piece, the frozen v1 corpus, the refusal
   of a newer version, and the keeping of unknown keys, properties and values.

## The application behind the format

`.cesure` is written and read by **[Cesure](https://cesure.app)** — a guitar tablature editor and
practice toolkit that runs [in the browser](https://cesure.app), on Android and on iOS. It imports
Guitar Pro, MusicXML, MIDI and AlphaTex, transcribes audio to tablature, and plays scores back with
a tuner, a metronome and a piano roll. The schema in this repository is checked against its model
on every build, so a field added on one side and not the other fails the build.

## License

This specification is released under the [MIT License](LICENSE).
