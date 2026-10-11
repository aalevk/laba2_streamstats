from datetime import datetime, timezone

from streamstats.analysis import analyze_events
from streamstats.models import Event


def make_event(timestamp, level, source, message="test"):
    return Event(
        datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc),
        level,
        source,
        message,
    )


def test_empty_events():
    report = analyze_events([])

    assert report["total"] == 0
    assert report["by_source"] == {}
    assert report["errors_by_source"] == {}
    assert report["top_error_sources"] == []
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None


def test_event_counts():
    events = [
        make_event("2026-10-11T09:00:00", "INFO", "server"),
        make_event("2026-10-11T10:00:00", "ERROR", "database"),
        make_event("2026-10-11T11:00:00", "WARNING", "server"),
    ]

    report = analyze_events(events)

    assert report["total"] == 3
    assert report["by_level"]["INFO"] == 1
    assert report["by_level"]["ERROR"] == 1
    assert report["by_level"]["WARNING"] == 1
    assert report["by_source"] == {"server": 2, "database": 1}
    assert report["errors_by_source"] == {"database": 1}


def test_top_error_sources():
    events = [
        make_event("2026-10-11T09:00:00", "ERROR", "server"),
        make_event("2026-10-11T10:00:00", "CRITICAL", "server"),
        make_event("2026-10-11T11:00:00", "ERROR", "database"),
        make_event("2026-10-11T12:00:00", "INFO", "worker"),
    ]

    report = analyze_events(events)

    assert report["top_error_sources"] == [
        ("server", 2),
        ("database", 1),
    ]


def test_top_error_sources_limit_five():
    events = [
        make_event("2026-10-11T09:00:00", "ERROR", "source_f"),
        make_event("2026-10-11T09:01:00", "ERROR", "source_e"),
        make_event("2026-10-11T09:02:00", "ERROR", "source_d"),
        make_event("2026-10-11T09:03:00", "ERROR", "source_c"),
        make_event("2026-10-11T09:04:00", "ERROR", "source_b"),
        make_event("2026-10-11T09:05:00", "ERROR", "source_a"),
    ]

    report = analyze_events(events)

    assert len(report["top_error_sources"]) == 5
    assert report["top_error_sources"] == [
        ("source_a", 1),
        ("source_b", 1),
        ("source_c", 1),
        ("source_d", 1),
        ("source_e", 1),
    ]


def test_top_error_sources_tie_order():
    events = [
        make_event("2026-10-11T09:00:00", "ERROR", "zebra"),
        make_event("2026-10-11T09:01:00", "CRITICAL", "alpha"),
        make_event("2026-10-11T09:02:00", "ERROR", "middle"),
    ]

    report = analyze_events(events)

    assert report["top_error_sources"] == [
        ("alpha", 1),
        ("middle", 1),
        ("zebra", 1),
    ]


def test_first_and_last_timestamp():
    events = [
        make_event("2026-10-11T12:00:00", "INFO", "server"),
        make_event("2026-10-11T09:00:00", "INFO", "server"),
        make_event("2026-10-11T15:00:00", "INFO", "server"),
    ]

    report = analyze_events(events)

    assert report["first_timestamp"] == datetime(
        2026, 10, 11, 9, 0, tzinfo=timezone.utc
    )
    assert report["last_timestamp"] == datetime(
        2026, 10, 11, 15, 0, tzinfo=timezone.utc
    )