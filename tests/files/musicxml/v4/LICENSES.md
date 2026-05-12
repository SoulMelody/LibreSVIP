# MusicXML 4.0 test fixtures

All files in this directory are hand-crafted minimal MusicXML 4.0 documents,
written by LibreSVIP contributors and licensed under the same MIT license as
the rest of the LibreSVIP project. No content was copied from external test
suites.

| File | Purpose |
|------|---------|
| `v4-empty-fermata.musicxml` | Exercises the strictness preprocessor: contains an empty `<fermata/>` element which the v4 spec allows (== "normal"). |
| `v4-direction-tempo.musicxml` | Mid-measure tempo change via `<direction><sound tempo="60"/></direction>` — verifies that tempo changes outside `<measure>.sound` are picked up. |
| `v4-dynamics-wedge.musicxml` | Per-direction `<dynamics><p/></dynamics>`, a `<wedge type="crescendo"/>`, and `<dynamics><f/></dynamics>` to verify volume-curve population. |
