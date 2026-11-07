path = r"C:\Users\hp\Desktop\NCMB\database.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

old_block = """            if IS_POSTGRES:
                cursor.executemany(\"\"\"
                    INSERT INTO exam_tokens (token_code, status)
                    VALUES (%s, 'unassigned')
                    ON CONFLICT (token_code) DO NOTHING
                \"\"\", [(t,) for t in sample_tokens])"""

new_block = """            if IS_POSTGRES:
                from psycopg2.extras import execute_values
                raw_cur = cursor.cursor if hasattr(cursor, 'cursor') else cursor
                execute_values(raw_cur, \"\"\"
                    INSERT INTO exam_tokens (token_code, status)
                    VALUES %s
                    ON CONFLICT (token_code) DO NOTHING
                \"\"\", [(t, 'unassigned') for t in sample_tokens])"""

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: Optimized token seeding in database.py!")
else:
    print("Target block not found!")
