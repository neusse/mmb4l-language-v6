# PicoMite Reference Map

The PicoMite reference tree is:

```text
C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions
```

This project uses PicoMite as a language/runtime reference. It is not a plan to
turn MMB4L into PicoMite firmware. PicoMite is an embedded firmware monolith
with hardware startup, display drivers, storage stacks, and board variants that
do not map directly to a Linux process.

## Source Areas To Compare First

| PicoMite area | Typical files | MMB4L area | Notes |
| --- | --- | --- | --- |
| Interpreter core | `MMBasic.c`, `MMBasic.h`, `MMBasic_Includes.h` | `src/core/MMBasic.c`, `src/core/MMBasic.h` | Tokenization, execution, variables, error paths. |
| Command dispatch | `AllCommands.h`, `Commands.h`, `Custom.h` | `src/core/commandtbl.*`, `src/commands/*.c` | Compare command availability and syntax. |
| Functions | `Functions.h`, `Functions.c` | `src/core/Functions.*`, `src/functions/*.c` | Compare function names, arity, return types, and edge cases. |
| Operators | `Operators.h`, `Operators.c` | `src/core/Operators.c`, `src/operators/*.c` | Compare precedence and numeric/string coercion. |
| Runtime services | `MM_Misc.c`, `Memory.c`, `MATHS.c`, `re.c`, `aes.c` | `src/common/*`, `src/core/maths.*` | Only portable runtime behavior belongs here. |
| Graphics language surface | `Draw.c`, `FrameBuffer.c`, `GUI.c` | `src/commands/cmd_*.c`, `src/common/graphics.*` | Port syntax/semantics only when Linux backends can support it. |

## Areas Out Of Scope For This Fork

These files can explain command behavior, but they should not be ported as
hardware implementations in this project:

- `PicoMite.c`
- `configuration.h`
- `gpio.c`
- `psram.c`
- `External.c`
- `I2C.c`
- `SPI.c`
- `Serial.c` when tied to Pico pin ownership
- display driver files such as `SPI-LCD.c`, `SSD1963.c`, `VGA222.c`

## Attribution Rules

When adapting behavior or code from PicoMite:

- Keep the source copyright/license notice when code is copied.
- Prefer behavior-compatible reimplementation when the original code depends on
  bare-metal firmware state.
- Mention the PicoMite source file in the commit message or nearby developer
  documentation.
- Keep upstream MMB4L attribution intact.
