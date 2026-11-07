app_path = r'C:\Users\hp\Desktop\NCMB\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'DEFAULT_DURATION_MINUTES = int(os.environ.get("DEFAULT_DURATION_MINUTES", "30"))',
    'DEFAULT_DURATION_MINUTES = int(os.environ.get("DEFAULT_DURATION_MINUTES", "60"))'
)

code = code.replace(
    '"duration_minutes": 20,',
    '"duration_minutes": DEFAULT_DURATION_MINUTES,'
)

code = code.replace(
    '"test_duration_minutes": 20,',
    '"test_duration_minutes": DEFAULT_DURATION_MINUTES,'
)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated duration_minutes to dynamic DEFAULT_DURATION_MINUTES in app.py!")
