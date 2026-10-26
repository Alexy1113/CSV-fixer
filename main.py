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

    result = chardet.detect(raw_data)
    detected = result.get("encoding")

    # Prefer a detected encoding, but fall back to common encodings if needed.
    candidates = [detected, "utf-8-sig", "cp1252", "latin-1"]
    for encoding in candidates:
        if not encoding:
            continue
        try:
            raw_data.decode(encoding)
            return encoding
        except (LookupError, UnicodeDecodeError):
            continue

    return "utf-8"


def detect_delimiter(file_path, encoding):
    """Guess the delimiter from a sample; fall back to the most common candidate."""
    with open(file_path, "r", encoding=encoding, errors="replace", newline="") as f:
        sample = f.read(50_000)

    if not sample.strip():
        return ","

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(DELIMITER_CANDIDATES))
        return dialect.delimiter
    except csv.Error:
        # A conservative fallback for files that csv.Sniffer cannot classify.
        first_line = next((line for line in sample.splitlines() if line.strip()), "")
        counts = {delimiter: first_line.count(delimiter) for delimiter in DELIMITER_CANDIDATES}
        return max(counts, key=counts.get) if max(counts.values(), default=0) else ","


def clean_phone_and_zip(val):
    """Trim a value and remove a trailing .0 artifact without numeric conversion.

    This deliberately does not invent missing leading zeros: the correct value
    cannot be inferred reliably from a damaged file.
    """
    if val is None or pd.isna(val):
        return ""

    val_str = str(val).strip()
    if re.fullmatch(r"\d+\.0", val_str):
        val_str = val_str[:-2]
    return val_str


def validate_email(email):
    """Trim an email and flag suspicious values without rewriting its contents."""
    if email is None or pd.isna(email):
        return ""

    email_str = str(email).strip()
    if not email_str:
        return ""

    # This is a basic format check, not proof that the mailbox exists.
    pattern = r"^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$"
    if re.fullmatch(pattern, email_str):
        return email_str

    # Keep the original value visible for manual review; do not guess how to fix it.
    return f"REVIEW: {email_str}"


def repair_csv(input_path, output_path, current_delimiter=None):
    """Clean a CSV while preserving identifiers and avoiding speculative edits."""
    print(f"\nLaunching data cleaning pipeline for: {input_path}")

    encoding = detect_encoding(input_path)
    print(f"[1/5] Detected encoding: {encoding}")

    delimiter = current_delimiter or detect_delimiter(input_path, encoding)
    print(f"[2/5] Using detected delimiter: {repr(delimiter)}")

    try:
        # Read every column as text so pandas does not convert ZIP codes,
        # phone numbers, or IDs to numeric values and discard leading zeros.
        df = pd.read_csv(
            input_path,
            encoding=encoding,
            sep=delimiter,
            dtype=str,
            keep_default_na=False,
            na_filter=False,
            skipinitialspace=False,
        )
        print(f"File parsed successfully into {len(df.columns)} columns.")
    except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as exc:
        print(f"Failed to read CSV: {exc}")
        return False

    original_rows = len(df)

    # Trim leading/trailing whitespace in every cell, regardless of column dtype.
    for col in df.columns:
        df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)

    # Remove exact duplicate rows after trimming surrounding whitespace.
    df = df.drop_duplicates()
    print(f"[3/5] Removed {original_rows - len(df)} duplicate rows.")

    print("[4/5] Cleaning phone, ZIP/postal code, ID, and email columns.")
    for col in df.columns:
        col_lower = str(col).strip().lower()

        if any(token in col_lower for token in ("phone", "zip", "postal", "post code", "postcode", " id", "_id", "id ")):
            df[col] = df[col].map(clean_phone_and_zip)

        if "email" in col_lower or col_lower in {"e-mail", "mail"}:
            df[col] = df[col].map(validate_email)

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Standardized output: UTF-8, comma-separated, no pandas index column.
        df.to_csv(output_path, index=False, encoding="utf-8", sep=",", lineterminator="\n")
    except OSError as exc:
        print(f"Failed to write output CSV: {exc}")
        return False

    print(f"[5/5] Saved cleaned CSV: {output_path}")
    print(f"Summary: {original_rows} input rows -> {len(df)} output rows.")
    print("Note: missing leading zeros cannot be safely reconstructed from damaged source values.")
    return True


if __name__ == "__main__":
    dirty_file = os.path.join("examples", "broken_leads_dirty.csv")
    clean_file = os.path.join("examples", "fixed_leads_clean.csv")

    if os.path.exists(dirty_file):
        repair_csv(dirty_file, clean_file)
    else:
        print(f"Input file not found: {dirty_file}. Run generate_dirty_csv.py first.")
