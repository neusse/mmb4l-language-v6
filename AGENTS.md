# AGENTS.md

This repository is a working fork of upstream MMB4L for language/runtime
alignment with current PicoMite MMBasic. Keep changes structured so they can be
reviewed, tested, and offered upstream as small pull requests.

## Scope

- Work on language/runtime behavior first: parser, tokenizer, commands,
  functions, operators, error behavior, and portable runtime services.
- Do not port PicoMite GPIO, SPI, I2C, RP2040/RP2350 board support, or bare-metal
  startup code unless a later requirement explicitly adds that scope.
- Keep PicoCalc framebuffer/DirectFB/Luckfox deployment fixes in the separate
  `mmbasic-4-luckfox-lyra` project unless a fix is generally useful to MMB4L.

## Reference Sources

- Upstream MMB4L remote: `https://github.com/thwill1000/mmb4l`
- Local PicoMite reference tree:
  `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions`
- PicoMite developer notes:
  `C:\Users\georg\Codex_Projects\WebMite\PicoMiteAllVersions\docs`

Use PicoMite files as reference material, not as unreviewed bulk imports. Each
ported behavior should cite the source file and the reason it is portable to
Linux.

## Workflow

- Start from a clean `main` tracking upstream.
- Create one branch per language/runtime feature or compatibility fix.
- Prefer tests before implementation for behavior changes.
- Keep commits narrow and explain which PicoMite behavior they align with.
- Preserve the upstream credit and license chain in any copied or adapted code.

## Verification

At minimum, run the host build and relevant tests before calling a change done:

```sh
./build.sh
```

If a change affects parser/runtime behavior, run the matching gtest target or
program-level tests in addition to a full build.

When working from Windows, see `docs/build-verification.md`: full tests must run
on a case-sensitive WSL/Linux filesystem, not directly under `/mnt/c`.
