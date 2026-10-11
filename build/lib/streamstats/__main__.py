import argparse
import logging
import sys

from streamstats.analysis import analyze_events
from streamstats.errors import StreamStatsError
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import write_report


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("inputs", nargs="+")
    analyze_parser.add_argument(
        "--format", choices=["csv", "jsonl"], required=True
    )
    analyze_parser.add_argument("--output", required=True)
    analyze_parser.add_argument("--skip-invalid", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    skipped = [0]

    def events():
        for path in args.inputs:
            if args.format == "csv":
                read_events = parse_csv(path, args.skip_invalid, skipped)
            else:
                read_events = parse_jsonl(path, args.skip_invalid, skipped)

            yield from read_events

    try:
        report = analyze_events(events())
        report["skipped_rows"] = skipped[0]
        write_report(report, args.output)
    except (StreamStatsError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())