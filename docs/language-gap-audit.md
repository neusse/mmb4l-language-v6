# Language Gap Audit

Status: initial scaffold.

This audit will track differences between upstream MMB4L and the current
PicoMite MMBasic v6 language/runtime. Do not treat a difference as a bug until
it is classified.

## Baseline

| Item | Value |
| --- | --- |
| MMB4L upstream remote | `https://github.com/thwill1000/mmb4l` |
| PicoMite reference tree | `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions` |
| Initial branch | `main` |
| Hardware scope | Excluded for now |

## Classification

| Gap | Classification | Reference | MMB4L location | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| ARMv7 architecture label | portable | N/A | `src/main.c` | candidate | Existing Luckfox patch changes reported banner text from ARMv6 to ARMv7 when compiled for ARMv7. |
| PicoCalc framebuffer scaling/DirectFB behavior | hardware/linux-backend | N/A | Luckfox project | out of scope | Keep in `mmbasic-4-luckfox-lyra`; not part of language v6 work. |
| GPIO/SPI/I2C commands | hardware | PicoMite hardware modules | N/A | out of scope | No current use case. |

## Audit Procedure

1. Extract MMB4L command, function, and operator tables.
2. Extract PicoMite command, function, and operator definitions.
3. Compare names and syntax.
4. Read source for differences that are behavior-compatible but named
   differently.
5. Add one row per candidate gap before writing code.

## Notes

MMB4L already documents intentional differences from PicoMite in its README.
Those differences should be reviewed before classifying a missing behavior as a
porting task.
