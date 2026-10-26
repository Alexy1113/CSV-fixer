import os  # OS module for file and directory operations
import re  # Regular expressions engine for pattern matching
import chardet  # Universal character encoding detector
import pandas as pd  # High-performance data analysis library


def detect_encoding(file_path):
    """AUTOMATED ENCODING DETECTION (Fixes garbage text / 'krkozyabry') Reads

    the raw binary data of the file and guesses its original encoding.
    """
    with open(file_path, "rb") as f:
        raw_data = f.read(20000)  # Read first 20KB for analysis

        result = chardet.detect(raw_data)
        detected_enc = result["encoding"]

        # If chardet is confident, return it. Otherwise, fallback to ISO-8859-1.
        return detected_enc if detected_enc else "ISO-8859-1"


def clean_phone_and_zip(val):
    """DATA FORMATTING WIZARD (Formatting Fixes) Removes unwanted '.0' float

    artifacts added by Excel/Pandas to numeric string columns.
    """
    if pd.isna(val):
        return ""

    val_str = str(val).strip()

    # Regex: Find '.' and '0' at the exact end of the string ($) and erase them
    # Example: '10001.0' becomes '10001'
    val_str = re.sub(r"\.0$", "", val_str)

    return val_str


def validate_email(email):
    """ULTIMATE EMAIL SCRUBBER & VALIDATION Erases internal spaces, fixes 'at'

    placeholders, and strips forbidden special characters after '@'.
    """
    if pd.isna(email):
        return ""

    # Convert email to lowercase and remove any internal whitespaces
    email_str = str(email).lower().replace(" ", "")

    # Fix plaintext 'at' variations (e.g., 'johnat_domain.com' -> 'john@domain.com')
    email_str = re.sub(r"(?<=\w)at(?=\w)", "@", email_str)

    # Strip any garbage characters right after the '@' symbol (e.g., '@_domain' -> '@domain')
    email_str = re.sub(r"@([^a-z0-9]+)", r"@", email_str)

    # Standard regex pattern for strict email validation
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if re.match(pattern, email_str):
        return email_str  # Return pristine email if valid
    else:
        # Flag highly corrupted emails for manual client review
        return f"⚠️ FIX NEEDED: {email_str}"


def repair_csv(input_path, output_path, current_delimiter=";"):
    """MASTER DATA CLEANING ENGINE Orchestrates all data repair steps on the

    DataFrame.
    """
    print(f"\n🚀 Launching data cleaning pipeline for: {input_path}")

    # --- STEP 1: Handle Encoding Issues ---
    encoding = detect_encoding(input_path)
    print(f"[1/5] Detected encoding: {encoding} (resolving character issues...)")

    # --- STEP 2: Splitting Text to Columns ---
    try:
        # Load custom delimited file into a Pandas DataFrame
        df = pd.read_csv(input_path, encoding=encoding, sep=current_delimiter)
        print(f"[2/5] File parsed successfully into {len(df.columns)} columns.")
    except Exception as e:
        print(f"❌ Failed to split columns: {e}")
        return

    original_rows = len(df)

    # --- STEP 3: Deduplication (PDEP-8 Compliant) ---
    # inplace=True is deprecated in modern Pandas; reassignment is used instead
    df = df.drop_duplicates()
    rows_after_dedup = len(df)
    print(
        f"[3/5] Deduplication complete: Removed {original_rows - rows_after_dedup} duplicate rows."
    )

    # --- STEP 4: Cell Standardization & Trimming ---
    print("[4/5] Scrubbing records (Phones, ZIP Codes, Emails, IDs)...")

    # Strip outer whitespaces from all string-based elements
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # Apply specialized cleaning algorithms to target columns
    for col in df.columns:
        col_lower = col.lower()

        if "phone" in col_lower or "zip" in col_lower or "id" in col_lower:
            df[col] = df[col].apply(clean_phone_and_zip)

        if "email" in col_lower:
            df[col] = df[col].apply(validate_email)

    # --- STEP 5: Standardized UTF-8 Export ---
    print(f"[5/5] Exporting pristine data to comma-separated UTF-8 CSV...")

    # Export clean matrix without system index numbers
    df.to_csv(output_path, index=False, encoding="utf-8", sep=",")

    print(f"✨ [SUCCESS] Pristine file saved to: {output_path}")
    print(f"📊 Summary: Original rows: {original_rows} -> Cleaned rows: {len(df)}")


if __name__ == "__main__":
    # Define production routing paths
    dirty_file = "examples/broken_leads_dirty.csv"
    clean_file = "examples/fixed_leads_clean.csv"

    # Verify dataset existence before pipeline ignition
    if os.path.exists(dirty_file):
        repair_csv(dirty_file, clean_file, current_delimiter=";")
    else:
        print(
            f"❌ Target dataset {dirty_file} not found. Run generate_dirty_csv.py first."
        )

print()
