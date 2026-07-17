#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER_PATTERN = re.compile(r"<[A-Z][A-Z0-9_]*>|%(?:\d+\$)?[sdi]|\{[A-Za-z_][A-Za-z0-9_]*\}")


def parse_po(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    current: dict[str, list[str]] = {"msgid": [], "msgstr": []}
    active: str | None = None

    def flush() -> None:
        nonlocal current, active
        message_id = "".join(current["msgid"])
        message_text = "".join(current["msgstr"])
        if message_id:
            entries.append((message_id, message_text))
        current = {"msgid": [], "msgstr": []}
        active = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid "):
            active = "msgid"
            current[active].append(ast.literal_eval(line[6:]))
        elif line.startswith("msgstr "):
            active = "msgstr"
            current[active].append(ast.literal_eval(line[7:]))
        elif line.startswith('"') and active:
            current[active].append(ast.literal_eval(line))
    flush()
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a GDRE Tools PO translation.")
    parser.add_argument(
        "translation",
        type=Path,
        nargs="?",
        default=ROOT / "standalone" / "translations" / "gdre_tools.zh_CN.po",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=ROOT / "standalone" / "translations" / "gdre_tools.pot",
    )
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    entries = parse_po(args.translation)
    template_entries = parse_po(args.template)
    template_messages = {message_id for message_id, _ in template_entries}
    errors: list[str] = []
    seen: set[str] = set()
    translated = 0

    for message_id, message_text in entries:
        if message_id in seen:
            errors.append(f"Duplicate msgid: {message_id!r}")
        seen.add(message_id)
        if not message_text:
            if args.require_complete:
                errors.append(f"Missing translation: {message_id!r}")
            continue
        translated += 1
        source_placeholders = sorted(PLACEHOLDER_PATTERN.findall(message_id))
        target_placeholders = sorted(PLACEHOLDER_PATTERN.findall(message_text))
        if source_placeholders != target_placeholders:
            errors.append(
                f"Placeholder mismatch for {message_id!r}: "
                f"source={source_placeholders}, target={target_placeholders}"
            )

    unknown_messages = seen - template_messages
    for message_id in sorted(unknown_messages):
        errors.append(f"Translation msgid is not present in template: {message_id!r}")

    missing_messages = template_messages - seen
    if args.require_complete:
        for message_id in sorted(missing_messages):
            errors.append(f"Missing template msgid: {message_id!r}")

    total_messages = len(template_messages)
    coverage = 100.0 if not total_messages else translated * 100.0 / total_messages
    print(f"Translation coverage: {translated}/{total_messages} ({coverage:.1f}%)")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
