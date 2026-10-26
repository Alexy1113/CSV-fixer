import os
import random

# Create the folder structure for the GitHub project.
os.makedirs("examples", exist_ok=True)

# Source data used to generate messy sample records.
first_names = ["John", "Jane", "Alice", "Bob", "Michael", "Emma", "David", "Olivia", "James", "Sophia"]
last_names = ["Doe", "Smith", "Johnson", "Brown", "Miller", "Davis", "Wilson", "Taylor", "Clark", "White"]
companies = ["Alpha LLC", "Beta Corp", "Gamma Inc", "Delta Tech", "Omega Solutions"]

# Cities with special characters for testing text encoding (German umlauts and French accents).
cities = ["New York", "Los Angeles", "München", "Paris", "Montréal", "Tokyo", "Köln"]

# CSV header. Issue 1: uses semicolons (;) instead of commas (,) as delimiters.
header = "First Name;Last Name;Email;Phone;ZIP Code;City;Company;Lead ID\n"
rows = [header]

# Generate 85 unique sample rows containing data issues.
for i in range(1, 86):
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)

    # Issue 2: Add leading and trailing whitespace.
    if i % 5 == 0:
        f_name = f"  {f_name} "

    # Issue 3: Create malformed and suspicious email addresses for testing the cleaner.
    base_email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example.com"

    if i % 10 == 0:
        # Recognizable typo that can be repaired automatically: replace @ with at_.
        email = f"{f_name.lower()}.{l_name.lower()}{i}at_example.com"
    elif i % 17 == 0:
        # Suspicious email: two @ characters.
        email = base_email.replace("@", "@@", 1)
    elif i % 19 == 0:
        # Suspicious email: the domain has no dot.
        email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example"
    elif i % 23 == 0:
        # Suspicious email: whitespace inside the address.
        email = f"{f_name.lower().strip()} {l_name.lower()}{i}@example.com"
    elif i % 29 == 0:
        # Suspicious email: the local part before @ is missing.
        email = "@example.com"
    elif i % 31 == 0:
        # Suspicious email: two consecutive dots in the domain.
        email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example..com"
    else:
        email = base_email

    # Issue 4: Include phone numbers with inconsistent leading zeros.
    if i % 4 == 0:
        phone = f"447911{random.randint(100000, 999999)}"  # UK-style number without a leading zero.
    elif i % 4 == 1:
        phone = f"0151{random.randint(1000000, 9999999)}"  # Number with a leading zero.
    else:
        phone = f"1555{random.randint(1000000, 9999999)}"  # US-style sample number.

    # Issue 5: Make some ZIP codes and IDs look like floating-point values by adding .0.
    if i % 2 == 0:
        zip_code = f"{random.randint(10000, 99999)}.0"
        lead_id = f"{1000 + i}.0"
    else:
        zip_code = f"0{random.randint(1000, 9999)}"  # A leading zero may be lost if treated as a number.
        lead_id = f"{1000 + i}"

    city = random.choice(cities)
    company = random.choice(companies)

    row = f"{f_name};{l_name};{email};{phone};{zip_code};{city};{company};{lead_id}\n"
    rows.append(row)

# Issue 6: Insert 15 full duplicate rows at random positions in the file.
for _ in range(15):
    duplicate_row = random.choice(rows[1:])
    rows.insert(random.randint(1, len(rows)), duplicate_row)

# Issue 7: Save the file using ISO-8859-1 (Latin-1) instead of UTF-8.
# This helps test how the program handles text encoding and special characters.
file_path = "examples/broken_leads_dirty.csv"
with open(file_path, "w", encoding="ISO-8859-1") as f:
    f.writelines(rows)

print(f"✅ Sample file generated and saved to: {file_path}")
print(f"📊 Total rows in the file (including the header and 15 duplicates): {len(rows)}")
print(f"📊 Total unique rows (excluding duplicates): {len(set(rows))}")
print(f"📊 Total duplicate rows: {len(rows) - len(set(rows))}")
print(f"📊 Unique data rows after excluding the header and duplicate rows: {len(set(rows)) - 1}")
