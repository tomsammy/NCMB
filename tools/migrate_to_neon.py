import sys
import os
sys.path.insert(0, r"C:\Users\hp\Desktop\NCMB")

import sqlite3
import psycopg2
import psycopg2.extras
import json

neon_url = "postgresql://neondb_owner:npg_7qXbkc2RIhPC@ep-shy-breeze-bbue2qt8-pooler.c-15.us-east-1.aws.neon.tech/neondb?sslmode=require"
sqlite_path = r"C:\Users\hp\Desktop\NCMB\cbt.db"

print("Connecting to SQLite...")
s_conn = sqlite3.connect(sqlite_path)
s_conn.row_factory = sqlite3.Row
s_cur = s_conn.cursor()

print("Connecting to Neon PostgreSQL...")
os.environ["DATABASE_URL"] = neon_url
from database import init_db
print("Running init_db() on Neon...")
init_db()

# Reconnect after init_db closed it
p_conn = psycopg2.connect(neon_url)
p_cur = p_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# 2. Migrate tables
tables_to_migrate = [
    ("system_settings", ["setting_key", "setting_value"]),
    ("questions", ["grade_level", "question_number", "question_text", "option_a", "option_b", "option_c", "option_d", "correct_answer"]),
    ("candidates", ["name", "amended_name", "psn", "email", "grade_level", "mda", "created_at"]),
    ("candidate_roster", [
        "psn", "name", "amended_name", "code_1", "mda", "exam_code", "proposed_rank", "proposed_gl",
        "group_category", "exam_date", "batch_session", "batch_time", "accreditation_time",
        "test_duration_minutes", "phone", "email", "passport_photo", "registration_status",
        "registered_at", "created_at", "amended_psn", "amended_rank", "amended_gl", "amended_group", "amended_exam_code"
    ]),
    ("exam_tokens", ["token_code", "status", "assigned_to_psn", "activated_at", "created_at"]),
    ("submissions", [
        "candidate_id", "candidate_name", "amended_name", "psn", "email", "grade_level", "mda",
        "total_questions", "correct_count", "score_percentage", "grade_remark", "time_taken_seconds",
        "submitted_at", "answers_json", "email_status", "email_sent_at", "violations_count", "security_flags"
    ])
]

for table, cols in tables_to_migrate:
    print(f"\n--- Migrating {table} ---")
    s_cur.execute(f"PRAGMA table_info({table})")
    existing_sqlite_cols = [r["name"] for r in s_cur.fetchall()]
    active_cols = [c for c in cols if c in existing_sqlite_cols]
    
    s_cur.execute(f"SELECT {', '.join(active_cols)} FROM {table}")
    rows = s_cur.fetchall()
    print(f"Found {len(rows)} rows in SQLite {table}")
    
    if rows:
        # Clear existing in postgres to avoid duplicate keys
        p_cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
        
        col_str = ", ".join(active_cols)
        val_str = ", ".join(["%s"] * len(active_cols))
        insert_sql = f"INSERT INTO {table} ({col_str}) VALUES ({val_str})"
        
        batch = []
        for r in rows:
            batch.append([r[c] for c in active_cols])
            
        psycopg2.extras.execute_batch(p_cur, insert_sql, batch)
        p_conn.commit()
        print(f"Successfully inserted {len(batch)} rows into Neon {table}")

# Verify
print("\n=== VERIFICATION IN NEON POSTGRESQL ===")
for table, _ in tables_to_migrate:
    p_cur.execute(f"SELECT count(*) as cnt FROM {table}")
    res = p_cur.fetchone()
    print(f"{table}: {res['cnt']} rows")

s_conn.close()
p_conn.close()
print("\nMigration to Neon PostgreSQL completed with 100% success!")
