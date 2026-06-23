#!/usr/bin/env python3
"""Extract and compare MMB4L and PicoMite MMBasic language surfaces."""

from __future__ import annotations

import argparse
import csv
import dataclasses
import os
import pathlib
import re
from collections import Counter, defaultdict


SURFACE_ORDER = {"command": 0, "function": 1, "operator": 2, "keyword": 3, "token": 4}


@dataclasses.dataclass(frozen=True)
class Entry:
    source: str
    table: str
    name: str
    normalized: str
    surfaces: tuple[str, ...]
    flags: str
    precedence: str
    handler: str
    line: int


ENTRY_RE = re.compile(
    r'\{\s*(?:\(unsigned\s+char\s*\*\))?\s*"((?:\\.|[^"])*)"\s*,'
    r"\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*,?\s*\}",
    re.DOTALL,
)


PORTABLE = {
    "/*",
    "*/",
    "ARRAY ADD",
    "ARRAY INSERT",
    "ARRAY SET",
    "ARRAY SLICE",
    "ASTRO",
    "BASE$",
    "BEZIER",
    "BIT",
    "BLIT MEMORY",
    "BYTE",
    "CHAIN",
    "END TYPE",
    "FILL",
    "FLAG",
    "FLAGS",
    "LMID",
    "LINPUT",
    "LOCATION",
    "MANDELBROT",
    "PIXEL",
    "REDIM",
    "SCHANGE$",
    "STAR",
    "STRUCT",
    "TOPBOTTOM",
    "TURTLE",
    "TYPE",
    "VAR",
}

LINUX_SPECIFIC = {
    "CMM2 LOAD",
    "CMM2 RUN",
    "CONFIGURE",
    "DATE$",
    "DRIVE",
    "EDIT FILE",
    "FLASH",
    "FLUSH",
    "HELP",
    "LIBRARY",
    "MSGBOX",
    "SAVE",
    "TIME$",
    "UPDATE FIRMWARE",
    "YMODEM",
}

HARDWARE = {
    "_END PROGRAM",
    "_LABEL",
    "_LINE",
    "_PROGRAM",
    "_SIDE SET",
    "_WRAP",
    "_WRAP TARGET",
    "ADC",
    "BACKLIGHT",
    "BITSTREAM",
    "CAMERA",
    "CLASSIC",
    "CLICK",
    "COLOUR MAP",
    "CPU",
    "CTRLVAL",
    "DISTANCE",
    "DRAW3D",
    "FM",
    "FRAME",
    "GAMEPAD",
    "GETSCANLINE",
    "GPS",
    "HUMID",
    "I2C",
    "I2C2",
    "I2CLCD",
    "IN",
    "IR",
    "IRQ",
    "IRQ CLEAR",
    "IRQ NEXT",
    "IRQ NOWAIT",
    "IRQ PREV",
    "IRQ SET",
    "IRQ WAIT",
    "JMP",
    "KEYBOARD",
    "KEYPAD",
    "LCD",
    "MAP",
    "MODE",
    "MOUSE",
    "MOV",
    "NOP",
    "ONEWIRE",
    "ONESHOT",
    "OUT",
    "PIO",
    "PORT",
    "PULL",
    "PULSIN",
    "PUSH",
    "PWM",
    "RAM",
    "RAY",
    "REFRESH",
    "RESOLUTION",
    "RTC",
    "SERVO",
    "SET",
    "SLEW",
    "SPI",
    "SPI2",
    "STEPPER",
    "SYNC",
    "TEMPR",
    "TEMPR START",
    "TILE",
    "TILEMAP",
    "TMC22XX",
    "TOUCH",
    "WAIT",
    "WEB",
    "WII",
    "WII CLASSIC",
    "WII NUNCHUCK",
    "WS2812",
}

DEFER = {
    "~",
    "CALC",
    "INTERRUPT",
    "WATCHDOG",
}

NOTE_OVERRIDES = {
    "BACKLIGHT": "Hardware command, but a target-specific Luckfox/PicoCalc backend may be useful because the device has controllable backlight support.",
    "EDIT FILE": "PicoMite edits an external file buffer; MMB4L `Edit` already accepts a filename, so this is likely a compatibility alias/design task.",
    "HELP": "PicoMite reads `A:/help.txt`; MMB4L should map this to local docs or command/function lists if implemented.",
    "LIBRARY": "PicoMite library storage is flash-based; Linux needs a filesystem/module design rather than direct behavior cloning.",
    "MSGBOX": "GUI popup helper; needs an SDL/Linux UI decision before implementation.",
    "PIXEL": "PicoMite `Pixel(x,y)` reads a pixel colour; MMB4L has the write command and likely can add this through its graphics surface pixels.",
    "SAVE": "MMB4L intentionally edits real files and has no flash-to-disk save step; any compatibility command needs Linux file semantics.",
    "WAIT": "PIO assembler instruction wrapper, not a sleep command; keep with PIO/hardware surface.",
    "YMODEM": "Serial transfer workflow; not needed for the current PicoCalc/Luckfox scope.",
}


