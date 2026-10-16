# label-pair-diff

Compare two categorical label JSONL files by exact record ID. The tool reports agreement, disagreement line numbers, and unpaired lines without exposing IDs or labels in its output.

This is a descriptive pair comparison. It is not a chance-corrected agreement statistic, a quality or accuracy judgment, an adjudicator, a ground-truth selector, or an annotation platform adapter. It makes no claim about which label is correct. Inputs are held in memory, so choose file sizes that fit available memory.

## Install

Python 3.10 or newer is required. Runtime code uses only the Python standard library.

```console
python -m venv .venv
```

Activate the environment, then install the test extra:

```console
python -m pip install -e ".[test]"
pytest
```

## Input format

Each file is strict UTF-8 JSON Lines: every physical line is one object with exactly two properties, `id` and `label`, both nonempty strings. IDs must be unique within each file. Empty files are valid. LF, CRLF, and CR line endings are supported. IDs and labels compare exactly as Unicode strings; there is no normalization. Blank lines, malformed JSON, duplicate object keys, non-standard JSON constants, invalid UTF-8, duplicate IDs, or missing/extra/wrong fields invalidate the whole run.

Both files are fully validated before a comparison result is printed. Invalid input produces only `{"status":"invalid_input"}` on stdout, no stderr, and exit code 2. No source content, IDs, paths, exception text, or hashes are printed. Counts and source line numbers are intentionally disclosed.

## Run

```console
label-pair-diff LEFT.jsonl RIGHT.jsonl
```

Exit code 0 means all rows pair and their labels match. Exit code 1 means there is at least one unpaired row or disagreement. Exit code 2 means either input is invalid or inaccessible. The JSON result includes row counts, paired and agreeing counts, sorted unpaired line numbers, and disagreements ordered by left line.

## Synthetic examples

These public fixtures contain no private or production data:

```console
label-pair-diff examples/equal-left.jsonl examples/equal-right.jsonl
label-pair-diff examples/differences-left.jsonl examples/differences-right.jsonl
label-pair-diff examples/invalid-left.jsonl examples/invalid-right.jsonl
```

The first exits 0 with status `equal`; the second exits 1 with status `differences`; the third exits 2 with exactly `{"status":"invalid_input"}`. Reordering rows does not affect ID pairing.
