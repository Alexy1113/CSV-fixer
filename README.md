# CSV-Fixer: CSV Cleaning Tool

CSV-Fixer is a small Python project that cleans CSV files and makes common data-quality problems easier to spot. It is designed for simple, reviewable cleanup tasks rather than silently guessing how to fix uncertain data.

## Features

- **Automatic encoding detection:** Uses `chardet` and tries common fallback encodings.
- **Delimiter detection:** Detects common separators: comma, semicolon, tab, or pipe.
- **Whitespace trimming:** Removes leading and trailing whitespace from cell values.
- **Duplicate removal:** Removes fully duplicated rows after trimming whitespace.
- **Identifier-safe reading:** Reads columns as text to avoid converting phone numbers, ZIP/postal codes, and IDs to numbers and losing zeros that are still present in the source.
- **Basic identifier cleanup:** Removes a trailing `.0` from digit-only values in columns that look like phone, ZIP/postal-code, or ID fields.
- **Email format checks:** Checks for common syntax problems, including missing parts, multiple `@` characters, whitespace, and malformed domains.
- **Conservative email repair:** Repairs recognizable `at_`-instead-of-`@` typos. Uncertain or invalid values are not guessed at.
- **Email review column:** Adds an `Email Review` column to the output when email columns are present. Blank, invalid, or unrepairable email values are marked `⚠️ NEEDS REVIEW`.
- **Readable terminal progress:** Shows five numbered processing steps, colored status text, emoji indicators, and a summary of rows removed, emails repaired, and rows needing review.
- **Spreadsheet-friendly output:** Writes a comma-separated CSV using UTF-8 with BOM (`utf-8-sig`) so spreadsheet programs can display special characters and emoji more reliably. It does not add a DataFrame index column.

## How the email review works

CSV-Fixer only applies a repair when it recognizes a specific pattern and the result passes its syntax checks. For example, an address containing `at_` in place of `@` may be repaired.

Addresses that are blank, malformed, or cannot be repaired confidently are marked `⚠️ NEEDS REVIEW` in the added review column. Review the flagged rows manually before using the data.

**Important:** A syntactically valid email address is not proof that the address exists or that its mailbox can receive messages.

## Requirements

- Python 3.10 or newer recommended
- `pandas`
- `chardet`

Install the dependencies:

```bash
python -m pip install pandas chardet
```

## Run the example

Run these commands from the repository folder.

1. Generate a sample CSV containing deliberately messy data:

   ```bash
   python generate_dirty_csv.py
   ```

2. Clean the generated CSV:

   ```bash
   python main.py
   ```

By default, the example uses:

- **Input:** `examples/broken_leads_dirty.csv`
- **Output:** `examples/fixed_leads_clean.csv`

The sample generator includes issues such as:

- Extra whitespace around values
- Duplicate rows
- Email typos where `@` is replaced with `at_`
- Emails with multiple `@` characters
- Missing dots in email domains
- Whitespace inside email addresses
- Missing email local parts
- Consecutive dots in email domains
- Phone, ZIP/postal-code, and ID values with trailing `.0` or potentially missing leading zeros
- Non-ASCII characters in city names to exercise encoding handling

The input generator uses random sample data, so exact row counts and repair totals can vary between runs.

## Use it on another CSV file

You can edit the input and output paths in the `if __name__ == "__main__"` section of `main.py`, or import the cleaning function:

```python
from main import repair_csv

repair_csv("input.csv", "output.csv")
```

To specify a delimiter manually:

```python
repair_csv("input.csv", "output.csv", current_delimiter=";")
```

## Important limitations

- **Missing leading zeros cannot be safely reconstructed from the value alone.** CSV-Fixer preserves zeros that are still present in source values, but it cannot know how many zeros were lost unless you provide a trusted rule or expected field length.
- Encoding detection and delimiter detection are best-effort heuristics. Inspect the output if the source file is unusual.
- Email checks validate syntax only; they do not contact mail servers or confirm mailbox existence.
- Email repairs are intentionally conservative. Values that cannot be repaired with confidence are flagged for review instead of being guessed.
- The tool does not restore every case of text that was already corrupted by decoding with the wrong encoding.
- Always review the output before using it for business-critical records.

## Project purpose

CSV-Fixer is a personal Python portfolio project demonstrating CSV parsing, data cleaning, basic validation, conservative error correction, and clear reporting of records that need human review.