def strip_c_comments(text: str) -> str:
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    line_comment = False
    block_comment = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
                out.append(ch)
            else:
                out.append(" ")
            i += 1
            continue
        if block_comment:
            if ch == "\n":
                out.append(ch)
            else:
                out.append(" ")
            if ch == "*" and nxt == "/":
                out.append(" ")
                i += 2
                block_comment = False
            else:
                i += 1
            continue
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            out.extend("  ")
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            out.extend("  ")
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def decode_c_string(value: str) -> str:
    return bytes(value, "utf-8").decode("unicode_escape")


def normalize_name(name: str) -> str:
    value = name.strip()
    while value.endswith("("):
        value = value[:-1]
    return re.sub(r"\s+", " ", value).upper()


def surfaces_from_flags(flags: str) -> tuple[str, ...]:
    upper = flags.upper()
    surfaces: list[str] = []
    if "T_CMD" in upper:
        surfaces.append("command")
    if "T_FUN" in upper or "T_FNA" in upper:
        surfaces.append("function")
    if "T_OPER" in upper:
        surfaces.append("operator")
    if not surfaces and "T_NA" in upper:
        surfaces.append("keyword")
    if not surfaces:
        surfaces.append("token")
    return tuple(surfaces)


def extract_entries_from_text(
    text: str, source: str, table: str, line_offset: int = 0
) -> list[Entry]:
    text = strip_c_comments(text)
    entries: list[Entry] = []
    for match in ENTRY_RE.finditer(text):
        name = decode_c_string(match.group(1))
        if not name:
            continue
        flags = re.sub(r"\s+", " ", match.group(2).strip())
        entries.append(
            Entry(
                source=source,
                table=table,
                name=name,
                normalized=normalize_name(name),
                surfaces=surfaces_from_flags(flags),
                flags=flags,
                precedence=match.group(3).strip(),
                handler=match.group(4).strip(),
                line=line_offset + text.count("\n", 0, match.start()) + 1,
            )
        )
    return entries


def extract_entries(path: pathlib.Path, source: str, table: str) -> list[Entry]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return extract_entries_from_text(text, source, table)


def extract_picomite(allcommands: pathlib.Path) -> list[Entry]:
    text = allcommands.read_text(encoding="utf-8", errors="replace")
    command = re.search(r"#ifdef INCLUDE_COMMAND_TABLE(?P<body>.*?)#endif /\* INCLUDE_COMMAND_TABLE \*/", text, re.S)
    token = re.search(r"#ifdef INCLUDE_TOKEN_TABLE(?P<body>.*?)#endif /\* INCLUDE_TOKEN_TABLE \*/", text, re.S)
    if not command or not token:
        raise RuntimeError(f"Could not locate PicoMite command/token tables in {allcommands}")
    command_line = text.count("\n", 0, command.start("body"))
    token_line = text.count("\n", 0, token.start("body"))
    return extract_entries_from_text(command.group("body"), "PicoMite", "command", command_line) + extract_entries_from_text(
        token.group("body"), "PicoMite", "token", token_line
    )


def dedupe_entries(entries: list[Entry]) -> list[Entry]:
    seen: set[tuple[str, tuple[str, ...], str, str]] = set()
    result: list[Entry] = []
    for entry in entries:
        key = (entry.normalized, entry.surfaces, entry.flags.upper(), entry.handler)
        if key not in seen:
            seen.add(key)
            result.append(entry)
    return result


def classify_gap(name: str, surface: str) -> tuple[str, str]:
    note_override = NOTE_OVERRIDES.get(name)
    if name in PORTABLE:
        return "portable", note_override or "Language/runtime feature with no required PicoMite-only hardware."
    if name in LINUX_SPECIFIC:
        return "linux-specific", note_override or "Needs Linux filesystem, process, or host configuration semantics."
    if name in HARDWARE:
        return "hardware", note_override or "Depends on PicoMite hardware, display, input, bus, or firmware backend."
    if name in DEFER:
        return "defer", note_override or "Needs source review before deciding whether it is portable or backend-specific."
    if surface == "operator":
        return "portable", "Operator/parser surface."
    return "defer", "Unclassified by rule; source review required before porting."


