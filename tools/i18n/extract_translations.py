#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCENE_PATTERN = re.compile(
    r'(?m)^(?:text|title|tooltip_text|placeholder_text|popup/item_\d+/text)\s*=\s*"((?:\\.|[^"\\])*)"'
)
CODE_PATTERNS = (
    re.compile(r'RTR\(\s*"((?:\\.|[^"\\])*)"\s*\)'),
    re.compile(r'\btr\(\s*"((?:\\.|[^"\\])*)"\s*\)'),
)
CONFIG_SETTING_PATTERN = re.compile(
    r'GDREConfigSetting(?:Enum|Range)?\(\s*"((?:\\.|[^"\\])*)"\s*,\s*'
    r'"((?:\\.|[^"\\])*)"\s*,\s*"((?:\\.|[^"\\])*)"',
    re.DOTALL,
)
CONFIG_ENUM_PATTERN = re.compile(
    r'GDREConfigSettingEnum\(\s*"(?:\\.|[^"\\])*"\s*,\s*'
    r'"(?:\\.|[^"\\])*"\s*,\s*"(?:\\.|[^"\\])*"\s*,\s*[^,]+,\s*'
    r'"((?:\\.|[^"\\])*)"',
    re.DOTALL,
)
CONFIG_VALUE_PATTERN = re.compile(r'ret\[[^\]]+\]\s*=\s*"((?:\\.|[^"\\])*)"')
ESCAPE_PATTERN = re.compile(r'\\([\\"nrt])')


def decode_string(value: str) -> str:
    replacements = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t"}
    return ESCAPE_PATTERN.sub(lambda match: replacements[match.group(1)], value)


def po_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def collect_messages() -> dict[str, set[str]]:
    messages: dict[str, set[str]] = defaultdict(set)

    for path in sorted((ROOT / "standalone").rglob("*.tscn")):
        content = path.read_text(encoding="utf-8")
        for match in SCENE_PATTERN.finditer(content):
            message = decode_string(match.group(1)).strip()
            if message:
                line = content.count("\n", 0, match.start()) + 1
                messages[message].add(f"{path.relative_to(ROOT).as_posix()}:{line}")

    code_files = [
        *ROOT.rglob("*.cpp"),
        *ROOT.rglob("*.h"),
        *(ROOT / "standalone").rglob("*.gd"),
    ]
    for path in sorted(set(code_files)):
        if "thirdparty" in path.parts or ".git" in path.parts:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for pattern in CODE_PATTERNS:
            for match in pattern.finditer(content):
                message = decode_string(match.group(1)).strip()
                if message:
                    line = content.count("\n", 0, match.start()) + 1
                    messages[message].add(f"{path.relative_to(ROOT).as_posix()}:{line}")

    config_path = ROOT / "utility" / "gdre_config.cpp"
    config_content = config_path.read_text(encoding="utf-8")
    for match in CONFIG_SETTING_PATTERN.finditer(config_content):
        line = config_content.count("\n", 0, match.start()) + 1
        full_name = decode_string(match.group(1)).strip()
        for section_name in full_name.split("/")[:-1]:
            if section_name:
                messages[section_name].add(f"utility/gdre_config.cpp:{line}")
        for raw_message in match.groups()[1:]:
            message = decode_string(raw_message).strip()
            if message:
                messages[message].add(f"utility/gdre_config.cpp:{line}")
    for match in CONFIG_ENUM_PATTERN.finditer(config_content):
        line = config_content.count("\n", 0, match.start()) + 1
        for raw_message in match.group(1).split(","):
            message = decode_string(raw_message).strip()
            if message:
                messages[message].add(f"utility/gdre_config.cpp:{line}")
    for match in CONFIG_VALUE_PATTERN.finditer(config_content):
        message = decode_string(match.group(1)).strip()
        if message:
            line = config_content.count("\n", 0, match.start()) + 1
            messages[message].add(f"utility/gdre_config.cpp:{line}")

    return messages


def render_pot(messages: dict[str, set[str]]) -> str:
    lines = [
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: GDRE Tools v2.6.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        "",
    ]
    for message in sorted(messages, key=str.casefold):
        for reference in sorted(messages[message]):
            lines.append(f"#: {reference}")
        lines.append(f"msgid {po_quote(message)}")
        lines.append('msgstr ""')
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract GDRE Tools UI messages into a POT file.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "standalone" / "translations" / "gdre_tools.pot",
    )
    args = parser.parse_args()

    messages = collect_messages()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_pot(messages), encoding="utf-8", newline="\n")
    print(f"Extracted {len(messages)} messages to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
