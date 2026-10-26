import csv
import os
import re

import chardet
import pandas as pd


DELIMITER_CANDIDATES = [",", ";", "\t", "|"]
REVIEW_LABEL = "⚠️ NEEDS REVIEW"

# ANSI colors work in modern Windows Terminal and PowerShell.
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"
COLOR_RESET = "\033[0m"


def step(number, message, color=COLOR_CYAN):
    """Print a colored step number and a readable status message."""
    print(f"{color}[{number}/5]{COLOR_RESET} {message}")


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
    """Trim a value and remove a trailing .0 artifact without numeric conversion."""
    if value is None or pd.isna(value):
        return ""

    value = str(value).strip()
    if re.fullmatch(r"\d+\.0", value):
        value = value[:-2]
    return value


def is_email_format_valid(value):
    """Check common email syntax problems; this does not verify mailbox existence."""
    if not value:
        return False

    value = str(value).strip()
    if any(char.isspace() for char in value):
        return False
    if value.count("@") != 1:
        return False

    local, domain = value.split("@", 1)
    if not local or len(local) > 64 or not domain:
        return False
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+", local):
        return False
    if len(domain) > 253 or "." not in domain or ".." in domain:
        return False

    labels = domain.split(".")
    if any(
        not label
        or len(label) > 63
        or label.startswith("-")
        or label.endswith("-")
        or not re.fullmatch(r"[A-Za-z0-9-]+", label)
        for label in labels
    ):
        return False
    if len(labels[-1]) < 2 or not labels[-1].isalpha():
        return False

    return True


def suggest_email_repair(value):
    """Repair only recognizable typos; return None when the fix is uncertain."""
    original = str(value).strip()
    if not original or is_email_format_valid(original):
        return original

    # Remove whitespace immediately around dots, then try a specific known repair.
    candidate = re.sub(r"\s*\.\s*", ".", original)

    # Recognize 'at_' used instead of '@'. Do not replace arbitrary 'at' text.
    if "@" not in candidate:
        match = re.fullmatch(
            r"([A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+)at_([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
            candidate,
        )
        if match:
            candidate = f"{match.group(1)}@{match.group(2)}"

    return candidate if is_email_format_valid(candidate) else None


def repair_csv(input_path, output_path, current_delimiter=None):
    """Clean a CSV and mark suspicious email rows in an added review column."""
    print(f"\n🚀 Launching data cleaning pipeline for: {input_path}")

    encoding = detect_encoding(input_path)
    step(1, f"🔎 Detected encoding: {encoding}", COLOR_CYAN)

    delimiter = current_delimiter or detect_delimiter(input_path, encoding)
    step(2, f"🧩 Using delimiter: {repr(delimiter)}", COLOR_CYAN)

    try:
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
        print(f"❌ Failed to read CSV: {exc}")
        return False

    print(f"📄 File parsed successfully into {len(df.columns)} columns.")
    original_rows = len(df)

    for col in df.columns:
        df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)

    df = df.drop_duplicates()
    step(3, f"🧹 Removed {original_rows - len(df)} duplicate rows.", COLOR_YELLOW)

    step(4, "🛠️ Cleaning identifier-like columns and checking email format.", COLOR_MAGENTA)
    repaired_email_count = 0
    review_count = 0
    email_columns = [
        col for col in df.columns
        if "email" in str(col).strip().lower()
        or str(col).strip().lower() in {"e-mail", "mail"}
    ]

    for col in df.columns:
        col_lower = str(col).strip().lower()

        if any(word in col_lower for word in ("phone", "zip", "postal", "post code", "postcode")) or re.search(r"\bid\b", col_lower):
            df[col] = df[col].map(clean_phone_and_zip)

    if email_columns:
        # Add one clear status column to the output table.
        review_col = "Email Review"
        if review_col in df.columns:
            review_col = "Email Review Status"

        review_flags = []
        for index, row in df.iterrows():
            row_needs_review = False

            for col in email_columns:
                value = row[col]
                if not value:
                    row_needs_review = True
                    continue

                if is_email_format_valid(value):
                    continue

                suggestion = suggest_email_repair(value)
                if suggestion is not None and suggestion != value:
                    df.at[index, col] = suggestion
                    repaired_email_count += 1
                else:
                    row_needs_review = True

            review_flags.append(REVIEW_LABEL if row_needs_review else "")

        df[review_col] = review_flags
        review_count = sum(flag == REVIEW_LABEL for flag in review_flags)

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    try:
        # UTF-8 with BOM helps spreadsheet programs display emoji correctly.
        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
            sep=",",
            lineterminator="\n",
        )
    except OSError as exc:
        print(f"Failed to write output CSV: {exc}")
        return False

    step(5, f"💾 Saved cleaned CSV: {output_path}", COLOR_GREEN)
    print(f"📊 Summary: {original_rows} input rows -> {len(df)} output rows.")
    print(f"🔧 Email addresses repaired using recognizable patterns: {repaired_email_count}.")
    print(f"⚠️ Rows marked '{REVIEW_LABEL}': {review_count}.")
    print("ℹ️ Email syntax checks do not confirm that an address or mailbox exists.")
    print("📝 Note: zeros already missing from the source cannot be safely reconstructed.")
    print()  # Leave a blank line before the PowerShell prompt.
    return True


if __name__ == "__main__":
    dirty_file = os.path.join("examples", "broken_leads_dirty.csv")
    clean_file = os.path.join("examples", "fixed_leads_clean.csv")

    if os.path.exists(dirty_file):
        repair_csv(dirty_file, clean_file)
    else:
        print(f"❌ Input file not found: {dirty_file}. Run generate_dirty_csv.py first.")
