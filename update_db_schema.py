db_path = r'C:\Users\hp\Desktop\NCMB\database.py'

with open(db_path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'name VARCHAR(255) NOT NULL,',
    'name VARCHAR(255) NOT NULL,\n            amended_name VARCHAR(255),'
)

code = code.replace(
    'name TEXT NOT NULL,',
    'name TEXT NOT NULL,\n            amended_name TEXT,'
)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated database.py with amended_name column!")
