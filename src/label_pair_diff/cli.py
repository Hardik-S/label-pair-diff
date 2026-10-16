"""Command-line entry point; all diagnostics are deliberately content-free."""

import argparse
import json
import sys

from .core import InvalidInput, compare, read_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="label-pair-diff",
        description="Compare categorical labels paired by exact ID without displaying source content.",
    )
    parser.add_argument("left", help="left JSONL input")
    parser.add_argument("right", help="right JSONL input")
    args = parser.parse_args()
    try:
        left = read_rows(args.left)
        right = read_rows(args.right)
    except InvalidInput:
        print('{"status":"invalid_input"}')
        return 2
    result = compare(left, right)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["status"] == "equal" else 1


if __name__ == "__main__":
    sys.exit(main())
