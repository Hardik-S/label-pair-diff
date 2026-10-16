# Independent release review

**Issue:** [#3 — Independent frozen-contract release review](https://github.com/Hardik-S/label-pair-diff/issues/3)
**Reviewed commit:** `70943c24ccc7b84b513a86076f6a4dbfadd38701`
**Branch:** `issue1-strict-label-pair-diff`
**Review date:** 2026-10-16 (America/Toronto)

## Verdict

**PASS for the frozen `CONTRACT.md` and the requested pre-release checks.** This review does not publish a release or tag.

## Evidence

- Fresh Windows Python 3.13.1 virtual environment; `python -m pip install --disable-pip-version-check .[test]` built and installed `label-pair-diff==0.1.0` and its test extra successfully. The installed command was found at the environment's `sysconfig.get_path("scripts")` location (`Scripts\label-pair-diff.exe`).
- `python -m pytest -q -rs`: **18 passed, 0 skipped**.
- Installed console command against README fixtures:
  - Equal fixture: exit 0, `status=equal`.
  - Differences fixture: exit 1, `status=differences`.
  - Duplicate-ID invalid fixture: exit 2, stdout exactly `{"status":"invalid_input"}\n`.
- Additional installed-command adversarial run used reordered mixed CR/CRLF records, unequal labels, and unmatched records on both sides. It returned exit 1, paired by exact ID, sorted unpaired source lines, and ordered disagreements by left line. A malformed second input returned exit 2 with only the generic invalid JSON; the valid first input's sentinel ID and label were not emitted.
- Reviewed source and tests for strict UTF-8/JSONL parsing, duplicate JSON keys and IDs, non-standard constants, complete validation before output, exact Unicode comparison without normalization, empty inputs, and content-free diagnostics. README and launch checklist accurately describe the tested behavior, limitations, and the four-cell release gate.
- GitHub Actions at the reviewed SHA: all four latest matrix cells passed (`ubuntu-latest` and `windows-latest` on Python 3.10 and 3.13). Both latest CI runs, [38951774125](https://github.com/Hardik-S/label-pair-diff/actions/runs/38951774125) and [38951767801](https://github.com/Hardik-S/label-pair-diff/actions/runs/38951767801), show every matrix cell successful; the latter also shows GitGuardian successful. The earlier Windows console-path failure on `b2546f10b8d24b260675df01cc58121eda1038fc` is resolved by the reviewed `sysconfig.get_path("scripts")` lookup and current Windows checks are green.

## Commands and environment

- `python --version` → `Python 3.13.1`
- `python -m venv <fresh-temp-environment>`
- `<fresh-env>\Scripts\python.exe -m pip install --disable-pip-version-check .[test]`
- `<fresh-env>\Scripts\python.exe -m pytest -q -rs`
- `<fresh-env>\Scripts\label-pair-diff.exe examples\equal-left.jsonl examples\equal-right.jsonl` (and the differences and invalid fixture pairs)
- GitHub check-runs API for commit `70943c24ccc7b84b513a86076f6a4dbfadd38701`.

## Gaps and limits

- The local fresh-install run was on Windows with Python 3.13.1 only; the other supported OS/version combinations are covered by hosted CI evidence above.
- No production, private, or real annotation data was used. The tool is memory-resident and provides descriptive agreement only; it does not assess label quality, choose ground truth, adjudicate, or calculate chance-corrected agreement.
- Review is limited to the requested contract/release gate at the stated commit. It is not a security audit or release publication.
