# CSV Data Repair & Cleaning Automation Tool 🛠️

A professional Python-based data cleaning and optimization wizard. This automation tool is specifically engineered to repair corrupted or poorly formatted CSV exports from CRMs (HubSpot, Salesforce), lead scrapers, and e-commerce platforms (Shopify, WooCommerce) before database import.

## 🚀 Key Features (What it Fixes)
- **Advanced Delimiter Parsing:** Automatically handles custom or broken delimiters (such as semicolons `;` or tabs) and splits unified text rows into beautifully structured individual columns.
- **Automated Encoding Resolution:** Instantly fixes character corruption and garbage text ("krkozyabry" like `MÃ¼nchen` instead of `München`) by auto-detecting original encodings using `chardet`.
- **Pro-Level Duplication Elimination:** Instantly drops duplicate rows to ensure clean, high-quality database entries.
- **Smart Phone & ZIP Code Formatting:** Prevents spreadsheet engines from dropping leading zeros (e.g., maintaining `01234` instead of converting to `1234`) and strips unwanted `.0` float artifacts from structural numbers.
- **Ultimate Email Scrubbing & Regex Validation:** 
  - Erases accidental spaces inside email strings (e.g., `david .smith` -> `david.smith`).
  - Converts plaintext text artifacts like `[at]` or `at` into genuine `@` symbols.
  - Automatically strips forbidden trailing or leading special characters immediately following the `@` sign (e.g., `@_example.com` -> `@example.com`).

## 📦 Tech Stack
- **Python 3.15**
- **Pandas** (Modern Copy-on-Write pipeline setup without deprecated `inplace` parameters)
- **Chardet** (Universal character encoding detection)
- **Re** (Built-in regular expressions engine)

## 💻 How to Run Locally

1. Clone this repository to your local machine:
```bash
git clone https://github.com
cd CSV-Python
```

2. Install the production-ready dependencies:
```bash
pip install pandas chardet
```

3. Generate a massive 100-row "dirty" synthetic dataset full of structural errors to test the tool:
```bash
python generate_dirty_csv.py
```

4. Run the master data-cleaning script to produce a pristine, production-ready CSV output:
```bash
python main.py
```

## 💼 Fiverr Services Powered by This Script
I leverage this exact automated system to provide lightning-fast, highly accurate turnarounds on Fiverr for:
- B2B Lead List validation, scrubbing, and data deduplication.
- E-commerce inventory list standardizations (Shopify, Amazon, and WooCommerce mapping).
- Complex text-to-columns conversion tasks and character encoding recoveries.
