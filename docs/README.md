# MMB4L Language V6 Port Workspace

This workspace is for developing an upstream-friendly MMB4L fork that moves
MMB4L language/runtime behavior toward the current PicoMite MMBasic v6 family.

It is intentionally separate from the Luckfox Lyra/PicoCalc packaging project.
The Luckfox project owns cross-compilation, install scripts, framebuffer quirks,
PicoCalc tests, and deployment. This project owns portable MMBasic language
work that could reasonably be proposed back to upstream MMB4L.

## Goals

- Audit the language/runtime differences between MMB4L and current PicoMite.
- Port portable MMBasic v6 behavior into MMB4L as small, reviewable changes.
- Preserve Linux behavior where MMB4L intentionally differs from embedded
  PicoMite firmware.
- Keep clear attribution to upstream MMB4L and PicoMite sources.
- Produce tests that can run in WSL or normal Linux before code is used on the
  PicoCalc.

## Non-Goals

- No PicoMite bare-metal boot/runtime port.
- No RP2040/RP2350 board support.
- No GPIO, SPI, or I2C work unless a later use case requires it.
- No PicoCalc framebuffer repair in this repository.

## Reference Material

- Upstream MMB4L: `https://github.com/thwill1000/mmb4l`
- PicoMite reference tree:
  `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions`
- PicoMite architecture notes:
  `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions\docs`

Important reference docs:

- `docs/code-structure-report.md`
- `docs/module-ownership.md`
- `docs/variant-build-matrix.md`

## Local Build

On Windows, use WSL for the normal Linux build path. For full test-suite
verification, build from a WSL-native filesystem or temporary copy rather than
directly under `/mnt/c`, because the tests include case-sensitive path behavior.

```powershell
wsl.exe -d Ubuntu-22.04 -- sh -lc 'cd /mnt/c/Users/georg/Codex_Projects/mmb4l-language-v6 && bash ./build.sh'
```

Use the distribution name installed on the machine if it is not
`Ubuntu-22.04`. The repository includes `.gitattributes` rules that keep shell
scripts and build files LF-normalized for WSL/Linux.

See [build verification](build-verification.md) for dependency installation and
the case-sensitive test-suite path.

## Documents

- [PicoMite reference map](picomite-reference.md)
- [Language port plan](language-port-plan.md)
- [Language gap audit](language-gap-audit.md)
- [Build verification](build-verification.md)
- [Source credit](source-credit.md)
