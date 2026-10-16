# Launch checklist

1. Create a clean Python 3.10+ environment and install `python -m pip install .[test]`.
2. Run `pytest`; the suite must execute without skipped tests.
3. From the installed environment, run each of the three commands in README.md. Confirm the equal example exits 0, the differences example exits 1, and the duplicate-ID example exits 2 with only `{"status":"invalid_input"}` on stdout.
4. Review the output against the README: no IDs, labels, paths, hashes, or exception text should appear.
5. Publish tag `v0.1.0` only after the full Ubuntu and Windows Python 3.10 and 3.13 CI matrix passes. This repository change does not itself create a release.
