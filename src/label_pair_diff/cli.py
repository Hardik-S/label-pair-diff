"""Command-line entry point; all diagnostics are deliberately content-free."""

import argparse
import json
import sys

from .core import InvalidInput, compare, read_rows


class _QuietArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # Default diagnostics may echo private paths or arbitrary caller values.
        raise InvalidInput


def main() -> int:
    parser = _QuietArgumentParser(
        prog="label-pair-diff",
        description="Compare categorical labels paired by exact ID without displaying source content.",
    )
    parser.add_argument("left", help="left JSONL input")
    parser.add_argument("right", help="right JSONL input")
    try:
        args = parser.parse_args()
        inputs = []
        invalid = False
        # Attempt each complete file even when its peer is invalid.
        for path in (args.left, args.right):
            try:
                inputs.append(read_rows(path))
            except InvalidInput:
                invalid = True
        if invalid:
            raise InvalidInput
        left, right = inputs
    except InvalidInput:
        print('{"status":"invalid_input"}')
        return 2
    result = compare(left, right)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["status"] == "equal" else 1


if __name__ == "__main__":
    sys.exit(main())
