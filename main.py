import csv
import os
import re

import chardet
import pandas as pd


DELIMITER_CANDIDATES = [",", ";", "\t", "|"]


def detect_encoding(file_path):
    """Detect a likely text encoding, with safe fallbacks."""
    with open(file_path, "rb") as f:
        raw_data = f.read(100_000)

    if not raw_data:
        return "utf-8"

    detected = chardet.detect(raw_data).get("encoding")
    for encoding in (detected, "utf-8-sig", "cp1252", "latin-1"):
        if not encoding:
            continue
        try:
            raw_data.decode(encoding)
            return encoding
        except (LookupError, UnicodeDecodeError):
            continue
    return "utf-8"


def detect_delimiter(file_path, encoding):
    """Guess the delimiter from a sample, with a conservative fallback."""
    with open(file_path, "r", encoding=encoding, errors="replace", newline="") as f:
        sample = f.read(50_000)

    if not sample.strip():
        return ","

    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(DELIMITER_CANDIDATES)).delimiter
    except csv.Error:
        first_line = next((line for line in sample.splitlines() if line.strip()), "")
        counts = {delimiter: first_line.count(delimiter) for delimiter in DELIMITER_CANDIDATES}
        return max(counts, key=counts.get) if max(counts.values(), default=0) else ","


def clean_phone_and_zip(value):
    """Trim a value and remove a trailing .0 artifact without numeric conversion.

    This does not invent missing leading zeros because the correct value cannot
    be inferred reliably from a damaged source file.
    """
    if value is None or pd.isna(value):
        return ""

    value = str(value).strip()
    if re.fullmatch(r"\d+\.0", value):
        value = value[:-2]
    return value


def is_email_format_valid(value):
    """Basic syntax check only; this does not verify that a mailbox exists."""
    if not value:
        return True
    return bool(re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", value))


def repair_csv(input_path, output_path, current_delimiter=None):
    """Clean a CSV while preserving identifiers and avoiding speculative edits."""
    print(f"\nLaunching data cleaning pipeline for: {input_path}")

    encoding = detect_encoding(input_path)
    print(f"[1/5] Detected encoding: {encoding}")

    delimiter = current_delimiter or detect_delimiter(input_path, encoding)
    print(f"[2/5] Using delimiter: {repr(delimiter)}")

    try:
        # Read all values as text so IDs, ZIP codes, and phone numbers keep zeros.
        df = pd.read_csv(
            input_path,
            encoding=encoding,
            sep=delimiter,
            dtype=str,
            keep_default_na=False,
            na_filter=False,
            skipinitialspace=False,
        )
    except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as exc:
        print(f"Failed to read CSV: {exc}")
        return False

    print(f"File parsed successfully into {len(df.columns)} columns.")
    original_rows = len(df)

    # Trim outer whitespace from every cell, regardless of column type.
    for col in df.columns:
        df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)

    # Drop duplicate rows after trimming outer whitespace.
    df = df.drop_duplicates()
    print(f"[3/5] Removed {original_rows - len(df)} duplicate rows.")

    print("[4/5] Cleaning identifier-like columns and checking email format.")
    invalid_email_count = 0

    for col in df.columns:
        col_lower = str(col).strip().lower()

        if any(word in col_lower for word in ("phone", "zip", "postal", "post code", "postcode")) or re.search(r"\bid\b", col_lower):
            df[col] = df[col].map(clean_phone_and_zip)

        if "email" in col_lower or col_lower in {"e-mail", "mail"}:
            # Do not guess how to repair addresses. Preserve original text and report
            # suspicious formats so a human can review them without losing data.
            invalid_email_count += sum(
                1 for value in df[col].tolist() if not is_email_format_valid(value)
            )

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    try:
        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
            sep=",",
            lineterminator="\n",
        )
    except OSError as exc:
        print(f"Failed to write output CSV: {exc}")
        return False

    print(f"[5/5] Saved cleaned CSV: {output_path}")
    print(f"Summary: {original_rows} input rows -> {len(df)} output rows.")
    print(f"Email values needing manual review: {invalid_email_count}. Original values were preserved.")
    print("Note: zeros already missing from the source cannot be safely reconstructed.")
    return True


if __name__ == "__main__":
    dirty_file = os.path.join("examples", "broken_leads_dirty.csv")
    clean_file = os.path.join("examples", "fixed_leads_clean.csv")

    if os.path.exists(dirty_file):
        repair_csv(dirty_file, clean_file)
    else:
        print(f"Input file not found: {dirty_file}. Run generate_dirty_csv.py first.")
