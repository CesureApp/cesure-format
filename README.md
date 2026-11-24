# .cesure format

Open specification for `.cesure` — the native tablature format of [Cesure](https://cesure.app).
This is **version 4**. Versions 3, 2 and 1 are frozen and described in [v3.md](v3.md), [v2.md](v2.md)
and [v1.md](v1.md); every reader keeps reading them ([Reading version 3](#reading-version-3)).

## What it is

`.cesure` is a UTF-8 text file for tablature and scores. It is:

- **Lossless** — a score saved as `.cesure` re-opens identically, every time
- **Readable and writable by hand, and by agents** — a JSON skeleton (tracks, measures, metadata)
  whose notes are written in a short text notation, one string per voice and per measure
- **Addressable** — every measure carries a stable id, so a range of measures can be read or
  replaced without counting measures
- **Versioned** — an explicit `version` field, and a reader that keeps what it does not understand
- **A note is its pitch** — named as it was written (`D#5` is not `Eb5`); the string it is played on
  is a layer on top of it, on a track that has strings, and the fret is never written: it follows
  from the pitch, the string, the tuning and the capo
- **Validated** — a [JSON Schema](schema/v4.json) describes the skeleton, and an application reads
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
{"version":4,"score":{"title":"Simple Example","tempo":96,"key":{"fifths":0,"mode":"major"},"tracks":[
 {"id":"t1","name":"Guitar","instrument":"pluck.guitar.nylon-string","program":24,
  "staves":[{"clef":"treble8vb","type":"tablature"}],
  "tuning":["E4","B3","G3","D3","A2","E2"],"frets":24,"measures":[
  {"id":"p1","uncounted":false,"staves":[{"voices":["E4@1.4 C4@2.4 (G3@3 E3@4).4 r.4"]}]},
  {"id":"p2","numerator":3,"staves":[{"voices":["G4@1.8{d} F#4@1.16 E4@1.2","E2@6.2{d}"]}]}]},
 {"id":"t2","name":"Piano","instrument":"keyboard.piano.grand","program":0,
  "staves":[{"clef":"treble","type":"pitched"},{"clef":"bass","type":"pitched"}],"measures":[
  {"id":"p1","uncounted":false,"staves":[{"voices":["E5.4 C5.4 (G4 C5).4 r.4"]},{"voices":["C3.1"]}]},
  {"id":"p2","numerator":3,"staves":[{"voices":["G5.8{d} F#5.16 E5.2"]},{"voices":["E3.2{d}"]}]}]}
]}}
```

Two measures on a standard six-string guitar and on a piano: the first in 4/4 (the default),
four quarter beats — open high E, first fret on the B string (C4 on string 2), a chord, a rest; the
second in 3/4, a melody over a bass held for the whole measure (a second voice). The guitar has a
tuning, so each of its notes says its string; the piano has none, and writes its right hand over
its left, on two staves.

## File structure

```
score.cesure
└── (UTF-8 JSON)
    ├── version   4
    ├── requires  string[]  (absent: nothing)
    └── score     Score
        ├── measures[]       Measure  (id, time signature, count, bar line, repeat: once for every track)
        ├── tracks[]         Track
        │   └── measures[]   TrackMeasure  (measure i of the piece)
        │       └── staves[] Staff
        │           └── voices[]  string in the compact notation
        ├── tempoChanges[]   TempoChange  (by measure id and beat)
        └── keyChanges[]     KeyChange    (by measure id)
```

A writer omits every field that holds its default, and a reader gives an absent field its
default — except the fields this version **requires**, written whatever their value: the score's
`measures`; every track's `id`, `name`, `instrument`, `program`, `staves` and, beside a `tuning`, its
`frets`; every measure's `id`; the first measure's `uncounted`; a key's `fifths` and `mode`. A reader never
refuses a file that lacks one: it completes it by the rule an older version reads it with — the `instrument`
by the strings (a guitar on a `tuning`, else a piano), the `program` by the family, an `id` drawn, the default
`name`, `24` frets, the staves its measures write in its instrument's clefs, the opening counted as the
[pickup rule](#pickup-short-endings-and-irregular-measures) implies, a missing `fifths` `0` and `mode`
`none`; a score without `measures` is read as version 3 wrote it, each track's measures saying their own
id and time signature. A reader refuses only what it cannot play right.

What holds for a measure of every track — its id, time signature, count, bar line, repeat signs — is
written **once**, in the score's [`measures`](#measure), as MuseScore's `<Measure>`: no two tracks can
disagree on it. A track's [measure](#trackmeasure) holds its content alone: measure *i* of every
track is measure *i* of the piece, played at the same time.

### Root

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | `integer` | ✓ | Format version: `4`, an integer, never `4.0` nor `"4"`. A reader refuses a higher one, and reads `3`, `2` and `1` forever. |
| `requires` | `string[]` | — | What a reader must know to read the file right, as glTF's `extensionsRequired`: the names of the additions a file uses that change what is heard or read (a rhythm, a pitch). A reader that does not know a name listed refuses the file as one of a newer version, and proposes the update — before it reads anything else. Absent or empty, nothing is required: it is empty in every file of this version, and not written then. A list of anything but names is refused. |
| `score` | [`Score`](#score) | ✓ | The piece. |

A key the root holds beside these, which a later build may write, is kept and written back.

---

### Score

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `"Untitled"` | Title of the piece. |
| `artist` | `string` | `""` | Composer or performer. |
| `album` | `string` | `""` | Album, when the piece comes from one. |
| `tempo` | `number` | `120` | Initial tempo in **quarter notes** per minute (4 to 999), whatever the time signature, in force until the first tempo change. Whole or not: `92.5` is kept, played and written back as it is. `0`, which no writer is to write, reads as no tempo: the piece takes 120. A reader refuses a file whose tempo, or a tempo change above 0, lies outside 4 to 999, naming the range. |
| `tempoChanges` | [`TempoChange[]`](#tempochange) | `[]` | Tempo changes. Empty = constant tempo. |
| `key` | [`Key`](#key) | required | The key of the piece from its first measure, always written: as a source or the user states it, else the signature its notes give and no mode (`none`, as MusicXML writes a `<key>` naming no tonic) — found when the file is first written and after a gesture that changes what it sounds, never again by a later build that only reads it. A reader shows a key of no mode in the mode it finds for that signature, a suggestion it never writes; a file without `key` is completed the same way. See [KeyChange](#keychange). |
| `keyChanges` | [`KeyChange[]`](#keychange) | `[]` | Key changes. Empty = one key for the whole piece. |
| `measures` | [`Measure[]`](#measure) | required | The measures of the piece, in order, each written once for every track: its id, time signature, count, bar line and [repeat signs](#repeat). A key the score holds named `measures` that is no list of measures — one an older file kept — is written `{measures`; a key named `repeats`, a field of version 3 and no more, is written by its name. |
| `license` | `string` | `""` | License of the published work (e.g. `Public Domain`, `CC BY 4.0`). Empty = the file says nothing. One line: a line break in it is read as a space, and written back so (as is one in `attribution`). |
| `attribution` | `string` | `""` | Attribution of the edition — year and source URL included when applicable. It travels **with the file** because CC-BY requires it when a copy is kept. |
| `hideEmptyStaves` | `boolean` | `false` | Whether the staves whose `hideWhenEmpty` is `auto` leave a system they play nothing in (MuseScore's "Hide empty staves"). |
| `hideEmptyStavesInFirstSystem` | `boolean` | `false` | Whether the first system too leaves out the staves that hide when empty (LilyPond's `remove-first`). |
| `tracks` | [`Track[]`](#track) | `[]` | The instrument tracks: measure *i* of each is measure *i* of `measures`. |

---

### TempoChange

| Field | Type | Required | Description |
|---|---|---|---|
| `measure` | `string` | ✓ | Id of the measure the tempo falls in. |
| `at` | `number` | | Where in that measure the tempo falls, in **quarter notes** from its start (`1.5`: on the second eighth of the second beat of a 4/4), less than the measure's length. Absent: at its start. |
| `tempo` | `number` | ✓ | Tempo from that beat on, quarter-note beats per minute, whole or not. A writer writes it between 4 and 999; a reader ignores a change at 0 or below. |

Tempo belongs to the piece, not to a track, and is always counted in **quarter notes per minute**:
a 6/8 felt at 60 dotted quarters per minute has tempo 90. A change falls on a beat, as MuseScore
places a tempo text: mid-measure, the beats after it in the measure play at the new tempo. A
place no beat of a track starts at is a place all the same (a gradual slowing down read from a
MIDI file falls between notes). An `at` that is not a number, below 0, or at or past the end of
its measure is refused. A change is named by the id of its
measure, so it stays on that measure when measures are inserted or deleted before it; one whose
measure is deleted goes to the start of the next measure that remains. A change
naming no measure of the piece is ignored, and not written back: a version 1 file with a change
past its last measure loses it at its first save in version 2, as is a change whose tempo is not
positive, which applies to nothing.

---

### KeyChange

| Field | Type | Required | Description |
|---|---|---|---|
| `measure` | `string` | ✓ | Id of the measure at whose **start** the key takes effect. |
| `key` | [`Key`](#key) | ✓ | Key from that measure on, written as the score's `key`. |

Like the tempo, the key belongs to the piece, not to a track, and a change is named by the id of
its measure. A change naming no measure of the piece is ignored, and not written back. The key is the
one heard: transposing the piece moves it with the sound, and so does a capo every track has; with
tracks under different capos it is the key the piece has without one.

---

### Key

`{"fifths": 2, "mode": "major"}`: MusicXML's `<key>`, which MuseScore writes too.

| Field | Type | Required | Description |
|---|---|---|---|
| `fifths` | `integer` | ✓ | The signature: sharps (positive) or flats (negative), `-7` to `7`; `0` none. |
| `mode` | `string` | ✓ | A mode of MusicXML: `major`, `minor`, `ionian`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`, or `none` — a signature naming no tonic. |

The tonic of a mode is its degree of the major scale of the signature: `{"fifths": 0, "mode": "dorian"}` is D
dorian. A key is spelled as the major or minor key of its signature (`aeolian` as the minor, any other
as the major), and a transposition keeps its mode. A `mode` the reader does not know is read as `none`,
a whole `fifths` past seven as `0`; either, and any other key of the object, is kept as written and
written back, until the key is changed.

---

### Repeat

The repeat signs of one measure of the piece, its [`repeat`](#measure), on every track.

| Field | Type | Default | Description |
|---|---|---|---|
| `start` | `boolean` | `false` | A repeated section opens at the start of the measure (`|:`). |
| `end` | `integer` | — | A repeated section closes at the end of the measure (`:|`): how many times the section is played in all, 2 to 99; any other value is refused, naming the repeat. Absent = no close. |
| `endings` | `integer[]` | `[]` | Alternative ending (volta): the passes on which the measure is played — `[1]` first ending, `[2]` second, `[1, 2]` both, each from 1 to 99 (any other is refused). A bracket longer than one measure repeats its passes on each of them. A repeat with no sign at all (`{}`) says nothing, and is not written back. |
| `directions` | `string[]` | `[]` | The signs and jumps of the measure, named as alphaTab names them: the signs `Segno`, `SegnoSegno`, `Coda`, `DoubleCoda`, `Fine`; the jumps `DaCapo`, `DaCapoAlCoda`, `DaCapoAlDoubleCoda`, `DaCapoAlFine`, `DalSegno`, `DalSegnoAlCoda`, `DalSegnoAlDoubleCoda`, `DalSegnoAlFine`, `DalSegnoSegno`, `DalSegnoSegnoAlCoda`, `DalSegnoSegnoAlDoubleCoda`, `DalSegnoSegnoAlFine`; and `DaCoda`, `DaDoubleCoda` (To Coda, To Double Coda). Any other name plays as none and is kept: the list is written back as written, every name at its place, while the names a reader knows are unchanged — once they change, after them. A reader that does not know this field keeps it and writes it back. |
| `section` | `boolean` | `false` | The measure opens a section (a movement, MuseScore's section break): its repeats and jumps are played on their own, a da capo going back to the section's first measure and a `Fine` ending only the section, after which playback goes on with the next one. Any other value than `true` or `false` is refused, naming the repeat. A reader that does not know this field keeps it and writes it back. |

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

The `directions` are then followed, as Gould and MuseScore play them. Repeats are played up to a
jump, taken on the last pass through its measure; a da capo goes back to the first measure, a dal
segno to the nearest segno at or before it (else the first after it, as Guitar Pro looks it up).
From there the repeats are not played again and only the ending of the last pass is taken; `Fine`
ends the piece, and `DaCoda` leaves for the nearest `Coda` after it (else the last before it), only
after a jump that names them (al Fine, al Coda). From the coda on, repeats are played again. Each
jump and each To Coda is taken once, and one with nowhere to go (no segno, no coda) is ignored.

A complete example, `|: A [1. B C :| [2. |: D :| E` — a first ending two measures long, and a
second ending that opens a repeat of its own, played A B C A D D E:

```json
"measures":[{"id":"p1","uncounted":false,"repeat":{"start":true}},{"id":"p2","repeat":{"endings":[1]}},
            {"id":"p3","repeat":{"end":2,"endings":[1]}},{"id":"p4","repeat":{"start":true,"end":2,"endings":[2]}},
            {"id":"p5"}]
```

Limit, which no editing gesture makes audible: a section with no body whose first ending names
only passes the section before it still waits for reads as an ending of that section.

---

### Track

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `string` | required | What tells the track from the others of its score, whatever its place, as MusicXML's `<score-part id>`: opaque, at most 64 characters, unique in the file. See [Track ids](#track-ids). |
| `name` | `string` | required | Track name, shown as written. |
| `tuning` | `string[]` | — | Open strings, as [pitches](#pitch), from string 1 (the highest) to string N (the lowest); its length is the number of strings — standard 6-string `["E4","B3","G3","D3","A2","E2"]`. An open string has no name of its own: a flat is read as the sharp of the same pitch (`Eb4` is `D#4`) and written so. **Absent = the track has no strings** (a piano, a voice, a flute): its notes are pitches alone. An open string a version 2 file wrote as a [Note](#note) object with keys a reader does not know is written back as that object. |
| `capo` | `integer` | `0` | Capo position in frets, only with a `tuning` — a capo without one is refused. A note is its sounding pitch: the capo moves the fret it is played at, never what it sounds. |
| `frets` | `integer` | required with a `tuning` | The frets of the neck, `1`..`127`, as MuseScore's `<StringData><frets>` and Guitar Pro's; only with a `tuning`, ignored without one. A capo sits under the last fret: one at or past it (a file written before `frets`, capoed at `24`) makes the neck reach the fret past the capo, nothing refused. A note past the last fret is kept on its string, played as written and drawn out of the neck; frets whose note would sound past `G9` take none. A value outside `1`..`127` is refused, naming the track. |
| `volume` | `number` | `1` | Volume in the mix, `0`..`1`. |
| `hideWhenEmpty` | `string[]` | `[]` | How each staff, by index, hides in a system it plays no note in, as MuseScore's per-staff "Hide when empty": `auto` as the score's `hideEmptyStaves` says, `always` on its own, `never` not, `instrument` only with the whole track, when none of its staves plays. A staff past the list is `auto`; a staff left out stays in the file; a system keeps one staff at least, its first when every staff leaves. |
| `instrument` | `string` | required | What the track is played on: an instrument sound id of MusicXML (`sounds.xml`, the `<instrument-sound>` vocabulary MuseScore writes too), an open vocabulary — `pluck.guitar.nylon-string`, `pluck.bass.electric`, `keyboard.piano.grand`, `drum.group.set`, `strings.violin`, `wind.flutes.flute`, `voice.alto`. A reader handles the families it knows by their prefix: `keyboard.piano` (a piano: without a `tuning`, written on two staves, see [Staff](#staff)), `pluck.guitar`, `pluck.bass`, and `drum.group.set`, the General MIDI drum kit — no strings, its beats strike [drum notes](#note) (`p36`), drawn on a percussion staff and sounding the standard kit. Any other id is kept as written, and the track sounds its `program`. The four words version 3 wrote (`PIANO`, `GUITAR`, `BASS`, `DRUMS`, in any case) are read as their family's sound — no id of MusicXML is a bare word —, and written back as the sound the app writes for that family. A track whose source named no instrument (a scanned page) is written as the app takes it: a guitar (`pluck.guitar…`) with a `tuning`, a piano (`keyboard.piano…`) without, on staves that say it is no grand staff (see `staves`). **What the track is, when its `instrument` says otherwise than its notes, strings or staves — the staves first, then the sound**: the `type` of its `staves` says what the track is, a `percussion` staff a drum kit, any other a track of pitches, and a note of the other kind is refused; where no staff says a type a reader knows, the notes decide as in version 3 — notes all [drum hits](#note) make a drum kit, whatever the sound; pitches are never a kit's —; else the sound's family, a `keyboard.piano` being the grand staff only on treble over bass (see `staves`); else, a family the reader does not handle, by the strings — a guitar with a `tuning`, a piano without. The `instrument`, the `program` and the `tuning` are kept and written back as declared whatever family is read: a reader never drops a sound that contradicts the rest. A drum kit never holds strings, whatever the version of its file: a `tuning`, `capo` and `frets` declared on one are kept and written back as they are, and play and show nothing. |
| `program` | `integer` | required | The General MIDI program, `0`..`127` (General MIDI's program 1 is `0`), the track sounds: as its source states it, else its instrument's — a nylon guitar (`24`), a finger bass (`33`), a grand piano (`0`). On a drum kit it is `0` unless its file states another, written back as stated and ignored: the track sounds the standard kit. A value outside `0`..`127` is refused, naming the track. |
| `staves` | `object[]` | required | The staves the track is drawn on, top to bottom, as MusicXML's `<staves>` and the `<clef number>` of each: one object per staff, its `clef` the one it opens on where no measure writes one (a [clef](#staff) name). A piano's two hands at least, else as many as a measure holds; a measure holding more keeps them, each drawn in its instrument's clef. A `keyboard.piano` track without a `tuning` is the grand staff — right hand over left — only on a `treble` staff over `bass` ones; on any other clefs (one `treble` staff, `treble` over `treble`) it is a part its source named no instrument for, each staff drawn on its own, sounding a piano. A staff declared past the ones a measure holds is drawn, a measure rest where nothing is written, as MuseScore adds a staff. A staff is drawn in the `clef` it declares — a name a reader does not draw is kept, written back and drawn as its instrument's —, and a key it does not know is kept and written back. Each staff says its `type`, as MuseScore's staff type groups: `pitched`, `tablature` or `percussion` — what the track is, never how a reader shows it: a writer declares `percussion` for a drum kit, `tablature` for a track with a `tuning`, `pitched` for any other; a reader takes a `percussion` staff for a drum kit (a pitch on it is refused), any other for a track of pitches (a drum hit on it is refused, a kit's sound naming no family there), a `tablature` without a `tuning` on its family's standard one (a bass's, else a guitar's); a `percussion` staff beside another type is refused; a `pitched` staff on a track with a `tuning` is kept and written back; a name a reader does not know is kept and written back, and where no staff says one it knows, the notes decide. A change of instrument gives the track the new instrument's staves and sound, as MuseScore does: a file never declares another staff, clef or sound than the one the track is drawn on and played as. |
| `measures` | [`TrackMeasure[]`](#trackmeasure) | `[]` | The measures of the track, in order: measure *i* is measure *i* of the score's [`measures`](#measure). A track may hold fewer measures than another: it is silent after its last one. |

A measure of `measures` past every track's last is a measure of the piece, silent on every track.

---

### Measure

A measure of the piece, in the score's `measures`: what it holds holds for every track, as MuseScore's
`<Measure>` holds it for every staff. **Nothing carries over from one measure to the next**: a measure
without `numerator` and `denominator` is in 4/4, not in the time signature of the measure before it.
Write them on every measure that is not in 4/4.

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `string` | required | Stable id of the measure, at most 64 characters. See [Measure ids](#measure-ids). |
| `numerator` | `integer` | `4` | Beats per measure (time signature numerator), 1 to 128. Cesure refuses a file that writes a value outside the range, naming it. |
| `denominator` | `integer` | `4` | Note value of a beat: 1, 2, 4, 8, 16 or 32. |
| `incomplete` | `boolean` | `false` | Irregular on purpose, in its own signature: shorter than the piece's measures (an opening pickup, a closing measure that completes it, an inner pickup) or longer (a stretch of a cadenza). See [Pickup, short endings and irregular measures](#pickup-short-endings-and-irregular-measures). |
| `barLineRight` | `string` | — | The style of the bar line that closes the measure, by the name alphaTab gives it (`\barLineRight`, MusicXML's `bar-style`): `automatic`, `dashed`, `dotted`, `heavy`, `heavyHeavy`, `heavyLight`, `lightHeavy`, `lightLight`, `none`, `regular`, `short` or `tick`. Cesure draws `none` as no line and every other one as the regular line. Absent: the regular line. Any other name is kept, written back, and drawn as the regular line. |
| `uncounted` | `boolean` | `false`; required on the first measure | Left out of the measure count, as MusicXML's `implicit` and MuseScore's "exclude from measure count": the measure carries the number of the one before it and shows none. Always written on the first measure, which says whether a pickup counts. |
| `tsVisibility` | `boolean` | `true` | Whether the time signature the measure would engrave — at the head of the piece, or where the meter changes — is printed, by the name alphaTab gives it (`\barDisplay { tsVisibility false }`): `false` as MusicXML's `print-object="no"`, where the source engraves none. |
| `barNumberDisplay` | `string` | — | How the measure's number shows, by the name alphaTab gives it (`\barNumberDisplay`): `hide` for a measure counted without its number in sight, as LilyPond parenthesises the number of the measure a cadenza closing on a bar line opens. Absent: the rule. Any other name is kept, written back, and shown as the rule. |
| `meter` | `[integer, integer]` | — | The nominal time signature of an irregular measure when no regular measure gives it (a piece all in a cadenza), as MuseScore keeps a measure's time signature beside its actual length. Written only there. A pair that is no time signature is kept, written back, and shown as none. |
| `repeat` | [`Repeat`](#repeat) | — | The repeat signs of the measure. Absent: none. |

A key a measure holds that a reader does not know is kept with it, and written back, as is its `repeat`
— under the id a reader completes it with when a file leaves the `id` out.

### TrackMeasure

A track's measure *i*, in measure *i* of the piece: its content.

| Field | Type | Default | Description |
|---|---|---|---|
| `chords` | `object[]` | `[]` | The chord symbols written over the measure, in order, one per instant: `{"at": 2, "chord": "G/B"}`, `at` the quarter notes from the start of the measure — absent at its start —, at any instant, a beat struck there or inside a held note (MuseScore's time tick); each from its instant to the next. `chord` is read as a lead sheet writes it: a text is a chord when a root opens it and its suffix, if any, opens as a chord's does — a digit, a sign (`+ - ° ø Δ ( # b ^`), a quality (`m`, `M`, `maj`, `min`, `dim`, `aug`, `sus`, `add`, `alt`, `no`) or the diminished `o` alone or before a digit: `C7M`, `C7+`, `Cø`, `Co7` —, then the bass after the last slash when a name ends the text there (`G/B`); any other text (`N.C.`, `Coda`) is kept whole and never transposed. At most 40 characters, blanks folded into one. It never changes what sounds. |
| `staves` | [`Staff[]`](#staff) | — | The staves of the track in this measure, top to bottom, as many as the track has — a piano's two hands, an organ's three, a guitar's notation and its second part —, as MuseScore, Guitar Pro and MusicXML hold a part. Every staff of a track is played and drawn. Absent: the measure holds no staff, and the track is silent there. |

A field of the [Measure](#measure) written on a track's measure — as version 3 wrote them — is no field of
it. An `id` there is the measure's own said again: another one is refused, naming it. A mark (`numerator`,
`incomplete`, `barLineRight`…) equal to the measure's says nothing, and is not written back; a different
one is what an older file gave that track where its first track gave another: the track's own, kept and
written back, never read — the measure's holds ([Reading version 3](#reading-version-3)).

**A local time signature is reserved**: `numerator` and `denominator` on a track's measure are the time
signature of that track alone in that measure, as MusicXML gives each part its own `<time>` (polymeter)
and MuseScore a staff its local time signature. This version plays and draws every track in the
measure's: a reader keeps the track's, written back, never read. A file that asks for it to be played
will name `localTimeSignature` in `requires`, with no new version.

### Staff

| Field | Type | Required | Description |
|---|---|---|---|
| `voices` | `string[]` | ✓ | The voices of the staff, one to four, each in the [compact notation](#the-compact-notation) and with its own rhythm: the first, then a second one (a bass under a melody) when there is one, up to a fourth — the first and the third drawn stems up, the second and the fourth stems down. A fifth voice is refused where the file enters, naming the measure, the track and the staff. |
| `clef` | `string` | — | The clef this staff **opens this measure on**, as MusicXML draws one, a sign on a line: `treble` (G on line 2), `soprano`, `mezzosoprano`, `alto`, `tenor`, `baritone` (C on lines 1 to 5), `bass` (F on line 4), each followed when its notes sound octaves off where they stand by `8vb`, `8va`, `15mb` or `15ma` (`treble8vb`, the guitar's; `alto8vb`): a name a reader does not know is kept and written back; a value that is not a name is refused. A change of clef is written on every measure that opens in the new clef; a change in the middle of a measure is the beat property `clef` ([below](#the-compact-notation)). Absent from a measure, the clef that measure opens on is the one its track declares for that staff (`staves`); the instrument's clefs, those a writer declares for a track that says no other, are: a `keyboard.piano` without a `tuning` (the grand staff) `treble` then `bass`; a `pluck.bass` `bass8vb`; any other track with a `tuning` `treble8vb`; a `drum.group.set` the percussion staff; any other track without a `tuning` `treble`. **A clef never changes what sounds**: a note is its sounding pitch, whatever the clef it is drawn in, and a field that one day says a written pitch apart from the sounding one will not count the clef's octave. |

**A piano is one track on two staves**: `staves[0]` is the right hand, `staves[1]` the left, each
with its voices, measure by measure — up to four per hand, each in a rhythm of its own, so that one
hand can play several rhythms while the other plays; a staff past the second is a staff of the left
hand's side (an organ's pedals). A note is in the hand of the staff it is written
on, so `hand` is not written there — a `hand` on a piano's staff is refused. Each voice of each
staff is read and written back as it is; a left hand with nothing to play writes a rest of each
value of the right hand's first voice.

The voices of a staff are **played at the same time**, each over the whole measure: each should
fill its time signature exactly. A voice too short or too long is shown as a wrong measure, not
refused. A voice with no beat is written as an empty string.

#### Pickup, short endings and irregular measures

A pickup (anacrusis) is a measure in its **own** time signature — an eighth before a piece in 3/8
is a `1/8` measure — marked `"incomplete": true`. A closing measure that completes it (two eighths
in 3/8) is written the same way, and so is a short measure anywhere inside the piece — the two halves
of a measure split by a repeat sign, a section that opens on its own pickup. Each voice still fills the measure's own signature, and it is
played as written: the mark changes how it is shown, never how it sounds. Cesure shows an
incomplete measure the time signature of its nearest complete neighbour (the next one for an
opening pickup, else the one before it), so a piece in 3/8 opening on an eighth shows `3/8` once; an opening pickup is measure 0
and shows no number, the first full measure is 1. A short measure without the mark is a wrong
measure. A reader that does not know the key keeps it and writes it back.

A measure longer than the piece's meter on purpose — a stretch of a cadenza, cut where the source draws a
bar line, often an invisible one — is written the same way: its own signature is its real length
(`27/16` for a cadenza stretch of twenty-seven sixteenths in 4/4), marked `"incomplete": true`; it shows
and beams in the meter of its regular neighbour — or, in a piece without one, in its `"meter"`. Such a stretch usually also closes on `"barLineRight":
"none"` and, past the first of the cadenza, is `"uncounted": true`, as LilyPond numbers a cadenza.

#### Track ids

A track id names a track whatever its place: what a person chose for that track — how they see it,
on their own device — stays with it when other tracks are added, removed or reordered, and never
passes to another. A writer keeps the ids it read and gives a new track a new id, never one a track
of the score held before. Every track of a version 4 file carries its id. A track written without an id —
in an older version, or in version 4 by a writer that left it out —, or repeating the id of an earlier track,
gets one the reader derives from what the track holds — never from its place —, so that every reader
of the same file agrees, and a track a writer that knows no id removed or moved lends its id to none. Added 2026-11-18, no new version: a reader that does not
know the key keeps it with its track and writes it back.

#### Measure ids

An id names a measure from outside the file — a saved loop, a range an agent replaces — and
survives the insertion or deletion of other measures, which a measure **number** does not. Ids are
opaque. A measure of the piece carries its id once, for every track, no two measures share one, and an
id is never reused for another measure. A writer keeps the ids it read. A piece that names two of its
measures alike is refused, naming them.

Every measure of a version 4 file carries its id. A measure written without an id — in an older
version, or in version 4 by a writer that left it out — gets one from the reader: a file with no id at all is read with
positional ids, `p1`..`pN`; a measure missing among identified ones takes its column's id from
another track, or one the reader derives from the file alone, so that every reader of the same
file agrees.

---

### Note

An absolute pitch as version 2 wrote an open string; version 3 reads it in a `tuning` too, and
writes it only for an open string that keeps keys a reader does not know.

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
note     = pitch [ "@" string ] [ props ] | "x@" string [ props ] | drum [ props ]
pitch    = letter [ accidental ] octave
letter   = "A" | … | "G" | "a" | … | "g"
accidental = "#" | "##" | "x" | "b" | "bb"
octave   = [ "-" ] integer
drum     = "p" integer
duration = "-2" | "1" | "2" | "4" | "8" | "16" | "32" | "64" | "128" | "256"
props    = "{" prop { " " prop } "}"
prop     = name [ " " value ]
value    = integer | quoted string | "(" value { " " value } ")"
```

- **Durations**: `-2` breve (double whole, alphaTab's value), `1` whole, `2` half, `4` quarter,
  `8` eighth, `16` sixteenth, `32` thirty-second, `64` sixty-fourth, `128` hundred-twenty-eighth,
  `256` two-hundred-fifty-sixth; nothing else. **Every beat states its duration** right after a dot;
  a beat without one, a duration change (`:8`), an older form (`.8d`, `.8t`, `r16`, a chord in braces
  `{5.1 5.2}.4`, effect codes `5.3:hv`) or a value outside this list is an error, named by the
  reader. Nothing carries over from one measure to the next: a measure can be read, written or
  replaced alone.
- <a id="pitch"></a>**A note is its pitch**, the one that **sounds** (scientific pitch notation:
  middle C is `C4`; `##` and `x` a double sharp, `bb` a double flat). It is **named as written**:
  `D#5` and `Eb5` are two notes written differently, and a reader keeps the name and never changes
  it; a writer writes it back as it is. A writer writes a letter in capitals. **A pitch is at most
  `G9`**, MIDI's last key (127), however it is spelled (`Fx9`, `Abb9`): a note past it is an error.
- **On a track with strings, `@n` says the string**, numbered from 1 (the highest): `E4@1` is the
  open high E, `G4@1` its third fret. **The fret is never written**: it follows from the pitch, the
  string, the tuning and the capo. A note without `@` there is placed by the reader, by the rules
  Cesure places an import with, the whole track around it, and a writer writes the string chosen;
  mixed with notes that say their string, it takes the strings those leave free. Refused, by name,
  rather than guessed: a pitch lower than every open string of the track; a chord that leaves it no free
  string; a hammer or slide `h`, `sl` from it or aimed at it, or `nh` on it (they need the string);
  a tie `t` with no note of its pitch to continue. A string past the strings of the track is kept:
  the note sounds its pitch, and has no fret until the track has that string again. **On a track
  without strings, `@` is an error**: the note is its pitch alone.
- **A muted note** has no pitch, only a string: `x@6`.
- **A drum note** is `p` and its General MIDI key, from `p0` to `p127` (`p36` a bass drum, `p42` a
  closed hi-hat): it takes a place among the notes of a beat or a chord, with its own properties;
  a key past 127 is an error. It is a note of a `DRUMS` track, which holds no other: it sounds that key
  of the General MIDI standard kit and is drawn on the percussion staff where the kit writes that piece.
  A track written without an instrument whose notes are all drum notes — what files written before
  `DRUMS` hold — is read as a `DRUMS` track; a track mixing drum notes and pitches, or holding drum notes
  under an instrument with pitches, is an error naming the track. A reader that does not represent it
  keeps it on its beat.
- **On input only**, a reader also takes a note written `fret.string` (`3.1`, `x.6` muted) on a
  track with strings, as a tablature is copied: it is the pitch that place sounds, named as the key
  in force in the measure names it, on that string, and a writer writes it back as `G4@1`. On a
  track without strings, such a note has no pitch: it is kept on its beat as written, silent.
- A **tie** is written like any note, with the note property `t`: `E4@1{t}` prolongs, without
  attacking again, the note it continues on its line — its string, or on a track without strings
  its pitch — **on the same staff, in the same voice of that staff**, in the beat before, the last
  beat of the previous measure when it opens a measure; never a note of another voice or staff.
  The reader keeps it as written and guesses nothing.
- A chord is its notes in parentheses: `(A2@5 E3@4 A3@3).4`. A rest is `r`: `r.2`.
- **The fret has no ceiling**: a fret is the pitch less the open string and the capo, however high
  (some guitars have 27 or 30), and is kept as written. A note written without `@` is placed on the
  neck first — frets up to the track's last (`frets`, 24 by default), counted from the capo —, past it only when nothing else holds, on any
  string at or under its pitch; it is refused only when it is lower than every open string. **Refused, by name, on a track with
  strings**: a note lower than its open string — a fret under zero —, whether written `pitch@n` or
  `fret.string`.
- **Two notes may strike one string at an instant**, in one beat or two voices, as MuseScore and Guitar Pro read them: each is read and written back on its string, a reader showing the clash (Cesure draws both in red and plays both). A writer should not make one: a string strikes one note at a time. A tied note `t` that prolongs the note before it on its string is no strike; a tie with nothing to prolong strikes.
- **Every refusal names where it is**: the track, the measure (its id, else its rank), the staff,
  the voice and the token it could not take — and down to what it concerns when it is no note: a
  staff, a measure, a track or its tuning, a tempo or key change by its rank and measure, a repeat
  by its measure, the document.
- **Properties go where they apply, and the place decides**: braces right after a note are the
  note's (`E5@1{v}.4`, a vibrato on that note); braces after the duration are the beat's
  (`E5@1.4{d}`, a dotted quarter). In a chord, each note carries its own: `(E5@1{v} B4@2).4{d}`.
- **Tuplets**: every beat of the group carries the property, and the group declares its edges, as
  MusicXML's `<tuplet type="start|stop" number="n">`: `start n` on its first beat, `stop n` on its last
  (both on a group of one beat). `E5@1.8{tu 3 start 1} F#5@1.8{tu 3} G5@1.8{tu 3 stop 1}` is three
  triplet eighths, the time of one quarter; `E5@1.4{tu 3 start 1} F#5@1.8{tu 3 stop 1}` a triplet
  quarter and eighth, one group. A beat's length is its value × `m` / `n` for `tu (n m)`. A run of
  tuplet beats that declares no edge is grouped as version 3 grouped it: the beats of one tuplet in a
  row, cut at its count. A `start` or `stop` a reader cannot read (`start 0`, a second `start` on a
  beat, one on a beat out of a tuplet) is kept on its beat and written back.
- **Nested tuplets**: a beat in a group nested in another carries every `tu` it is in, the widest first,
  each followed by the edges of its own group: `C4.8{tu 3 start 1} D4.16{tu 3 tu 3 start 2}
  E4.16{tu 3 tu 3} F4.16{tu 3 tu 3 stop 2} G4.8{tu 3 stop 1}` is a triplet of eighths whose middle
  eighth is a triplet of sixteenths. A beat's length is its value times the ratio of every `tu` it carries;
  nested groups declare distinct numbers, as MusicXML's.

| Beat property | Meaning |
|---|---|
| `d` | Dotted: the duration × 1.5. |
| `dd` | Double-dotted: the duration × 1.75. Written alone, never with `d`; a beat that carries both is double-dotted. |
| `tu 3` | Triplet: three beats in the time of two of the same value. |
| `tu (n m)` | Tuplet: *n* beats in the time of *m* — `tu (5 4)` a quintuplet; *n* from 2 to 32, *m* from 1 to 32, any other refused by name. |
| `start n`, `stop n` | Beside `tu`: the first and the last beat of tuplet group *n* (from 1). Every group a writer writes declares both. Each follows the `tu` of its group: `{tu 3 tu 3 start 2}` opens the inner one. |
| `tt` | Every note of the beat is tapped. |
| `hide` | On a rest: a rest the source does not print (MusicXML `print-object="no"`, LilyPond's `s`, an invisible rest of MuseScore). It keeps the time of its voice, sounds nothing and is never drawn: `r.2{hide}`. A reader that does not know it keeps it on its beat and writes it back. |
| `measure` | On each rest of a voice that is one measure rest, MuseScore's: the rest lasts its measure, whatever the signature. Written as the rests its length takes, the fewest, the longest first, each marked: `r.2{d measure}` in 3/4, `r.1{measure} r.4{measure}` in 5/4. Read as one measure rest only when every rest of the voice carries it and they are exactly that split of the measure; otherwise as written, each mark kept on its beat — a note since entered there included — and written back. A reader that does not know it plays the rests as written, to the quarter. |
| `fermata`, `fermata shape`, `fermata (shape stretch)` | A fermata over the beat, note or rest. *shape* is one of `veryshort`, `short`, `shorthenze`, `normal` (the default, written as `fermata` alone), `long`, `longhenze`, `verylong` — SMuFL's and LilyPond's seven. Playback holds the beat as MuseScore does: from its start to the next beat any voice of any track starts, the tempo divided by its *stretch* — by default 1.25 (very short), 1.5 (short, short Henze), 2 (normal), 3 (long, long Henze), 4 (very long). A stated *stretch*, from 1 to 5, replaces the shape's: `E4@1.2{fermata (long 3.5)}`. alphaTab's `fermata short\|medium\|long` is read too, its second value Guitar Pro's length. Values a reader cannot read (`{fermata zz}`, `{fermata (long 2 3)}`) are kept as this fermata's, written back where they were, and the beat shows and plays a normal fermata until the user chooses one. |
| `beam up`, `beam down` | The beat's stem is forced up or down, as alphaTab writes it (MusicXML's `<stem>`, MuseScore's stem direction of a chord). Absent, the stem takes its voice's side: with several voices on the staff the first and third up, the second and fourth down; a voice alone chooses by the middle line. Written only where it differs from that side; a beamed group with no voice side takes the side of the first of its chords forced to one; chords forced both ways make a knee. alphaTab's other `beam` values (`invert`, `auto`…) are kept on their beat and written back. It never changes what sounds. |
| `beam split`, `beam merge`, `beam splitsecondary` | How the beat is beamed to the next one of its voice, as alphaTab writes it (MusicXML's `<beam>`, MuseScore's beam mode of a chord): `split` stops the beam after it, `merge` carries it on to the next beat — over a rest, past a beat of the meter —, `splitsecondary` stops its beam lines past the first where the beam goes on. Absent, beats are grouped by the meter: flagged notes in one quarter, or one dotted quarter of a compound meter. Written only where it differs from that grouping; a beam stops at the bar line. A beat may hold both a side and a beaming: `{beam up beam merge}`. It never changes what sounds. |
| `clef name` | The staff changes to clef *name* (a staff's `clef` name: `treble`, `alto`, `bass8vb`…) right before this beat, until the end of the measure: `E4.4{clef treble}`. A change at the start of a measure is the staff's `clef`, not this property. Written on one beat of the staff struck at that instant, the first voice's when it has one there. A value a reader cannot read — a name it does not know, a number, two names (`{clef treble bass}`) — is kept as this clef's, written back where it was, and the staff keeps the clef it is in until the user chooses one; `{clef}`, without a value, is refused. It never changes what sounds. |
| `ot (8va start n)`, `ot (8va stop n)` | An octave line of its staff, `8va`, `8vb`, `15ma` or `15mb` (MusicXML's `<octave-shift type number size>`, MuseScore's `Ottava`): it opens where the beat that writes `start n` starts and closes where the beat that writes `stop n` ends, a number from 1 telling it from a line it overlaps; a line of one beat writes `ot (8va start 1 stop 1)`. Every voice of the staff between is under it, and writes nothing. Its heads are written one or two octaves under (`8va`, `15ma`) or over (`8vb`, `15mb`) the pitch they sound, which stays the note's: it never changes what sounds. On a piano, a beat whose notes are all of one hand stands under the lines of that hand's staff. A `start` never stopped runs to the next `start` of its number, else to the end; a `stop` never started is a line of its beat alone. Any other form is kept on its beat and written back. A bare `ot 8va`, version 3's, is read as version 3 drew it: beats so marked in a row are one line. |

| Note property | Meaning |
|---|---|
| `h` | Hammer-on or pull-off **to the next note on the same string** (which one follows from the pitches). |
| `sl` | Slide to the next note on the same string. |
| `be (offset value …)` | Bend, as alphaTab and Guitar Pro hold one: its points, each an *offset* along the note from 0 (its start) to 60 (its end), rising from one point to the next, and a *value* in quarter tones above the pitch struck, from -12 to 12 (`4` is a whole tone). Between two points the pitch moves in a straight line; past the last it holds. A bend, a release, a pre-bend are read from the points: `be (0 0 15 4 60 4)` a whole-tone bend in the first quarter of the note, then held; `be (0 0 15 4 30 4 45 0 60 0)` a bend and release; `be (0 4 60 4)` a pre-bend; `be (0 4 15 4 30 0 60 0)` a pre-bend and release. Any other shape is an error. The pitch is the one struck, before the bend. |
| `b (0 n)` | The bend version 2 wrote, read and never written: Guitar Pro's bend to *n* quarter tones, `be (0 0 15 n 60 n)`. Any other shape (`b (0 4 0)`, `b (2 4)`) is an error. |
| `v` | Vibrato. |
| `lht` | Tapped note. |
| `t` | Tied to the note it continues (see above). |
| `tw` | On the note a tie leaves: the tie waits for the next note of its line (its string, or its pitch without one) in its voice, past the beats between, rests included — LilyPond's `tieWaitForNote`, an arpeggio held into its chord. That note, marked `t`, is not struck again. Written only where a beat stands between the two. |
| `g` | Ghost note: played very softly (Cesure strikes it at half the loudness of the same note played full) and drawn in parentheses. A tied note is as soft as the note it continues. |
| `lr` | Let ring: the note sounds on past its written length, as alphaTab plays it — through the next beats of its voice, across the barline, until one rests or, on a string, plays its string, never longer than its measure lasts. Its written duration does not change. A tied note rings as the note it continues; a muted note never does. |
| `ba n` | Version 2's bend height of *n* semitones kept on a note whose bend was taken off. Read, and dropped: no bend is played, and it is not written back. |
| `kept "…"` | Everything a reader keeps on that beat or note and has no property for — the keys of a version 1 file, a technique or a hand it cannot name — as percent-encoded JSON. Write it back as it is. |
| `nh n` | Natural harmonic: the open string touched at fret *n* (12 an octave up, 7 and 19 an octave and a fifth, 5 and 24 two octaves): the pitch, which is the one the harmonic rings, does not say where. `nh` alone is read as `nh 12`; on a note written `fret.string`, as alphaTab reads it, at its own fret. |
| `ah n`, `th n`, `ph n`, `sh n`, `fh n` | Artificial, tapped, pinched, semi and feedback harmonic: the node touched *n* frets above the fretted note, a whole number (`ah 12` an octave up, `ah 7` an octave and a fifth); `ah` alone is `ah 0`. The pitch written is the one it rings; the pitch a node rings is alphaTab's. |
| `hand A` / `hand B` | The note is set to the low (`A`) or high (`B`) hand of a two-hand part. Absent = derived by the reader, not stored: the simplest rule puts a note below a split point in `A` (Cesure's default is middle C, C4); Cesure also offers the most playable hand, worked out over the whole track. The rule and its split point are reader preferences, never part of the file, and a written hand always wins over them. Not written on a piano's staves, which say the hand. |

Examples: `C4@3.4` (fret 5 on string 3 of a standard guitar, a quarter); `(G2@6 B2@5 D3@4).2{d}`
(a dotted half chord); `F#4@2{be (0 0 15 2 60 2)}.8` (fret 7 on string 2, a half-tone bend, an eighth); `x@6.16` (a muted string);
`E5@1{nh 12}.4` (the octave harmonic of the open high E).

### Reserved forms

These forms are part of the grammar so that they can be added later without a new version. A
reader that does not represent them keeps them as written (see below); Cesure writes none today.

| Form | Meaning |
|---|---|
| `{lyrics "text"}` on a beat | The syllable sung on that beat. |
| `{ch "Am7"}` on a beat | The chord symbol shown above that beat. |
| `{mt n}` on a note | The note sounds *n* cents (a whole number, signed) away from its named pitch: `C4{mt 50}` a quarter tone above C4. A reader that does not represent it keeps it and plays the named pitch; a value that is not a whole number is refused. |

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
  `tempo`) — and a note in a reserved form the reader does not represent stays on its beat. A
  property written on a beat stays the beat's, never copied onto its notes;
- **a property delimits its own values**, as alphaTab reads one: its values in parentheses
  (`{tu (5 4)}`, `{be (0 0 15 4)}`, `{zz (1 2)}`), or one bare value (`{tu 3}`, `{zz 1}`,
  `{zz "x"}`), so that a reader keeps a property it does not know without guessing how many values
  it has. A writer puts the values of a property in parentheses whenever it has more than one. A
  property this specification names with several values is still read bare, as alphaTab reads it
  (`{tu 5 4}`); any other takes one bare value at most, and a value standing after it (`{zz 1 2}`) is
  refused. A bare value is a number or a text, or a name where the property takes one: a property's
  name is never a value (`b` after `hand` excepted); a name the property does not know (`zz`) is its
  value only when no value follows it, a name followed by values being the next property, known or
  not. `{tu 3 zz 1}` is a triplet and the unknown property `zz 1`, `{dy zz 1}` the dynamic `dy` and
  `zz 1`. Written alone and last, `zz` is the value of a property that takes a name in that place
  (`{fermata zz}`); a writer puts that property's values in parentheses before such a name
  (`{fermata () zz}`). Version 3's measures are read in version 3's grammar, where an unknown property
  took every bare number and text after it, and written in this one (`{zz 1 2}` becomes `{zz (1 2)}`);
- an unknown value of a known property (`fermata`, `clef`, `hand`) is kept as that property's value,
  written back in its place, and shown as the property's default until the user sets it;
- the keys a beat's tuplet keeps go into that beat's `kept`, under `tuplet`, where version 1 wrote
  the tuplet; they never part one group from another;
- a reader that shows fewer staves or voices than a measure holds keeps the others with their
  measure, and writes them back;
- an unknown value of a field is kept and written back: `instrument`, an open vocabulary, until the
  track is given another instrument; `hand`, until the user sets it;
- a value of a closed list a reader does not name — a key's `mode`, a `barLineRight`, a
  `barNumberDisplay`, a `meter`, a direction, a clef, a `hideWhenEmpty`, an octave line, a stem or a
  beam — is kept, shown as the default, and written back as written: the file is never refused for it.
  Only what would not sound right is: a duration, a pitch.

A field of the skeleton written with another type than this specification gives it — a list as
text, an object as a list, a voice as a number, a repeat's `start` that is not `true` or `false` —
is refused, naming where it is: it is never read as empty. Absent, a field keeps its default, and one
this version requires is completed ([File structure](#file-structure)); a staff without its `voices`,
which no rule completes, is refused.

What cannot be kept is refused: an unknown **duration**, an unknown pitch class in a tuning, or a
beat or note the grammar cannot read, or a document whose JSON nests more than 64 levels deep. The
reader then refuses the file by naming what it could not read — guessing would change the rhythm or
the tuning.

This is what lets one account use an older and a newer build at once, and an agent add what a
build does not know yet, without either ever silently losing a part of the piece.

## For agents: working on a range of measures

- **Name measures by id.** A range is a list of ids, or a first and a last id; it survives edits
  elsewhere in the piece, where measure numbers do not.
- **Replace a range as a whole**, as the file writes it: its measures of the piece (`measures`, each its id,
  time signature, marks and `repeat`) and, for every track, its measures in them (staves, voices, chords),
  measure i of a track in measure i of the piece. A time signature goes on the measure of the piece: on a
  track's measure it is that track's own (reserved, never played). Keep the ids of the measures you keep;
  leave out the id of a measure you insert — the reader gives it one — and never reuse an id for another
  measure.
- **Each measure stands alone**: its durations are all written, and its voices should fill its
  time signature. A tempo change or a repeat named by the id of a measure you keep stays on it.
- **The revision is not in the file.** Whoever stores the file keeps a revision number beside it;
  an agent says which revision it read when it writes, and a write over a newer revision is
  refused, so that nobody overwrites what they have not seen.
- **Write a note by its pitch**, and on a track with strings its string (`E4@1`): never a fret.
  A note written `fret.string` is still read, and written back as a pitch.
- **Validate the skeleton** with [the JSON Schema](schema/v4.json) before writing; the notation is
  checked by the reader, which names the beat it cannot read.

## Transport

A `.cesure` file is plain text that compresses about five times over: a server **should**
compress it in transit (`Content-Encoding: gzip` or `br`), and a client should accept it so. The
file itself is never compressed.

## Versioning policy

| Change | Action |
|---|---|
| A field with a default, a beat or note property, a [reserved form](#reserved-forms) put to use | No new version: a reader that does not know it keeps it |
| An instrument sound id (an open vocabulary), a value added to an optional enum | No new version: kept by a reader that cannot name it |
| Anything new that changes what is heard or read — a duration, a pitch class, a field or form a reader that ignores it would play or show otherwise (a [local time signature](#trackmeasure)) | No new version: its name goes into the root's `requires`, and a reader that does not know it refuses the file as a newer one |
| A removed, renamed or retyped field, a field whose absence changes meaning | New version, with a migration from every older one |

A pitch between the semitones — a quarter tone — is the reserved note property `mt`, not a new
pitch class: it needs no new version.

The durations of version 2 go down to the sixty-fourth (`64`): version 1 stopped at the
thirty-second. Version 4 adds the breve (`-2`), the hundred-twenty-eighth (`128`) and the
two-hundred-fifty-sixth (`256`): a file of an older version that writes one is refused, as it was. A
duration added after them goes into `requires`. The tempo became a number within version 2: every file read before reads the same,
and a reader that still takes it as an integer refuses only a file whose tempo is not whole.

A reader **refuses** a file whose `version` is above the ones it reads, or whose `requires` names
what it does not know, rather than misread it, and proposes the update: an application that reads up
to version 3 refuses a version 4 file so.
Version 3, 2 and 1 files ([v3.md](v3.md), [v2.md](v2.md), [v1.md](v1.md)) are read forever and
migrated in memory ([Reading version 3](#reading-version-3), [Reading version 2](#reading-version-2));
nothing writes them.
A key that a version 1 file held on a beat or a note, unknown to the reader, is kept: saved in
version 2 or later, it goes into the `kept` property of that beat or note, its name and value unchanged —
a name opening with `{` included: read back, a key of `kept` is kept exactly as the same key of the
file would be. A `kept` whose value is not percent-encoded JSON (`%+1`, `%FF` alone, a value that
is not an object) is an error, named by the reader. A key that a version 1 file held on another
object keeps its name the same way, including a name version 2 gives a field of that object
(`measure` on a tempo change, `staves` on a measure, `repeats` on the score): it is written
`{measure`, and read back as the key `measure`, never as the field. A version 1 file escaped
nothing and is read as written: its key `{repeats` is the key `{repeats`, saved as `{{repeats`.

## Reading version 3

A version 3 file says the same once read, note for note: version 4 writes its body as version 3 did,
and declares on each track what version 3 left to be deduced. Migrated in memory as it is read:

- a track without `instrument` is written as the app takes it, as it sounded: a guitar with a
  `tuning`, else a piano on treble staves, never the grand staff (drawn as it was); `GUITAR`,
  `BASS`, `PIANO` and `DRUMS` are `pluck.guitar`, `pluck.bass`, `keyboard.piano` and
  `drum.group.set`, written as the sound of the track's program in that family
  (`pluck.guitar.nylon-string` for program `24`);
- a track without `program` sounds its instrument's, written; one without `name` is `Guitar`; its
  `staves` are the ones it is drawn on, each with the clef it opens on where none is written;
- a tuning without `frets` has 24; a track or a measure without an id gets the one the reader
  derives, as below; an opening without `uncounted` counts as the rule of version 3 implies;
- what each track's measure *i* said of the measure — its id, time signature, irregular mark, count,
  bar line, printed time signature, hidden number, meter — and the `repeats` by id become measure *i*
  of the piece's `measures`, written once. Where tracks disagree, the measure is the first track's
  holding it — the one Cesure has always laid out, numbered and barred the measure by —, and each
  other track keeps its own value of a mark on its measure, written back and never read: nothing is
  lost, and the measure of the piece is one;
- a key name (`"Bb"`, `"F#m"`) is the [Key](#key) of that signature and mode; a score without `key`
  states none, and stays so: its key is found from its notes at each opening, as in version 4.

## Reading version 2

A version 2 file says the same once read: every note sounds the same pitch, at the same instant,
for the same time, and on a track that keeps its strings, on the same string at the same fret —
save a track marked `PIANO` (below). It is migrated in memory, as it is read, and never written
again:

- a note `fret.string` is the pitch that place sounds, named as the key in force in its measure
  names it (the stated key, else the one found from the notes), on that string; a natural harmonic
  is touched at its fret, `nh` becoming `nh n`; a note version 2 wrote by its pitch keeps its name;
- `tuning` absent is the standard guitar, written out in full (`["E4","B3","G3","D3","A2","E2"]`),
  and an open string a `{"note":"E","octave":4}` object;
- **a `PIANO` track with no `tuning` written is a guitar**: there, `PIANO` was only the sound a track
  played and every track a tablature — it keeps its six strings, its frets and its capo (version 1
  alike);
- **a `PIANO` track that writes its `tuning` becomes a piano without strings**: its notes keep their pitches — a capo is in
  them —, lose their strings, and the hand each one showed becomes the staff it is written on:
  `hand B` the right hand (`staves[0]`), `hand A` the left (`staves[1]`); a note without one goes to
  the right hand from middle C (C4) up, else to the left — version 2's default rule, frozen for the
  migration; a tie takes the hand of the note it continues;
- **two notes struck on one string at an instant** (in one voice or two, versions 1 and 2 alike)
  stay as written, each on its string at its fret, as in a version 3 file;
- a bend `b (0 n)` is Guitar Pro's bend to *n* quarter tones, `be (0 0 15 n 60 n)` — from the pitch
  struck to its height in the first quarter of the note, then held; a `ba n` reads and is dropped;
- everything else reads as in version 2: `kept`, unknown keys, reserved forms.

Two notes have no pitch to give: a note on a string past the tuning of its track, and a muted note
on a piano. Each is kept on its beat as written (`3.7`, `x.6`), silent as it was, and written back
so — on a piano on the staff of the `hand` it carried (`hand A`: the left), without that hand, which
its staff says, and two of them may share a string there: a piano has no strings. On a track with
strings, what is kept so stays as written too. A note written by its pitch alone is placed, on
a string no voice takes at that instant, with all of them at once, and the file refused, naming it,
when none is left. On a piano laid on strings, the voices of every staff, its first's then the next
ones', are its notes: the first two voices split between the hands as version 1's beats, each later
voice's notes going, each without its `hand`, to a voice of its own on the staff of their hand (by the
default rule when none is written). What goes is said.
Cesure's own corpus holds none.

## JSON Schema

[`schema/v4.json`](schema/v4.json) (JSON Schema Draft 2020-12), served at
`https://cesure.app/format/schema/v4.json`, describes the skeleton; the version 3, 2 and 1
schemas stay at [`schema/v3.json`](schema/v3.json), [`schema/v2.json`](schema/v2.json) and
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
- [`examples/piano.cesure`](examples/piano.cesure) — a piano on two staves, a pickup, and a
  guitar beside it
- [`examples/v3/`](examples/v3/), [`examples/v2/`](examples/v2/) and [`examples/v1/`](examples/v1/) —
  the version 3, 2 and 1 examples, as they were

## Maintenance

The format is developed and regression-tested inside the Cesure application; this section documents
**how it stays stable** (the tooling lives in the app repository, not here).

**A `.cesure` file that a user saved must open identically forever.** Before changing the model or
the notation:

1. **Additive** (a field with a default, a property, a reserved form put to use) → no new version;
   one that changes what is heard or read names itself in `requires`. Update this README,
   `schema/v4.json` and `CHANGELOG.md`, and add the addition to a file of the corpus so that it is
   actually exercised.
2. **Structural** (see the table above) → raise `CURRENT_VERSION` in `CesureSerializer`, add the
   migration, and keep a frozen file of every older version: it must still load.
3. **Never edit a frozen file to make a test pass**: an old file that no longer reads the same is
   the bug.
4. **Run the guards** — all in `:music:score`: `./gradlew :music:score:jvmTest`. They hold the schema against
   the model, the round trip of every example and catalog piece, the frozen v1, v2 and v3 corpus — each
   v2 file saying, note for note, what it said —, the refusal
   of a newer version, and the keeping of unknown keys, properties and values.

## The application behind the format

`.cesure` is written and read by **[Cesure](https://cesure.app)** — a guitar tablature editor and
practice toolkit that runs [in the browser](https://cesure.app), on Android and on iOS. It imports
Guitar Pro, MusicXML, MIDI and AlphaTex, transcribes audio to tablature, and plays scores back with
a tuner, a metronome and a piano roll. The schema in this repository is checked against its model
on every build, so a field added on one side and not the other fails the build.

## License

This specification is released under the [MIT License](LICENSE).