def surface_map(entries: list[Entry]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        result[entry.normalized].update(entry.surfaces)
    return result


def representative(entries: list[Entry], normalized: str) -> str:
    names = sorted({entry.name for entry in entries if entry.normalized == normalized}, key=lambda item: (len(item), item))
    return names[0] if names else normalized


def handlers(entries: list[Entry], normalized: str, surface: str) -> str:
    values = sorted(
        {entry.handler for entry in entries if entry.normalized == normalized and surface in entry.surfaces}
    )
    return ", ".join(values)


def build_gap_rows(picomite: list[Entry], mmb4l: list[Entry]) -> list[dict[str, str]]:
    pico_surfaces = surface_map(picomite)
    mmb_surfaces = surface_map(mmb4l)
    rows: list[dict[str, str]] = []
    for name in sorted(pico_surfaces):
        for surface in sorted(pico_surfaces[name], key=lambda item: SURFACE_ORDER.get(item, 99)):
            if surface in mmb_surfaces.get(name, set()):
                continue
            classification, note = classify_gap(name, surface)
            rows.append(
                {
                    "picomite": representative(picomite, name),
                    "normalized": name,
                    "missing_surface": surface,
                    "classification": classification,
                    "picomite_handlers": handlers(picomite, name, surface),
                    "mmb4l_surfaces": ", ".join(sorted(mmb_surfaces.get(name, set()))) or "-",
                    "notes": note,
                }
            )
    return rows


def md_code(value: str) -> str:
    escaped = value.replace("|", "\\|")
    return f"`{escaped}`"


def write_surface_markdown(path: pathlib.Path, title: str, entries: list[Entry]) -> None:
    entries = sorted(
        dedupe_entries(entries),
        key=lambda entry: (
            min(SURFACE_ORDER.get(surface, 99) for surface in entry.surfaces),
            entry.normalized,
            entry.name,
            entry.handler,
        ),
    )
    counts = Counter(surface for entry in entries for surface in entry.surfaces)
    lines = [
        f"# {title}",
        "",
        "Generated by `tools/language_audit.py`. Do not edit by hand.",
        "",
        "## Counts",
        "",
        "| Surface | Count |",
        "| --- | ---: |",
    ]
    for surface in sorted(counts, key=lambda item: SURFACE_ORDER.get(item, 99)):
        lines.append(f"| {surface} | {counts[surface]} |")
    lines.extend(
        [
            "",
            "## Entries",
            "",
            "| Name | Surface | Flags | Handler |",
            "| --- | --- | --- | --- |",
        ]
    )
    for entry in entries:
        lines.append(
            f"| {md_code(entry.name)} | {', '.join(entry.surfaces)} | "
            f"{md_code(entry.flags)} | {md_code(entry.handler)} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gap_markdown(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["classification"] for row in rows)
    lines = [
        "# PicoMite v6 to MMB4L Language Gap Table",
        "",
        "Generated by `tools/language_audit.py`. Do not edit by hand.",
        "",
        "A gap row means PicoMite exposes that surface and MMB4L does not expose the same normalized name as that surface.",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
    ]
    for classification in ("portable", "linux-specific", "hardware", "defer"):
        lines.append(f"| {classification} | {counts[classification]} |")
    lines.extend(
        [
            "",
            "## Gaps",
            "",
            "| PicoMite entry | Missing surface | Classification | PicoMite handler(s) | MMB4L same-name surfaces | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in sorted(rows, key=lambda item: (item["classification"], item["normalized"], item["missing_surface"])):
        lines.append(
            f"| {md_code(row['picomite'])} | {row['missing_surface']} | {row['classification']} | "
            f"{md_code(row['picomite_handlers'])} | {row['mmb4l_surfaces']} | {row['notes']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: pathlib.Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def entry_rows(entries: list[Entry]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for entry in dedupe_entries(entries):
        rows.append(
            {
                "source": entry.source,
                "table": entry.table,
                "name": entry.name,
                "normalized": entry.normalized,
                "surfaces": ",".join(entry.surfaces),
                "flags": entry.flags,
                "precedence": entry.precedence,
                "handler": entry.handler,
                "line": str(entry.line),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_picomite = os.environ.get("PICOMITE_ALLVERSIONS")
    parser.add_argument("--repo-root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument(
        "--picomite-root",
        type=pathlib.Path,
        default=pathlib.Path(default_picomite) if default_picomite else pathlib.Path.cwd().parent / "PicoMiteAllVersions",
        help="Path to PicoMiteAllVersions; defaults to PICOMITE_ALLVERSIONS or ../PicoMiteAllVersions.",
    )
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("docs/generated"))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    picomite_root = args.picomite_root.resolve()
    allcommands = picomite_root / "AllCommands.h"
    if not allcommands.exists():
        raise FileNotFoundError(f"Missing PicoMite AllCommands.h: {allcommands}")

    mmb4l = extract_entries(repo_root / "src/core/commandtbl.c", "MMB4L", "command") + extract_entries(
        repo_root / "src/core/tokentbl.c", "MMB4L", "token"
    )
    picomite = extract_picomite(allcommands)
    gap_rows = build_gap_rows(picomite, mmb4l)

    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_surface_markdown(output_dir / "language-surface-mmb4l.md", "MMB4L Language Surface", mmb4l)
    write_surface_markdown(output_dir / "language-surface-picomite-v6.md", "PicoMite v6 Language Surface", picomite)
    write_gap_markdown(output_dir / "language-gap-table.md", gap_rows)
    write_csv(output_dir / "language-surface-mmb4l.csv", entry_rows(mmb4l), list(entry_rows(mmb4l)[0]))
    write_csv(output_dir / "language-surface-picomite-v6.csv", entry_rows(picomite), list(entry_rows(picomite)[0]))
    write_csv(output_dir / "language-gap-table.csv", gap_rows, list(gap_rows[0]))

    print(f"MMB4L entries: {len(dedupe_entries(mmb4l))}")
    print(f"PicoMite entries: {len(dedupe_entries(picomite))}")
    print(f"Gap rows: {len(gap_rows)}")
    for classification, count in sorted(Counter(row["classification"] for row in gap_rows).items()):
        print(f"{classification}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
