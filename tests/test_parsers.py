import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_valid_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"сервер","message":"Запуск"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(path))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "сервер"
    assert events[0].message == "Запуск"


def test_invalid_jsonl_stops_by_default(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"server","message":"OK"}\n'
        "invalid json\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError, match="строка 2"):
        list(parse_jsonl(path))


def test_invalid_jsonl_on_line_seven(tmp_path):
    path = tmp_path / "events.jsonl"
    valid_line = (
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"server","message":"OK"}\n'
    )
    path.write_text(
        valid_line * 6 + "invalid json\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError, match="строка 7"):
        list(parse_jsonl(path))


def test_skip_invalid_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-11T09:00:00Z",'
        '"level":"INFO","source":"server","message":"OK"}\n'
        "invalid json\n"
        '{"timestamp":"2026-10-11T10:00:00Z",'
        '"level":"ERROR","source":"database","message":"Failed"}\n',
        encoding="utf-8",
    )

    skipped = [0]
    events = list(parse_jsonl(path, skip_invalid=True, skipped=skipped))

    assert len(events) == 2
    assert [event.source for event in events] == ["server", "database"]
    assert skipped[0] == 1


def test_invalid_timestamp(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"not-a-date","level":"INFO",'
        '"source":"server","message":"OK"}\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidTimestampError, match="строка 1"):
        list(parse_jsonl(path))


def test_parse_valid_csv(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-11T09:00:00Z,INFO,server,Started\n",
        encoding="utf-8",
    )

    events = list(parse_csv(path))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "server"
    assert events[0].message == "Started"


def test_skip_invalid_csv(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "not-a-date,INFO,server,Bad date\n"
        "2026-10-11T10:00:00Z,ERROR,database,Failed\n",
        encoding="utf-8",
    )

    skipped = [0]
    events = list(parse_csv(path, skip_invalid=True, skipped=skipped))

    assert len(events) == 1
    assert events[0].source == "database"
    assert skipped[0] == 1