import csv
import json
import logging
from datetime import datetime, timezone
from json import JSONDecodeError

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import Event

VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
REQUIRED_FIELDS = {"timestamp", "level", "source", "message"}


def parse_csv(path, skip_invalid=False, skipped=None):
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            line_number = reader.line_num

            try:
                yield parse_event(row, path, line_number)
            except (InvalidEventError, InvalidTimestampError) as error:
                if not skip_invalid:
                    raise

                logging.warning("%s", error)
                if skipped is not None:
                    skipped[0] += 1


def parse_jsonl(path, skip_invalid=False, skipped=None):
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                row = json.loads(line)
                yield parse_event(row, path, line_number)
            except JSONDecodeError as error:
                invalid_error = InvalidEventError(
                    f"{path}: строка {line_number}: некорректный JSON"
                )
                if not skip_invalid:
                    raise invalid_error from error

                logging.warning("%s", invalid_error)
                if skipped is not None:
                    skipped[0] += 1
            except (InvalidEventError, InvalidTimestampError) as error:
                if not skip_invalid:
                    raise

                logging.warning("%s", error)
                if skipped is not None:
                    skipped[0] += 1


def parse_event(row, path, line_number):
    if not isinstance(row, dict):
        raise InvalidEventError(
            f"{path}: строка {line_number}: ожидался JSON-объект"
        )

    missing_fields = REQUIRED_FIELDS - row.keys()
    if missing_fields:
        raise InvalidEventError(
            f"{path}: строка {line_number}: отсутствуют поля {missing_fields}"
        )

    timestamp = row["timestamp"]
    if not isinstance(timestamp, str):
        raise InvalidTimestampError(
            f"{path}: строка {line_number}: timestamp должен быть строкой"
        )

    level = row["level"]
    if not isinstance(level, str):
        raise InvalidEventError(
            f"{path}: строка {line_number}: level должен быть строкой"
        )

    source = row["source"]
    if not isinstance(source, str):
        raise InvalidEventError(
            f"{path}: строка {line_number}: source должен быть строкой"
        )

    message = row["message"]
    if not isinstance(message, str):
        raise InvalidEventError(
            f"{path}: строка {line_number}: message должен быть строкой"
        )

    try:
        parsed_timestamp = datetime.fromisoformat(timestamp)
    except ValueError as error:
        raise InvalidTimestampError(
            f"{path}: строка {line_number}: некорректный timestamp"
        ) from error

    if parsed_timestamp.tzinfo is None:
        parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
    else:
        parsed_timestamp = parsed_timestamp.astimezone(timezone.utc)

    if level not in VALID_LEVELS:
        raise InvalidEventError(
            f"{path}: строка {line_number}: некорректный level"
        )

    if not source.strip():
        raise InvalidEventError(
            f"{path}: строка {line_number}: некорректный source"
        )

    return Event(parsed_timestamp, level, source, message)