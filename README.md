# Annotation Data Quality Checker

A small Python command-line project for checking CSV annotation data before review or analysis. It demonstrates file handling, validation rules, structured reporting, and automated tests using only the Python standard library.

This is a beginner portfolio exercise created with AI assistance. The examples are synthetic and do not represent client work or professional AI experience.

## What it checks

- Required columns: `id`, `text`, `language`, `label`.
- Duplicate column names and inconsistent numbers of fields.
- Empty or whitespace-only required values.
- Duplicate IDs after trimming surrounding whitespace (later occurrences are flagged).
- Language codes: `en` or `es`.
- Sentiment labels: `positive`, `neutral`, or `negative`.

Values are checked after trimming surrounding whitespace; codes and labels are case-sensitive. Extra named columns are allowed. Input files are never rewritten.

## Run it

Use Python 3.10 or newer. No packages or API keys are needed. Download the repository ZIP and extract it, or clone the repository, then open a terminal in its folder.

```sh
python check_data.py data/sample_annotations.csv
python check_data.py data/sample_annotations.csv --output report.json
python check_data.py data/valid_annotations.csv
python -m unittest -v
```

On Windows, use `py` if `python` is unavailable; on macOS/Linux, use `python3` if needed.

The deliberately flawed sample has **7 records and 4 issues**: a duplicate ID, empty text, an invalid label, and an invalid language code. Its expected report is saved in [`examples/sample_report.json`](examples/sample_report.json). The valid sample has **4 records and 0 issues**.

Exit codes: `0` means validation passed, `1` means quality issues were found, and `2` means a file, parsing, or command-line error. The flawed sample intentionally exits with `1`.

## Example workflow

1. Run the checker on a CSV.
2. Review each issue in the JSON report.
3. Check the source and annotation guidelines before making corrections.
4. Rerun the checker after editing your own copy of the data.

The report uses CSV record numbers, with the header counted as row 1. A quoted text field can span multiple physical lines, so these are not always editor line numbers. One record can have several issues; `issue_count` counts findings, not affected records. When headers are invalid, validation stops before data records are checked.

## Scope and limitations

This tool checks structure and permitted values. It cannot determine whether a sentiment label is accurate or whether text actually matches its language code. Those decisions require human review. A correctly structured file with only a header passes with zero records; whether an empty dataset is acceptable depends on the workflow. The tool is intended for small practice datasets and keeps the issue report and unique IDs in memory.

## Files

- `check_data.py` — validation logic and command-line interface.
- `test_check_data.py` — tests for validation, reporting, exit codes, and protecting the input file.
- `data/` — synthetic English/Spanish practice datasets.
- `examples/` — reproducible sample output.

## Possible next steps

- Allow label choices to come from a configuration file.
- Add a summary of issue types.
- Add checks for conflicting labels on repeated text.

These are future ideas, not implemented features.
