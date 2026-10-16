"""Strict JSONL input and exact-ID label comparison."""

import json
from pathlib import Path
from typing import Any


class InvalidInput(Exception):
    """An input is invalid; its details must never reach user-visible output."""


def _reject_constant(_: str) -> None:
    raise InvalidInput


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput
        result[key] = value
    return result


def read_rows(path: str) -> list[tuple[str, str, int]]:
    """Read validated rows, preserving exact text and 1-based physical lines."""
    try:
        text = Path(path).read_bytes().decode("utf-8", errors="strict")
        lines = (
            text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
            if text
            else []
        )
        if lines and lines[-1] == "" and text.endswith(("\n", "\r")):
            lines.pop()
        rows: list[tuple[str, str, int]] = []
        seen: set[str] = set()
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                raise InvalidInput
            row = json.loads(
                line,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
            if not isinstance(row, dict) or set(row) != {"id", "label"}:
                raise InvalidInput
            row_id, label = row["id"], row["label"]
            if not isinstance(row_id, str) or row_id == "":
                raise InvalidInput
            if not isinstance(label, str) or label == "":
                raise InvalidInput
            if row_id in seen:
                raise InvalidInput
            seen.add(row_id)
            rows.append((row_id, label, line_number))
        return rows
    except InvalidInput:
        raise
    except Exception:
        raise InvalidInput from None


def compare(left: list[tuple[str, str, int]], right: list[tuple[str, str, int]]) -> dict[str, object]:
    left_by_id = {row_id: (label, line) for row_id, label, line in left}
    right_by_id = {row_id: (label, line) for row_id, label, line in right}
    left_only = sorted(line for row_id, _, line in left if row_id not in right_by_id)
    right_only = sorted(line for row_id, _, line in right if row_id not in left_by_id)
    shared = left_by_id.keys() & right_by_id.keys()
    disagreements = sorted(
        ((left_by_id[row_id][1], right_by_id[row_id][1])
         for row_id in shared if left_by_id[row_id][0] != right_by_id[row_id][0]),
        key=lambda item: item[0],
    )
    paired_count = len(shared)
    agreement_count = paired_count - len(disagreements)
    equal = not left_only and not right_only and not disagreements
    return {
        "status": "equal" if equal else "differences",
        "left_count": len(left),
        "right_count": len(right),
        "paired_count": paired_count,
        "agreement_count": agreement_count,
        "left_only_lines": left_only,
        "right_only_lines": right_only,
        "disagreements": [
            {"left_line": left_line, "right_line": right_line}
            for left_line, right_line in disagreements
        ],
    }
