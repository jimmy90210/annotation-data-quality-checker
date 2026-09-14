"""Check annotation CSV structure and values without changing source data."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED_FIELDS = ("id", "text", "language", "label")
ALLOWED_LANGUAGES = {"en", "es"}
ALLOWED_LABELS = {"positive", "neutral", "negative"}


def check_csv(path):
    """Return a JSON-serializable report; row numbers count CSV records."""
    issues = []
    seen_ids = set()
    rows_checked = 0
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        headers = reader.fieldnames or []
        missing = sorted(set(REQUIRED_FIELDS) - set(headers))
        duplicates = sorted(name for name, count in Counter(headers).items() if count > 1)
        if missing or duplicates:
            if missing:
                issues.append({"row": 1, "code": "missing_columns", "fields": missing})
            if duplicates:
                issues.append({"row": 1, "code": "duplicate_columns", "fields": duplicates})
        else:
            for row_number, row in enumerate(reader, start=2):
                rows_checked += 1
                if None in row or any(value is None for value in row.values()):
                    issues.append({"row": row_number, "code": "column_count_mismatch"})
                values = {field: (row.get(field) or "").strip() for field in REQUIRED_FIELDS}
                for field, value in values.items():
                    if not value:
                        issues.append({"row": row_number, "code": "missing_value", "field": field})
                record_id = values["id"]
                if record_id:
                    if record_id in seen_ids:
                        issues.append({"row": row_number, "code": "duplicate_id", "field": "id"})
                    seen_ids.add(record_id)
                for field, allowed in (("language", ALLOWED_LANGUAGES), ("label", ALLOWED_LABELS)):
                    if values[field] and values[field] not in allowed:
                        issues.append({"row": row_number, "code": "invalid_value", "field": field})
    return {
        "rows_checked": rows_checked,
        "issue_count": len(issues),
        "passed": not issues,
        "issues": issues,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 CSV to check")
    parser.add_argument("--output", type=Path, help="Save the JSON report to a separate file")
    args = parser.parse_args(argv)
    if args.output and args.input.resolve() == args.output.resolve():
        parser.error("Output must be different from the input file.")
    try:
        report = check_csv(args.input)
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Unable to check data: {error}", file=sys.stderr)
        return 2
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
