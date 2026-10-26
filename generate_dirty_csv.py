import os
import random

# Создаем структуру папок для GitHub проекта
os.makedirs("examples", exist_ok=True)

# Исходные данные для генерации "каши"
first_names = ["John", "Jane", "Alice", "Bob", "Michael", "Emma", "David", "Olivia", "James", "Sophia"]
last_names = ["Doe", "Smith", "Johnson", "Brown", "Miller", "Davis", "Wilson", "Taylor", "Clark", "White"]
companies = ["Alpha LLC", "Beta Corp", "Gamma Inc", "Delta Tech", "Omega Solutions"]
# Города со спецсимволами для проверки кодировки (немецкие умлауты, французские акценты)
cities = ["New York", "Los Angeles", "München", "Paris", "Montréal", "Tokyo", "Köln"]

# Шапка таблицы. Ошибка 1: разделитель - точка с запятой (;) вместо запятой (,)
header = "First Name;Last Name;Email;Phone;ZIP Code;City;Company;Lead ID\n"
rows = [header]

# Генерируем 85 уникальных строк с ошибками
for i in range(1, 86):
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)

    # Ошибка 2: Лишние пробелы по краям (Trim Whitespaces)
    if i % 5 == 0:
        f_name = f"  {f_name} "

    # Ошибка 3: Битые и подозрительные Email-адреса для проверки очистки
    base_email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example.com"

    if i % 10 == 0:
        # Ошибка, которую можно распознать автоматически: @ заменен на at_
        email = f"{f_name.lower()}.{l_name.lower()}{i}at_example.com"
    elif i % 17 == 0:
        # Подозрительный адрес: два символа @
        email = base_email.replace("@", "@@", 1)
    elif i % 19 == 0:
        # Подозрительный адрес: в домене нет точки
        email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example"
    elif i % 23 == 0:
        # Подозрительный адрес: пробел внутри адреса
        email = f"{f_name.lower().strip()} {l_name.lower()}{i}@example.com"
    elif i % 29 == 0:
        # Подозрительный адрес: отсутствует имя до @
        email = f"@example.com"
    elif i % 31 == 0:
        # Подозрительный адрес: две точки подряд в домене
        email = f"{f_name.lower().strip()}.{l_name.lower()}{i}@example..com"
    else:
        email = base_email

    # Ошибка 4: Сломанные телефоны (потеря ведущего нуля Excel-ем)
    if i % 4 == 0:
        phone = f"447911{random.randint(100000, 999999)}" # пропал 0 в начале (Великобритания)
    elif i % 4 == 1:
        phone = f"0151{random.randint(1000000, 9999999)}" # нормальный номер с нулем (Германия)
    else:
        phone = f"1555{random.randint(1000000, 9999999)}" # США

    # Ошибка 5: ZIP-коды и ID превратились во float (числа с .0 на конце)
    if i % 2 == 0:
        zip_code = f"{random.randint(10000, 99999)}.0"
        lead_id = f"{1000 + i}.0"
    else:
        zip_code = f"0{random.randint(1000, 9999)}" # Потеря нуля: превратится в 4-значное вместо 5-значного
        lead_id = f"{1000 + i}"

    city = random.choice(cities)
    company = random.choice(companies)

    row = f"{f_name};{l_name};{email};{phone};{zip_code};{city};{company};{lead_id}\n"
    rows.append(row)

# Ошибка 6: Добавляем 15 полных дубликатов строк в случайные места таблицы
for _ in range(15):
    duplicate_row = random.choice(rows[1:])
    rows.insert(random.randint(1, len(rows)), duplicate_row)

# Ошибка 7: Сохраняем файл в кодировке Windows-1251 (CP1251) вместо UTF-8.
# Это превратит некоторые символы в названиях городов в некорректный текст при неверном чтении.
file_path = "examples/broken_leads_dirty.csv"
with open(file_path, "w", encoding="ISO-8859-1") as f:
    f.writelines(rows)

print(f"✅ Файл успешно сгенерирован и сохранен по пути: {file_path}")
print(f"📊 Всего строк в файле (включая шапку и 15 дубликатов): {len(rows)}")
print(f"📊 Всего уникальных строк (без дубликатов): {len(set(rows))}")
print(f"📊 Всего дубликатов: {len(rows) - len(set(rows))}")
print(f"📊 Всего уникальных строк (без дубликатов и полных дубликатов): {len(set(rows)) - 15}")
