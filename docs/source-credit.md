# Source Credit

This project stands on top of existing MMBasic work. Keep this credit visible
in user-facing documentation and commit messages when source-derived changes are
made.

## Upstream MMB4L

- Repository: `https://github.com/thwill1000/mmb4l`
- MMB4L-specific code: Thomas Hugo Williams
- License files in this repository:
  - `LICENSE`
  - `LICENSE.MIT`
  - `LICENSE.MMBasic`

## MMBasic And PicoMite

The upstream MMB4L README states that MMB4L is derived from and incorporates
code or ideas from MMBasic ports including PicoMite/PicoMite VGA.

- MMBasic: Geoff Graham
- PicoMite/PicoMite VGA: Geoff Graham and Peter Mather
- PicoMite source reference: `https://github.com/UKTailwind/PicoMiteAllVersions`
- Local PicoMite reference tree:
  `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions`

## Local Project Rule

When a change is adapted from PicoMite:

- Cite the PicoMite file in the commit message or related documentation.
- Preserve license headers for copied code.
- Prefer behavior-compatible Linux implementations when PicoMite code depends on
  bare-metal state or hardware registers.
- Keep hardware-only features out of this fork unless scope changes.
