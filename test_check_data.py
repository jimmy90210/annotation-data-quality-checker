"""Behavior tests using temporary, synthetic CSV data."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from check_data import check_csv, main


class DataQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "input.csv"

    def write(self, content):
        self.path.write_text(content, encoding="utf-8")
        return self.path

    def test_valid_bilingual_records_and_quoted_comma(self):
        report = check_csv(self.write('id,text,language,label\n1,"Good, thanks",en,positive\n2,Está aquí,es,neutral\n'))
        self.assertTrue(report["passed"])
        self.assertEqual(report["rows_checked"], 2)

    def test_sample_has_four_specific_issues(self):
        report = check_csv(Path(__file__).parent / "data" / "sample_annotations.csv")
        self.assertEqual(report["rows_checked"], 7)
        self.assertEqual([(i["row"], i["code"]) for i in report["issues"]], [
            (5, "duplicate_id"), (6, "missing_value"), (7, "invalid_value"), (8, "invalid_value")])

    def test_empty_file_and_missing_header(self):
        for content in ("", "id,text\n1,hello\n"):
            with self.subTest(content=content):
                report = check_csv(self.write(content))
                self.assertFalse(report["passed"])
                self.assertEqual(report["issues"][0]["code"], "missing_columns")

    def test_duplicate_header_is_rejected(self):
        report = check_csv(self.write("id,text,language,label,label\n"))
        self.assertEqual(report["issues"][0]["code"], "duplicate_columns")

    def test_short_and_long_records_are_flagged(self):
        for record in ("1,hello,en", "1,hello,en,neutral,extra"):
            with self.subTest(record=record):
                report = check_csv(self.write("id,text,language,label\n" + record + "\n"))
                self.assertIn("column_count_mismatch", [i["code"] for i in report["issues"]])

    def test_bom_whitespace_and_case_rules(self):
        report = check_csv(self.write("\ufeffid,text,language,label\n 1 , hello , en , neutral \n1,hello,EN,Neutral\n"))
        self.assertEqual([i["code"] for i in report["issues"]], ["duplicate_id", "invalid_value", "invalid_value"])

    def test_cli_writes_report_and_preserves_input(self):
        self.write("id,text,language,label\n1,hello,en,neutral\n")
        before = self.path.read_bytes()
        output = self.path.parent / "report.json"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path), "--output", str(output)]), 0)
        self.assertTrue(json.loads(output.read_text())["passed"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_cli_failure_codes(self):
        self.write("id,text,language,label\n1,,en,neutral\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([str(self.path)]), 1)
            self.assertEqual(main([str(self.path.parent / "missing.csv")]), 2)

    def test_cli_prevents_overwriting_input(self):
        self.write("id,text,language,label\n")
        before = self.path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main([str(self.path), "--output", str(self.path)])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
