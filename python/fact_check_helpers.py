from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NUMBER_RE = re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?(?:\s?%)?")


def load_facts(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_values(value) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(flatten_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(flatten_values(item))
        return values
    return [str(value)]


def extract_numbers(text: str) -> set[str]:
    return {match.group(0).replace(",", ".").replace(" ", "") for match in NUMBER_RE.finditer(text)}


def numbers_in_facts(facts: dict) -> set[str]:
    return extract_numbers("\n".join(flatten_values(facts)))


def numbers_in_draft(path: Path) -> set[str]:
    return extract_numbers(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find numbers in a draft that are not present in facts.")
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    facts_numbers = numbers_in_facts(load_facts(args.facts))
    draft_numbers = numbers_in_draft(args.draft)
    extra = sorted(draft_numbers - facts_numbers)

    if extra:
        print("Numbers present in draft but not in facts:")
        for number in extra:
            print(f"- {number}")
        return 1

    print("No extra numbers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

