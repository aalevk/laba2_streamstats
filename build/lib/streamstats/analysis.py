def get_top_sources(error_counts, limit=5):
    top = sorted(error_counts.items(),key=lambda item: (-item[1], item[0]))[:limit]
    return top


def analyze_events(events):
    total = 0
    level_counts = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0
    }
    source_counts = {}
    error_counts = {}
    first_timestamp = None
    last_timestamp = None

    for event in events:

        total += 1

        level_counts[event.level] += 1

        if event.source not in source_counts:
            source_counts[event.source] = 0

        source_counts[event.source] += 1

        if event.level in {"ERROR", "CRITICAL"}:
            if event.source not in error_counts:
                error_counts[event.source] = 0

            error_counts[event.source] += 1

        if first_timestamp is None or event.timestamp < first_timestamp:
            first_timestamp = event.timestamp

        if last_timestamp is None or event.timestamp > last_timestamp:
            last_timestamp = event.timestamp

    return {
        "total": total,
        "by_level": level_counts,
        "by_source": source_counts,
        "errors_by_source": error_counts,
        "top_error_sources": get_top_sources(error_counts),
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
    }
