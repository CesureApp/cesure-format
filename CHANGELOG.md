# Changelog

Additive fields (a new field with a default) are **backward-compatible** and do **not** bump the
version — old files still load, new files still open in older builds (unknown keys are ignored).
They are listed under v1 with the date they were added.

## v4

Written by Cesure from 2026-11-19 on; every reader keeps reading v3 ([v3.md](v3.md)), v2 and v1,
migrated as they are read ([Reading version 3](README.md#reading-version-3)).

- **Every track declares what version 3 left to be deduced**, always written: its `id`, its `name`,
  its `instrument`, its `program`, its `staves` and, beside a `tuning`, its `frets`; every measure of the piece its `id`,
  and the first its `uncounted`. A file that lacks one is never refused: a reader completes it by
  the rule an older version reads it with (the instrument by the strings, the program by the family, an id
  drawn, the default name, 24 frets…). A reader refuses only what it cannot play right.
- **`requires`**, at the root, as glTF's `extensionsRequired`: the names of what a reader must know to read
  the file right. A reader that does not know one refuses the file as a newer one. Empty in every file of
  this version, and not written then. It is the one way an addition that changes what is heard or read
  comes in — a duration or a pitch class included —: such an addition is no new version.
- **A local time signature is reserved**: `numerator` and `denominator` on a track's measure are that
  track's own time signature there (MusicXML's polymeter, MuseScore's local time signature). This
  version plays every track in the measure's, and keeps the track's, written back; a file that asks for
  it to be played will name `localTimeSignature` in `requires`.
- **A property delimits its own values**, as alphaTab reads one: in parentheses, or one bare value. A property a
  reader does not know is kept without its values being guessed: `{zz 1 2}`, read in version 3 as `zz` and two
  values, is refused in this version, which writes `{zz (1 2)}`. A version 3 file's measures are read in their
  grammar, and written in this one.
- **A value of a closed list a reader does not name is kept**, shown as the default and written back as
  written, never a refusal of the file: `barLineRight`, `barNumberDisplay`, `meter`, a direction (at its place), as a
  key's `mode`, a clef, a `hideWhenEmpty`, an octave line or a beam already were. The schema leaves those
  lists open. A duration or a pitch a reader does not name is still refused: it would not sound right.
- **A sound that contradicts its track is kept, and one rule says what the track is**: the type its staves
  declare first (`percussion` a kit, any other a track of pitches, a note of the other kind refused), else the
  notes (all hits a kit, pitches never one), then the sound's family, then the strings. The `instrument`, `program`
  and `tuning` are written back as declared — a kit's program included —, never dropped. A drum kit never
  holds strings, whatever the version of its file: a `tuning`, `capo` and `frets` declared on one are kept and written back, playing nothing.
- **`instrument` is an instrument sound id of MusicXML**, an open vocabulary (`pluck.guitar.nylon-string`,
  `keyboard.piano.grand`, `strings.violin`…): a reader handles `keyboard.piano`, `pluck.guitar`,
  `pluck.bass` and `drum.group.set` by their prefix, keeps any other id and sounds the track's
  `program`. A track whose source named no instrument is written as the app takes it: a guitar on
  strings, else a piano on staves that say it is no grand staff. Version 3's `GUITAR`, `BASS`, `PIANO` and `DRUMS`, and a track
  without one, are migrated.
- **`staves`, the staves a track is drawn on**, each with its clef and its `type` (`pitched`, `tablature`,
  `percussion`, MuseScore's staff type groups: what the track is, never a view; an unknown name kept), as MusicXML's `<staves>` and
  `<clef number>`: a measure holding more is refused; a `keyboard.piano` without a tuning is the grand
  staff only on treble over bass, any other a part its source named no instrument for. A staff
  declared past those a measure holds is drawn, and each staff in the clef it declares; a change of
  instrument gives the track the new instrument's staves and sound.
- **The words of version 3** (`PIANO`, `GUITAR`, `BASS`, `DRUMS`, any case) written as a version 4
  `instrument` are read as their family's sound.
- **A key of the root is kept**, beside `version` and `score`, and written back.
- **The measures of the piece are written once, for every track**, in the score's `measures`, as
  MuseScore's `<Measure>`: each its `id`, time signature, irregular mark, count, bar line, printed time
  signature, hidden number, meter and `repeat` (version 3's `repeats`, keyed by id, are gone). A track's
  measure holds its content alone, measure *i* of the piece at its place: no two tracks can disagree on
  a time signature. A version 1 to 3 file whose tracks disagree reads as its first track; another
  track's own value of a mark is kept on its measure and written back, never read.
- **The key is `{fifths, mode}`**, MusicXML's `<key>`, on the score and on each key change. It is
  always written: a piece no source states one for writes the signature its notes give and `none`,
  found once and never again — a file no longer changes from one build to the next. A reader shows a
  key of no mode in the mode it finds for that signature, a suggestion it never writes.
  `mode` is one of MusicXML's, `none` included; a mode a reader does not know is read as `none` and a
  signature past seven accidentals as none, kept and written back, never a damaged file; a `fifths` left
  out reads as `0`, a `mode` as `none`, and a key change without its `key` as `{}`.
- **A `measure` mark that makes no measure rest is kept** on its rest and written back (version 3
  dropped it).
- **A tuplet group declares its edges**, `start n` on its first beat and `stop n` on its last, beside
  `tu`, as MusicXML's `<tuplet type number>`: a group holds the beats between, whatever their values (a
  triplet quarter and eighth is one group). Version 3 grouped a run of tuplet beats by its count; its
  files declare those same groups as they are read, and a version 4 run that declares none is grouped
  the same way. An edge a reader cannot read is kept on its beat and written back.
- **An octave line is a stretch of time of its staff**, `ot (8va start n)` on the beat it opens on and
  `ot (8va stop n)` on the beat it closes on, nothing between, as MusicXML's `<octave-shift type number>`:
  two lines in a row stay two. Version 3 wrote `ot 8va` on every beat under it; its files declare the
  line each run drew, as they are read: the same heads, the same lines, the same sound. A start never
  stopped, or a stop never started, is completed, never refused.
- **Tuplets nest**: a beat carries every `tu` it is in, the widest first, each with the edges of its own
  group (`{tu 3 tu 3 start 2}`); it lasts its value times every ratio. Version 3 read a second `tu` as
  replacing the first.
- **Three durations**: the breve `-2` (alphaTab's value), the hundred-twenty-eighth `128` and the
  two-hundred-fifty-sixth `256`, MusicXML's `breve`, `128th` and `256th`. A reader reads, plays, draws and
  writes them back; versions 1 to 3 never named them, and a file of theirs that writes one is refused.

## v3

Written by Cesure from 2026-11 to 2026-11-19; every reader keeps reading v2 ([v2.md](v2.md)) and v1, migrated
as they are read ([Reading version 2](README.md#reading-version-2)).

- **A track may say the frets of its neck** (2026-11-19, no new version: an older reader keeps
  `frets` with its track and writes it back), as MuseScore's `<StringData><frets>` and Guitar Pro's:
  `1`..`127`, 24 when absent, only beside a `tuning`. A capo sits under the last fret: a file whose capo
  is not (capo `24`, written before `frets`) opens on a neck that reaches the fret past it. A note past
  the last fret is kept on its string, played as written and drawn out of the neck. A pitch is at most
  `G9` (MIDI 127): a note past it was always an error of the notation, and is one of every reader.
- **What follows a property's values is read as a property** (2026-11-19, no new version): every
  property declares the bare values it takes, and a name it does not know is its value only when no
  value follows it, so that a property a reader does not know, written with values after one it
  knows, is kept as a property: `{tu 3 zz 1}`, `{gr zz 1}`, `{tempo 120 zz 1 2}`. `kept`, `measure`
  and `ba` are never values. Before, `{tu 3 kept "…"}` was read as a tuplet of a broken value and
  refused. A value a reader cannot read of `fermata` or `clef` is kept as that property's, written
  back in its place, until the user chooses (`{clef treble bass}`, refused before, is kept). A
  property written on a beat stays the beat's: one a reader does not know is no longer copied onto
  each of its notes next to a harmonic or a tie. The keys of a tuplet are kept in the beat's
  `kept`, under `tuplet`, and never part one group from another.
- **A track may carry an `id`** (2026-11-18, no new version: every version reads it, so the schemas
  of versions 1 and 2 list it too, and an older reader keeps it with its track and writes it back), as
  MusicXML's `<score-part id>`: what tells it from the others whatever its place, so that what a person
  chose for a track stays with it. A track written without one is given one the reader derives from
  what it holds, never from its place ([Track ids](README.md#track-ids)).
- **A note is its pitch, named as written**: `D#5` and `Eb5` are two notes, and the name is kept.
  On a track with strings `@n` says the string (`E4@1`); **the fret is never written** — it follows
  from the pitch, the string, the tuning and the capo. A muted string is `x@6`. `fret.string` is
  still read, on input only, and written back as a pitch.
- **`tuning` absent means no strings** (a piano, a voice); present, it lists the open strings as
  pitches, `["E4","B3","G3","D3","A2","E2"]`. `capo` only with a tuning.
- **A piano is one track on two staves**: `staves[0]` the right hand, `staves[1]` the left, each of
  up to four voices in rhythms of their own, read and written back as they are (2026-11-01: a hand
  may play two rhythms while the other plays); a staff may say its `clef`. `hand` is not written on
  a piano's staves.
- **A track holds as many staves as it has, each of one to four voices** (2026-11-02, no new
  version: the syntax held them already): every staff of a track and every voice of a staff is read,
  played, drawn and written back as a staff or a voice — none kept as text past those Cesure showed
  —, the first and third voices stemmed up, the second and fourth down. A staff of five voices or
  more is refused where the file enters, naming the measure, the track and the staff; an import
  merges the voices past the fourth into it and says so.
- **A tempo lies in 4 to 999 quarter notes per minute** (2026-11-13, no new version: the range only
  widens, every file that was valid still is): a tempo, or a tempo change above 0, outside it makes a
  reader refuse the file, naming the range, instead of playing the nearest bound; `0` as the initial
  tempo, which no writer is to write, reads as none, and the piece takes 120.
- **A measure carries its signs and jumps** (2026-11-13, no new version: an unknown key of a repeat
  is kept): `directions` on a repeat — segno, coda, Fine, D.C., D.S., al Coda, al Fine, To Coda,
  the nineteen of Guitar Pro —, engraved and followed by playback; and `section` on a repeat, the
  measure that opens a section (a movement), whose repeats and jumps are played on their own.
- **A measure may carry chord symbols** (2026-11-13, no new version: an unknown key is kept with its
  object): `"chords": [{"chord": "C"}, {"at": 2, "chord": "G/B"}]`, each at its instant in quarter
  notes, a beat struck there or not, as MuseScore places a chord symbol. An older reader keeps the key
  with its measure and writes it back, as written: one that transposes the score leaves it unmoved.
- **A rest may be a measure rest** (2026-11-17, no new version: an unknown beat property is kept),
  MuseScore's: one rest alone in its voice that lasts its measure, whatever the signature. It is
  written as the rests its length takes, each marked `{measure}` — `r.2{d measure}` in 3/4,
  `r.1{measure} r.4{measure}` in 5/4 —, the values a reader that does not know the mark plays as
  written, to the quarter. A reader reads them as one measure rest only when every rest of the voice
  is marked and they are exactly that split of its measure; otherwise as written, the mark dropped.
- **A rest may be hidden** (2026-11-07, no new version: an unknown beat property is kept): `{hide}`
  on a rest, never drawn, as MusicXML's `print-object="no"` — a voice of hidden rests alone past
  the first is no voice.
- **A voice of rests the source prints is a voice** (2026-11-08): past the first, only a voice of
  hidden rests alone is none.
- **An older track marked `PIANO` with no `tuning` is a guitar** (2026-11-08): in versions 1 and 2
  `PIANO` was only its sound, and every track a tablature; it is read on its six strings, frets and
  capo kept. One that writes its `tuning` is read a piano without strings.
- **A tempo change falls on a beat**: `{"measure": "m3", "at": 1.5, "tempo": 90}`, `at` the quarter
  notes from the start of its measure, absent at its start, as MuseScore places a tempo text. A
  version 2 file's changes stand at the start of their measure, as they always did. A tempo goes
  down to 4 quarters a minute, the slowest MIDI writes: a fermata held on a slow tempo is one.
- **A beat may say how it is beamed to the next** (2026-11-09, no new version: an unknown beat
  property is kept): `{beam split}`, `{beam merge}`, `{beam splitsecondary}`, alphaTab's syntax,
  written only where it differs from the grouping by the meter.
- **A beat may force its stem's side** (2026-11-09, no new version: an unknown beat property is
  kept): `{beam up}`, `{beam down}`, alphaTab's syntax, written only where it differs from the side
  its voice takes by itself.
- **A staff may hide where it is empty** (2026-11-10, no new version: additive fields), as
  MuseScore's "Hide when empty": `Track.hideWhenEmpty`, one of `auto` (as `Score.hideEmptyStaves`
  says), `always`, `never`, `instrument` (with the whole track, LilyPond's PianoStaff under
  `\RemoveEmptyStaves`) per staff, `Score.hideEmptyStaves`, and `Score.hideEmptyStavesInFirstSystem`,
  the first system too. Absent, every staff is drawn everywhere; a file without them is written as
  before, byte for byte.
- **A beat may bear a fermata** (2026-11-07, no new version: an unknown beat property is kept):
  `{fermata}`, `{fermata long}`, `{fermata (long 3.5)}` — seven shapes, and a stretch only where it
  differs from its shape's; playback holds the beat by it.
- **A tie may wait for its note** (2026-11-10, no new version: older builds keep `tw` as an unknown
  property but drop the tie it makes, striking the note it reaches again): `{tw}` on the note a tie
  leaves, its `{t}` note further on in its voice, as LilyPond's `tieWaitForNote`.
- **A note may be let ring** (2026-11-10, no new version: an unknown note property was dropped by
  older builds, which lose it when they write the file again): `{lr}`, alphaTab's let ring. The note
  sounds on past its length; its written duration does not change.
- **A natural harmonic says where it is touched**: `nh n`, `nh` alone read as `nh 12`; its pitch
  does not say it (7 and 19 ring alike).
- **A bend is its points**, as Guitar Pro and alphaTab hold one: `be (offset value …)`, each offset
  from 0 to 60 along the note, each value in quarter tones. A bend and release, a pre-bend, a
  pre-bend and release, a quarter-tone bend are written as they are (2026-11-13, before any
  released build wrote version 3). Version 2's `b (0 n)` reads as Guitar Pro's bend to *n* quarter tones,
  `be (0 0 15 n 60 n)`; its `ba n` reads and is dropped.
- **One meaning or a refusal**: a tie prolongs the note of its pitch on its staff, in its voice; a
  note lower than its open string (a fret has no ceiling), a `hand` on a piano's
  staff, a capo without a tuning, ids twice in a track or differing by column are refused, each by
  track, measure, staff, voice and token. A shorter track is silent after its last measure. Two notes
  struck on one string at one instant, in one beat or two voices, are read and written as they stand
  (2026-11-08; they were refused before), as MuseScore reads them: a reader shows the clash. A clef
  never changes the sound; absent, it follows from `tuning` and `instrument`. `{mt n}` is reserved:
  a note n cents off its named pitch.
- **Reading v2**: a v2 `PIANO` track becomes a piano without strings, its pitches kept, its hands
  its staves (without a hand, from C4 up the right one); a note no pitch can be given (on a string
  past the tuning, a muted note on a piano) is kept on its beat as written, silent as in v2.
  Two notes struck on one string at an instant stay as written, each on its string at its fret
  (2026-11-08; they were settled before, a note merged, moved or left out).
- **A track may say the General MIDI program it sounds, and be a drum kit** (2026-11-14; every
  version reads both, so the schemas of versions 1 and 2 list them too): `program`, `0`..`127`, as
  Guitar Pro, MIDI and MusicXML state it — a violin sounds a violin, a distorted guitar a distorted
  guitar —, written back by the MIDI (Program Change) and MusicXML (`midi-program`) exports; and
  `instrument: "DRUMS"`, the General MIDI kit, whose drum notes (`p36`) sound and are drawn on a
  percussion staff, written to the MIDI drum channel and as unpitched MusicXML notes. Absent, a
  track sounds its instrument's program: a guitar a nylon guitar (`24`, which the MIDI and MusicXML
  exports now write instead of `25`, so that the file sounds what Cesure plays), a bass a finger
  bass (`33`), a piano a grand piano (`0`).
  A drum note lives on a `DRUMS` track alone: a track without an instrument whose notes are all drum
  notes is read as one; any other track mixing them is an error naming it.

## v2

Written by Cesure from 2026-10 to 2026-11; every reader keeps reading v1 ([v1.md](v1.md)).

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
  was the size of an allocation a file chose. Cesure read a value outside 1 to 128 as 4, as it
  read a denominator outside its list — until 2026-10-10, when it began refusing both (below).
- **A time signature outside its range is refused** (2026-10-10, no new version): a numerator
  outside 1 to 128 or a denominator outside its list makes Cesure's import refuse the file, naming
  the value, instead of reading it as 4. The schema always held these ranges: every file it
  validates still opens.
- **A document nests at most 64 levels** (added 2026-10-05, no new version): Cesure refuses a file
  whose JSON nests deeper as damaged, before reading it; no file it writes goes past a dozen.
- **Keys** (added 2026-10-17, no new version): `Score.key`, the key from the first measure (`"Am"`,
  `"Bb"`, `"F#m"`), and `Score.keyChanges`, by measure id like the tempo changes. Absent = the file
  states none. A v2 reader that does not know them keeps them and writes them back unchanged, even
  after it moves the notes: a file an older build transposed states the key it had before. A key
  name a reader does not know makes the file damaged.
- **A measure may be marked `incomplete`** (added 2026-10-17, no new version): a pickup, or a
  closing measure that completes it, in its own time signature. Every file reads and plays as
  before; a reader that does not know the key keeps it and writes it back. See *Pickup and short
  endings* in the README. Since 2026-10-24 the mark may also stand on a short measure inside the
  piece (an inner pickup, a bar split by a repeat sign): same key, same reading.
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
