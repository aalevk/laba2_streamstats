import json
import os
import subprocess
import sys


def run_cli(*args):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    return subprocess.run(
        [sys.executable, "-m", "streamstats", "analyze", *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def test_cli_multiple_files(tmp_path):
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    output = tmp_path / "report.json"

    first.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"сервер","message":"Запуск"}\n',
        encoding="utf-8",
    )
    second.write_text(
        '{"timestamp":"2026-10-11T10:00:00Z",'
        '"level":"ERROR","source":"база","message":"Ошибка"}\n',
        encoding="utf-8",
    )

    result = run_cli(
        first, second, "--format", "jsonl", "--output", output
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["total"] == 2
    assert report["by_source"] == {"сервер": 1, "база": 1}


def test_cli_invalid_json_returns_two(tmp_path):
    source = tmp_path / "broken.jsonl"
    output = tmp_path / "report.json"

    source.write_text("invalid json\n", encoding="utf-8")

    result = run_cli(
        source, "--format", "jsonl", "--output", output
    )

    assert result.returncode == 2
    assert "строка 1" in result.stderr
    assert not output.exists()


def test_cli_skip_invalid(tmp_path):
    source = tmp_path / "mixed.jsonl"
    output = tmp_path / "report.json"

    source.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"server","message":"OK"}\n'
        "invalid json\n",
        encoding="utf-8",
    )

    result = run_cli(
        source,
        "--format", "jsonl",
        "--output", output,
        "--skip-invalid",
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["total"] == 1
    assert report["skipped_rows"] == 1


def test_csv_and_jsonl_give_same_statistics(tmp_path):
    csv_file = tmp_path / "events.csv"
    jsonl_file = tmp_path / "events.jsonl"
    csv_report = tmp_path / "csv_report.json"
    jsonl_report = tmp_path / "jsonl_report.json"

    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-11T09:00:00Z,INFO,сервер,Запуск\n"
        "2026-10-11T10:00:00Z,ERROR,база,Ошибка\n",
        encoding="utf-8",
    )
    jsonl_file.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"сервер","message":"Запуск"}\n'
        '{"timestamp":"2026-10-11T10:00:00Z",'
        '"level":"ERROR","source":"база","message":"Ошибка"}\n',
        encoding="utf-8",
    )

    csv_result = run_cli(
        csv_file, "--format", "csv", "--output", csv_report
    )
    jsonl_result = run_cli(
        jsonl_file, "--format", "jsonl", "--output", jsonl_report
    )

    assert csv_result.returncode == 0
    assert jsonl_result.returncode == 0

    csv_data = json.loads(csv_report.read_text(encoding="utf-8"))
    jsonl_data = json.loads(jsonl_report.read_text(encoding="utf-8"))

    assert csv_data == jsonl_data


def test_empty_file_creates_empty_report(tmp_path):
    source = tmp_path / "empty.jsonl"
    output = tmp_path / "report.json"
    source.write_text("", encoding="utf-8")

    result = run_cli(
        source, "--format", "jsonl", "--output", output
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["total"] == 0
    assert report["by_source"] == {}
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None


def test_source_file_is_not_changed(tmp_path):
    source = tmp_path / "events.jsonl"
    output = tmp_path / "report.json"
    original_text = (
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"сервер","message":"Запуск"}\n'
    )
    source.write_text(original_text, encoding="utf-8")

    result = run_cli(
        source, "--format", "jsonl", "--output", output
    )

    assert result.returncode == 0
    assert source.read_text(encoding="utf-8") == original_text