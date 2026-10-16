import json
from pathlib import Path
import os
import subprocess
import sys

import pytest

from label_pair_diff.core import InvalidInput, compare, read_rows


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


def run_cli(left, right):
    return subprocess.run(
        [sys.executable, "-m", "label_pair_diff.cli", str(left), str(right)],
        text=True, capture_output=True, check=False,
    )


def test_empty_inputs_are_equal(tmp_path):
    a, b = write(tmp_path, "a", b""), write(tmp_path, "b", b"")
    result = run_cli(a, b)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "status": "equal", "left_count": 0, "right_count": 0,
        "paired_count": 0, "agreement_count": 0, "left_only_lines": [],
        "right_only_lines": [], "disagreements": [],
    }


def test_pairs_by_exact_id_and_reports_sorted_lines(tmp_path):
    left = write(tmp_path, "left", '{"id":"z","label":"same"}\n{"id":"a","label":"old"}\n{"id":"gone","label":"x"}\n{"id":"b","label":"old"}\n')
    right = write(tmp_path, "right", '{"id":"b","label":"new"}\n{"id":"a","label":"new"}\n{"id":"new","label":"x"}\n{"id":"z","label":"same"}\n')
    result = run_cli(left, right)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "status": "differences", "left_count": 4, "right_count": 4,
        "paired_count": 3, "agreement_count": 1, "left_only_lines": [3],
        "right_only_lines": [3],
        "disagreements": [{"left_line": 2, "right_line": 2}, {"left_line": 4, "right_line": 1}],
    }


def test_exact_unicode_and_newline_variants(tmp_path):
    left = write(tmp_path, "left", '{"id":"é","label":"café"}\r{"id":"é","label":"café"}\r')
    right = write(tmp_path, "right", '{"id":"é","label":"café"}\r\n{"id":"é","label":"café"}')
    assert compare(read_rows(str(left)), read_rows(str(right)))["status"] == "equal"


@pytest.mark.parametrize("bad", [
    b"\n", b"{}\n", b'{"id":"x","label":"y","extra":0}\n',
    b'{"id":"x","id":"z","label":"secret"}\n',
    b'{"id":"x","label":"secret"}\n{"id":"x","label":"again"}\n',
    b'{"id":"x","label":""}\n', b'{"id":"x","label":NaN}\n',
    b'{"id":"x","label":"ok"}\nnot-json\n', b'{"id":"x","label":"ok"}\n\xff',
])
def test_invalid_input_has_exact_content_free_response(tmp_path, bad):
    left, right = write(tmp_path, "left", bad), write(tmp_path, "right", b"")
    result = run_cli(left, right)
    assert result.returncode == 2
    assert result.stdout == '{"status":"invalid_input"}\n'
    assert result.stderr == ""
    assert "secret" not in result.stdout + result.stderr


def test_invalid_second_file_produces_no_partial_result(tmp_path):
    left = write(tmp_path, "left", '{"id":"private-id","label":"private-label"}\n')
    right = write(tmp_path, "right", b"{bad")
    result = run_cli(left, right)
    assert result.returncode == 2
    assert result.stdout == '{"status":"invalid_input"}\n'
    assert "private" not in result.stdout + result.stderr


def test_missing_file_is_invalid_without_echoing_path(tmp_path):
    missing = tmp_path / "sensitive-path-name"
    result = run_cli(missing, write(tmp_path, "right", b""))
    assert result.returncode == 2
    assert result.stdout == '{"status":"invalid_input"}\n'
    assert result.stderr == ""
    assert "sensitive-path-name" not in result.stdout


def test_malformed_direct_parser_error_is_generic(tmp_path):
    path = write(tmp_path, "bad", b"{")
    with pytest.raises(InvalidInput):
        read_rows(str(path))


@pytest.mark.parametrize("left_name,right_name,exit_code,status", [
    ("equal-left.jsonl", "equal-right.jsonl", 0, "equal"),
    ("differences-left.jsonl", "differences-right.jsonl", 1, "differences"),
    ("invalid-left.jsonl", "invalid-right.jsonl", 2, "invalid_input"),
])
def test_installed_console_command(left_name, right_name, exit_code, status):
    command = Path(sys.executable).with_name(
        "label-pair-diff.exe" if os.name == "nt" else "label-pair-diff"
    )
    assert command.is_file()
    examples = Path(__file__).parents[1] / "examples"
    result = subprocess.run(
        [str(command), str(examples / left_name), str(examples / right_name)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == exit_code
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == status
    if status == "invalid_input":
        assert result.stdout == '{"status":"invalid_input"}\n'
