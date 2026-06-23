# Language Port Plan

This plan keeps the work reviewable and suitable for upstream discussion.

## Phase 1: Baseline

- Confirm a clean upstream MMB4L clone builds on WSL/Linux.
- Record the exact upstream commit and submodule commit used for comparison.
- Run the existing host tests before changing language behavior.
- List current README-documented differences from PicoMite MMBasic v6.

## Phase 2: Gap Audit

- Build a command/function/operator inventory from MMB4L tables.
- Build the same inventory from the PicoMite reference tree.
- Classify gaps as:
  - `portable`: should work on Linux without hardware dependencies.
  - `linux-specific`: MMB4L intentionally differs because it is an OS process.
  - `hardware`: belongs to PicoMite firmware only.
  - `defer`: needs a concrete user program before porting.

## Phase 3: Small Ports

Port one behavior at a time:

1. Add or update a test that demonstrates the PicoMite v6 behavior.
2. Implement the smallest MMB4L change that passes the test.
3. Document the source file used as reference.
4. Run the host build and relevant tests.

Good first candidates are portable parser/runtime fixes, command syntax
compatibility, numeric/string edge cases, and error message compatibility where
existing tests already cover nearby behavior.

## Phase 4: Candidate Upstream PRs

Keep upstream PRs narrow. Candidate patches from the Luckfox project that may be
generally useful here:

- Correct Linux ARM architecture reporting where the binary is built for ARMv7.
- Improve portable test expectations around ARM range/error formatting.
- Keep portable test fixes separate from PicoCalc framebuffer/DirectFB-specific
  work.

## Phase 5: Return To PicoCalc

After portable language changes are proven on WSL/Linux:

- Pull selected fork commits into `mmbasic-4-luckfox-lyra`.
- Rebuild with the Luckfox Lyra SDK cross compiler.
- Re-run the PicoCalc deployment and BASIC test suite there.
- Keep PicoCalc framebuffer fixes in the Luckfox project unless the fix is a
  general MMB4L bug.
