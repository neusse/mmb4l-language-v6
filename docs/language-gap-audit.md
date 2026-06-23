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
| MMB4L | 131 | 103 | 22 | 10 |
| PicoMite v6 | 220 | 110 | 20 | 10 |

PicoMite v6 to MMB4L gap rows:

| Classification | Count | Meaning |
| --- | ---: | --- |
| portable | 0 | Language/runtime feature that should be possible to port without PicoMite hardware. |
| linux-specific | 16 | Needs Linux filesystem, process, display, GUI, or host behavior mapping. |
| hardware | 84 | Depends on PicoMite hardware, bus, display/input firmware, or embedded-only behavior. |
| defer | 23 | Needs source review before choosing a class. |

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

The generated table is the source of truth. The current portable bucket is
empty; all rows that were previously listed as portable have either been
implemented or moved to a more accurate class with a concrete blocker.

| Area | Status |
| --- | --- |
| Parser/comments | Complete for currently reviewed portable surfaces. |
| Strings | Complete for currently reviewed portable surfaces. |
| Arrays | Deferred; needs a reviewed array helper subsystem and resizing design. |
| Structured data | Deferred; needs parser, variable-table, and token-table architecture work. |
| Bit/byte helpers | `Flags = value`, `Bit(`, `Byte(`, and `Flag(` are implemented; bare `Flags` readback is token-table blocked. |
| LongString | `LMid(` is implemented; `LInput(` is token-table blocked. |
| Graphics | `Blit Memory` is implemented; algorithmic graphics commands are deferred for graphics-backend tests. |
| Program/runtime helpers | `Chain` is implemented; `VAR` is Linux-specific persistence design work. |
| Astronomy helpers | Deferred; needs GPS/astronomy source review and domain tests. |

## Resolution of Prior Portable Rows

These rows were the 21 remaining portable gaps before this pass. They are now
resolved as follows:

| Prior row | Resolution | Action |
| --- | --- | --- |
| `Array Add` | defer | Reclassified; requires a reviewed array helper subsystem for numeric/string arrays, cardinality, and stride semantics. |
| `Array Insert` | defer | Reclassified; requires multidimensional array slice/index semantics before implementation. |
| `Array Set` | defer | Reclassified; requires array helper coverage for numeric/string arrays and type coercion. |
| `Array Slice` | defer | Reclassified; requires multidimensional array slice/index semantics before implementation. |
| `Astro` | defer | Reclassified; implemented in PicoMite GPS/astronomy code and needs dedicated domain review/tests. |
| `Bezier` | defer | Reclassified; graphics algorithm needs a backend-aware port and visual/regression tests. |
| `Blit Memory` | implemented | Added top-level PicoMite command surface that reuses MMB4L's existing `Blit MEMORY` implementation. |
| `End Type` | defer | Reclassified; part of structured-type parser/runtime support, not a standalone command patch. |
| `Fill` | defer | Reclassified; graphics algorithm needs a backend-aware port and visual/regression tests. |
| `Flags` function | defer | Reclassified; `Flags = value` exists, but bare readback is blocked by the full one-byte function token table. |
| `LInput(` | defer | Reclassified; handler is portable in principle, but adding another function token is blocked by the full one-byte function token table. |
| `Location` | defer | Reclassified; implemented in PicoMite GPS/astronomy code and needs dedicated domain review/tests. |
| `Mandelbrot` | defer | Reclassified; graphics algorithm needs a backend-aware port and visual/regression tests. |
| `Pixel(` | defer | Reclassified; readback is plausible, but adding another function token is blocked by the full one-byte function token table. |
| `ReDim` | defer | Reclassified; requires reviewed runtime support for resizing existing arrays safely. |
| `Star` | defer | Reclassified; implemented in PicoMite GPS/astronomy code and needs dedicated domain review/tests. |
| `Struct` command | defer | Reclassified; structured-type support needs parser and variable-table architecture work. |
| `Struct(` function | defer | Reclassified; structured-type support also needs function-token architecture work. |
| `Turtle` | defer | Reclassified; graphics-state command set needs backend-aware port and visual/regression tests. |
| `Type` | defer | Reclassified; part of structured-type parser/runtime support, not a standalone command patch. |
| `VAR` | linux-specific | Reclassified; PicoMite persists variables in flash, while MMB4L needs explicit Linux filesystem persistence semantics. |

## Reviewed Edge Cases

| Candidate | Current class | Finding |
| --- | --- | --- |
| `Backlight` | hardware | PicoMite drives display backlight hardware. Keep hardware, but it may be a Luckfox/PicoCalc target feature because the device has controllable backlight support. |
| `Wait` | hardware | This is a PIO assembler instruction wrapper, not a sleep command. |
| `Edit File` | linux-specific | PicoMite edits an external file buffer. MMB4L `Edit` already accepts a filename, so this is likely a compatibility alias/design task. |
| `Help` | linux-specific | PicoMite reads `A:/help.txt`; MMB4L would need a local docs/help mapping. |
| `MsgBox(` | linux-specific | GUI popup helper; requires an SDL/Linux UI decision. |
| `Library` | linux-specific | PicoMite stores a library in flash; Linux needs filesystem/module semantics. |
| `Pixel(` | defer | PicoMite reads a pixel colour and MMB4L has pixel surfaces, but adding another function token is blocked by the full one-byte function token table. |
| `Save` | linux-specific | MMB4L intentionally edits real files and has no flash-to-disk `SAVE` step. Any compatibility command needs explicit Linux semantics. |
| `YModem` | linux-specific | Serial transfer workflow; not needed for current PicoCalc/Luckfox scope. |
| `Flags` function | defer | `Flags = value` is implemented as a command and `Flag(n)` can read individual bits. Bare `Flags` readback still needs parser/token-table work because the existing one-byte token table is full at `Flag(` token 255. |

## Defer Items

These four gaps should be source-reviewed before classification changes:

| Candidate | Reason |
| --- | --- |
| `Calc` | Could be interactive prompt behavior rather than core language. |
| `Interrupt` | Needs review of how PicoMite CSub interrupts map to Linux. |
| `WatchDog` | May be firmware/hardware behavior, but source should confirm. |
| `~(` | Needs source review for semantics and safety. |

## Prior Completed Patches

`Trim$(`, `SChange$(`, `base$(`, `TopBottom(`, `Bit(`, `Byte(`, `Flag(`,
`Flags = value`, `/*`, `*/`, `LMid(`, and `Chain` were ported before this
generated baseline. `Blit Memory` was ported in the current pass.
They now appear in both surfaces where token capacity allows and are no longer
gaps.

Verification at that point:

```text
test_trim_function: PASS (7/7)
tests/tst_strings.bas: PASS (15/15)
tests/tst_strings.bas --base=1: PASS (15/15)
100% tests passed, 0 tests failed out of 999
```
