import json
from datetime import datetime, timezone

from streamstats.report import write_report


def test_write_report(tmp_path):
    path = tmp_path / "report.json"
    report = {
        "total": 1,
        "by_level": {"INFO": 1},
        "by_source": {"сервер": 1},
        "errors_by_source": {},
        "top_error_sources": [],
        "first_timestamp": datetime(
            2026, 10, 11, 9, 0, tzinfo=timezone.utc
        ),
        "last_timestamp": datetime(
            2026, 10, 11, 9, 0, tzinfo=timezone.utc
        ),
        "skipped_rows": 0,
        "message": "Запуск программы",
    }

    write_report(report, path)

    saved = json.loads(path.read_text(encoding="utf-8"))

    assert saved["total"] == 1
    assert saved["by_source"] == {"сервер": 1}
    assert saved["message"] == "Запуск программы"
    assert saved["first_timestamp"] == "2026-10-11T09:00:00+00:00"
    assert saved["last_timestamp"] == "2026-10-11T09:00:00+00:00"


def test_write_empty_report(tmp_path):
    path = tmp_path / "report.json"
    report = {
        "total": 0,
        "by_level": {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        },
        "by_source": {},
        "errors_by_source": {},
        "top_error_sources": [],
        "first_timestamp": None,
        "last_timestamp": None,
        "skipped_rows": 0,
    }

    write_report(report, path)

    saved = json.loads(path.read_text(encoding="utf-8"))

    assert saved["total"] == 0
    assert saved["first_timestamp"] is None
    assert saved["last_timestamp"] is None