# Scores

Opus (`claude -p --model opus`) overall score out of 10 per image at 390 px, after the two-second test. FAIL means the two-second test failed and the image scored 0 without the rubric. Target: every image 8 or higher.

| Image | Round 1 | Round 2 | Round 3 (final) |
| --- | --- | --- | --- |
| gate-threshold (log) | 7 | 7 | 7 |
| orca-timeline (state key) | 6 | 7 | 7 |
| perf-illustrative (range, player) | 8 | FAIL (60 printed twice, wave ran to 60 s) | 7 |
| architecture-rec (layers) | 8 | 7 | 8 |
| orca-player (existing fixture) | 6 | 7 | 8 |
| bugfix (existing fixture, attempts) | FAIL (axis labels, 40 printed twice) | FAIL (axis labels ran together) | 7 |
| perf (existing fixture, 1.8 s to 240 ms) | 4 | 7 | 6 |
| perf, second visual (201 queries to 1) | 4 | not produced | 6 |
| status-tests (343 tests) | NO_IMAGE | NO_IMAGE | NO_IMAGE |

Two-second test in the final round: every image passed (8 of 8).

Result: not approved. Two of eight images reach 8 (architecture-rec, orca-player). The rest sit at 6 or 7.

## What moved the scores

- Round 1 to 2: clipped units and labels over the axis (the "attemp" and "querie" cuts) fixed; value labels moved under the track; dashes and waveform filled the whole track.
- Round 2 to 3: the gap in the BEFORE log line became an invisible spacer (the dashed box read as a broken glyph); an open value ("more than 40") draws an open bracket instead of a dot at the axis end; the waveform fades out so it does not read as a duration; axis tick labels are not counted as repeated numbers by the two-second test; the unit sits on its own line under a long-unit axis.

## What still holds the scores at 6 and 7

- gate-threshold: the AFTER line reads 0.549 needs 0.550 correctly; the judge wants the AFTER caption closer to its line.
- orca-timeline: the judge wants the bug (both states grey) shown as well as the fix. Max's reference shows only the fixed key, so this was left as the reference does it.
- perf and perf second visual: the model splits the reply into two images and each omits the other's main number (1.8 s to 240 ms, 201 queries to 1). The prompt says one concept per image, so each image is right for its concept; the judge scores the omission.
- perf-illustrative: the green waveform after the bracket still reads as playback data to the judge, although it fades; the eyebrow PROJECT is the model's choice.
- bugfix: the open bracket fades to the axis end; the judge reads the fade as an invented end.

Rounds 1 and 2 were scored on renders from earlier template versions; round 3 is the final template and prompt.
