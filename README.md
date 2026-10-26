# CSV-Fixer: CSV Cleaning Tool

CSV-Fixer is a small Python tool for cleaning and standardizing CSV files. It is intended for clearly defined, reviewable data-cleaning tasks.

## Features

- **Delimiter detection:** Tries to detect comma, semicolon, tab, or pipe delimiters. You can also pass a delimiter explicitly when calling `repair_csv`.
- **Encoding detection:** Uses `chardet` to guess the input encoding and tries common fallbacks.
- **Whitespace trimming:** Removes leading and trailing whitespace from cell values.
- **Duplicate removal:** Removes rows that are identical after outer whitespace has been trimmed.
- **Identifier-safe reading:** Reads values as text so Pandas does not automatically convert IDs, postal codes, or phone numbers to numbers and discard leading zeros that are present in the source.
- **Basic identifier cleanup:** Removes a trailing `.0` from digit-only values in columns whose names indicate phone, ZIP/postal code, or ID fields.
- **Email format review:** Performs a basic format check and reports suspicious email values. It preserves those values instead of guessing how to rewrite them.
- **Standardized export:** Writes a comma-separated UTF-8 CSV without an extra DataFrame index column.

## Important limitations

- CSV-Fixer cannot reliably reconstruct a leading zero that is already missing from the source. Provide the correct source data or a known field length if such repair is needed.
- Encoding detection is a best-effort guess; ambiguous files may need manual review.
- Delimiter detection is a heuristic and can be uncertain for unusual files.
- Email checks only flag suspicious syntax. They do not verify whether an email address exists or can receive messages.
- The tool does not currently restore mojibake (text that was already decoded with the wrong encoding) in every case.
- Always review the output before using it for business-critical records.

## Requirements

- Python 3.10 or newer is recommended.
- pandas
- chardet

Install dependencies:

```bash
python -m pip install pandas chardet
```

## Run the example

From the repository folder, generate the sample input:

```bash
python generate_dirty_csv.py
```

Then run CSV-Fixer:

```bash
python main.py
```

The input sample is read from `examples/broken_leads_dirty.csv`. The cleaned output is written to `examples/fixed_leads_clean.csv`.

## Use it on another file

Edit the input and output paths in the `if __name__ == "__main__"` section of `main.py`, or import and call the function:

```python
from main import repair_csv

repair_csv("input.csv", "output.csv")
```

To specify a delimiter explicitly:

```python
repair_csv("input.csv", "output.csv", current_delimiter=";")
```

## Project purpose

CSV-Fixer is a personal project and a starting point for simple CSV cleaning tasks. Check the input and output carefully, especially when handling identifiers, contact details, or other important data.
