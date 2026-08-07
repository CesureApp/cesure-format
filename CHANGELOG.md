# Changelog

Additive fields (a new field with a default) are **backward-compatible** and do **not** bump the
version — old files still load, new files still open in older builds (unknown keys are ignored).
They are listed under v1 with the date they were added.

## v1

### Additive fields (backward-compatible, no version bump)

- **`Track.volume`** *(number 0..1, default 1)* + **`Track.instrument`**
  *(`GUITAR` | `BASS` | `PIANO`, default `GUITAR`)* — the track's place in the mix. Both are
  **arrangement data**, like `capo`: imported from Guitar Pro (MIDI channel volume and General
  MIDI program), saved, exported. A file written before these fields reads as full-scale guitar,
  which is exactly how it used to sound. `instrument` is deliberately narrow — it lists only what
  a player can actually render, rather than promising timbres that would silently fall back.

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
