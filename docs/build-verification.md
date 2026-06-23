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

If the repo is checked out under `/mnt/c`, the executable can build, but the
full test suite may fail a case-sensitivity test because Windows filesystems
normally cannot hold `foo.bas`, `foo.BAS`, and `foo.Bas` as separate files. Use
a WSL-native clone or temporary copy for full verification.

Example PowerShell verification using a temporary WSL-native copy:

```powershell
wsl.exe -d Ubuntu-22.04 -- sh -lc 'set -e; rm -rf /tmp/mmb4l-language-v6-build; mkdir -p /tmp/mmb4l-language-v6-build; cd /mnt/c/path/to/mmb4l-language-v6; tar --exclude=.git --exclude=build -cf - . | tar -C /tmp/mmb4l-language-v6-build -xf -; cd /tmp/mmb4l-language-v6-build; bash ./build.sh'
```

Replace `/mnt/c/path/to/mmb4l-language-v6` with the WSL path to the Windows
checkout.

## Current Baseline Result

Verified on Ubuntu 22.04 WSL using a WSL-native temporary copy:

```text
100% tests passed, 0 tests failed out of 999
The following tests did not run:
  581 - ParseTest.ParsePage_GivenUnknownNonStringPageId_AndPicomite (Skipped)
```

The same build run directly from `/mnt/c` built `mmbasic`, but failed
`ProgramTest.GetBasFile_GivenRelativePath` because the Windows-mounted path is
case-insensitive.
