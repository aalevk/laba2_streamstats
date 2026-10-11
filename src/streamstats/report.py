import json


def write_report(report, output_path):
    copy_report = report.copy()

    for key in ("first_timestamp", "last_timestamp"):
        if copy_report[key] is not None:
            copy_report[key] = copy_report[key].isoformat()

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(copy_report, file, ensure_ascii=False, indent=2)