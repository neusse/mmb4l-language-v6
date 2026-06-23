# Language Gap Audit

Status: generated baseline for the MMB4L to PicoMite v6 language audit.

This audit tracks differences between upstream MMB4L and the PicoMite MMBasic
v6 command/function/operator surface. A difference is not a porting task until
it is classified and source-reviewed.

## Baseline

| Item | Value |
| --- | --- |
| MMB4L upstream remote | `https://github.com/thwill1000/mmb4l` |
| PicoMite reference tree | `PicoMiteAllVersions` checkout supplied with `--picomite-root` or `PICOMITE_ALLVERSIONS` |
| PicoMite reference file | `AllCommands.h` |
| Working branch | `language-v6-port-docs` |
| Hardware scope | Classified, but not prioritized for this fork |

## Generated Audit Files

Run the extractor from the repository root. Point `--picomite-root` at a local
copy of `PicoMiteAllVersions`:

```powershell
python tools\language_audit.py --repo-root . --picomite-root <path-to-PicoMiteAllVersions> --output-dir docs\generated
```

Outputs:

| File | Purpose |
| --- | --- |
| `docs/generated/language-surface-mmb4l.md` | Extracted MMB4L commands, functions, operators, and parser keywords. |
| `docs/generated/language-surface-picomite-v6.md` | Extracted PicoMite v6 commands, functions, operators, and parser keywords. |
| `docs/generated/language-gap-table.md` | PicoMite v6 surfaces missing from MMB4L, classified by portability. |
| `docs/generated/*.csv` | Machine-readable copies for filtering and review. |

## Current Counts

The extractor includes PicoMite entries guarded by variant macros so we can
classify them instead of silently missing them.

| Source | Command | Function | Operator | Keyword |
| --- | ---: | ---: | ---: | ---: |
| MMB4L | 122 | 93 | 22 | 10 |
| PicoMite v6 | 220 | 110 | 20 | 10 |

PicoMite v6 to MMB4L gap rows:

| Classification | Count | Meaning |
| --- | ---: | --- |
| portable | 36 | Language/runtime feature that should be possible to port without PicoMite hardware. |
| linux-specific | 15 | Needs Linux filesystem, process, display, GUI, or host behavior mapping. |
| hardware | 84 | Depends on PicoMite hardware, bus, display/input firmware, or embedded-only behavior. |
| defer | 4 | Needs source review before choosing a class. |

## Classification Rules

| Classification | Rule |
| --- | --- |
| portable | Pure language, parser, string, array, math, graphics algorithm, or runtime behavior. |
| linux-specific | Semantics depend on Linux paths, files, processes, terminal/display backend, or host UI. |
| hardware | Semantics require PicoMite GPIO, buses, PIO, firmware update flow, sensors, or embedded hardware. |
| defer | The name alone is not enough; inspect the PicoMite implementation before scheduling work. |

## Reserved Surface Policy

Do not add every PicoMite-only name as a token just to reserve it. That makes
the language stricter without giving users useful behavior.

Use this policy:

| Case | Behavior |
| --- | --- |
| Planned for this port | Add the token and implement it. |
| Planned but backend unavailable at runtime | Add the token and fail with a clear platform/backend error. |
| Not planned or not yet reviewed | Leave it unimplemented so normal parser errors expose unsupported use. |
| Hardware name with a target-specific implementation | Keep it classified as `hardware`, then document the supported target backend. |

This means hardware gaps are not automatically reserved. They become reserved
only when this project intentionally owns that command/function surface.

## Current Portable Candidates

The generated table is the source of truth, but the current portable bucket
includes likely port candidates such as:

| Area | Candidates |
| --- | --- |
| Parser/comments | `/*`, `*/` |
| Strings | `base$(`, `SChange$(` |
| Arrays | `Array Add`, `Array Insert`, `Array Set`, `Array Slice`, `ReDim` |
| Structured data | `Type`, `End Type`, `Struct`, `Struct(` |
| Bit/byte helpers | `Bit(`, `Byte(`, `Flag(`, `Flags` |
| LongString | `LInput(`, `LMid(` |
| Graphics | `Bezier`, `Fill`, `Mandelbrot`, `Pixel(`, `Turtle` |
| Program/runtime helpers | `Chain`, `VAR` |
| Astronomy helpers | `Astro`, `Location`, `Star` |

## Reviewed Edge Cases

| Candidate | Current class | Finding |
| --- | --- | --- |
| `Backlight` | hardware | PicoMite drives display backlight hardware. Keep hardware, but it may be a Luckfox/PicoCalc target feature because the device has controllable backlight support. |
| `Wait` | hardware | This is a PIO assembler instruction wrapper, not a sleep command. |
| `Edit File` | linux-specific | PicoMite edits an external file buffer. MMB4L `Edit` already accepts a filename, so this is likely a compatibility alias/design task. |
| `Help` | linux-specific | PicoMite reads `A:/help.txt`; MMB4L would need a local docs/help mapping. |
| `MsgBox(` | linux-specific | GUI popup helper; requires an SDL/Linux UI decision. |
| `Library` | linux-specific | PicoMite stores a library in flash; Linux needs filesystem/module semantics. |
| `Pixel(` | portable | PicoMite reads a pixel colour; MMB4L already has pixel-writing and in-memory graphics surfaces. |
| `Save` | linux-specific | MMB4L intentionally edits real files and has no flash-to-disk `SAVE` step. Any compatibility command needs explicit Linux semantics. |
| `YModem` | linux-specific | Serial transfer workflow; not needed for current PicoCalc/Luckfox scope. |

## Defer Items

These four gaps should be source-reviewed before classification changes:

| Candidate | Reason |
| --- | --- |
| `Calc` | Could be interactive prompt behavior rather than core language. |
| `Interrupt` | Needs review of how PicoMite CSub interrupts map to Linux. |
| `WatchDog` | May be firmware/hardware behavior, but source should confirm. |
| `~(` | Needs source review for semantics and safety. |

## Prior Completed Patch

`Trim$(` was ported before this generated baseline. It now appears in both
surfaces and is no longer a gap.

Verification at that point:

```text
test_trim_function: PASS (7/7)
tests/tst_strings.bas: PASS (15/15)
tests/tst_strings.bas --base=1: PASS (15/15)
100% tests passed, 0 tests failed out of 999
```
