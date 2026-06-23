# Build Verification

MMB4L builds and tests as a normal Linux project. On Windows, use WSL and keep
the tested tree on a case-sensitive Linux filesystem when running the full test
suite.

## Dependencies

For Ubuntu 22.04:

```sh
sudo apt-get update
sudo apt-get install -y libsdl2-dev libsdl2-image-dev build-essential cmake git
```

If `sudo` is not configured for the WSL user but Windows can launch WSL as root,
the same install can be run from PowerShell:

```powershell
wsl.exe -d Ubuntu-22.04 -u root -- sh -lc 'apt-get update && apt-get install -y libsdl2-dev libsdl2-image-dev build-essential cmake git'
```

## Build Command

From a Linux or WSL shell:

```sh
cd ~/src/mmb4l-language-v6
bash ./build.sh
```

If the repo is checked out under `/mnt/c`, the project directory must be
case-sensitive. The full test suite includes a path test that creates
`foo.bas`, `foo.BAS`, and `foo.Bas` as separate files.

From an elevated or WSL-enabled Windows environment:

```powershell
fsutil.exe file setCaseSensitiveInfo C:\Users\georg\Codex_Projects\mmb4l-language-v6 enable
fsutil.exe file queryCaseSensitiveInfo C:\Users\georg\Codex_Projects\mmb4l-language-v6
```

Expected query output:

```text
Case sensitive attribute on directory C:\Users\georg\Codex_Projects\mmb4l-language-v6 is enabled.
```

If enabling case sensitivity is not possible, use a WSL-native clone or
temporary copy for full verification.

Example PowerShell verification using a temporary WSL-native copy:

```powershell
wsl.exe -d Ubuntu-22.04 -- sh -lc 'set -e; rm -rf /tmp/mmb4l-language-v6-build; mkdir -p /tmp/mmb4l-language-v6-build; cd /mnt/c/path/to/mmb4l-language-v6; tar --exclude=.git --exclude=build -cf - . | tar -C /tmp/mmb4l-language-v6-build -xf -; cd /tmp/mmb4l-language-v6-build; bash ./build.sh'
```

Replace `/mnt/c/path/to/mmb4l-language-v6` with the WSL path to the Windows
checkout.

## Current Baseline Result

Verified on Ubuntu 22.04 WSL from a case-sensitive project directory mounted at
`/mnt/c/Users/georg/Codex_Projects/mmb4l-language-v6`:

```text
100% tests passed, 0 tests failed out of 999
The following tests did not run:
  581 - ParseTest.ParsePage_GivenUnknownNonStringPageId_AndPicomite (Skipped)
```

If this same build is run from a non-case-sensitive Windows directory, it can
build `mmbasic` but fail `ProgramTest.GetBasFile_GivenRelativePath`.
