import os

path = r'C:\Users\hp\Desktop\NCMB\database.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'SQLITE_PATH = os.path.join(os.path.dirname(__file__), "cbt.db")'
replacement = '''SQLITE_PATH = os.path.join(os.path.dirname(__file__), "cbt.db")

# Vercel serverless read/write filesystem adaptation
if os.environ.get("VERCEL"):
    import shutil
    tmp_db = "/tmp/cbt.db"
    orig_db = os.path.join(os.path.dirname(__file__), "cbt.db")
    if not os.path.exists(tmp_db) and os.path.exists(orig_db):
        try:
            shutil.copy2(orig_db, tmp_db)
        except Exception as e:
            pass
    if os.path.exists(tmp_db):
        SQLITE_PATH = tmp_db'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated database.py for Vercel support successfully!")
else:
    print("Target not found in database.py")
