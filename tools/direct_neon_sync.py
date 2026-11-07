import sys
import os
import sqlite3
import psycopg2
import psycopg2.extras

neon_url = "postgresql://neondb_owner:npg_7qXbkc2RIhPC@ep-shy-breeze-bbue2qt8-pooler.c-15.us-east-1.aws.neon.tech/neondb?sslmode=require"
sqlite_path = r"C:\Users\hp\Desktop\NCMB\cbt.db"

print("1. Connecting to SQLite...")
s_conn = sqlite3.connect(sqlite_path)
s_conn.row_factory = sqlite3.Row
s_cur = s_conn.cursor()

print("2. Connecting to Neon PostgreSQL...")
p_conn = psycopg2.connect(neon_url)
p_cur = p_conn.cursor()

# Create tables in Neon
ddl = """
CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    grade_level VARCHAR(100) NOT NULL,
    question_number INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer VARCHAR(10) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_questions_gl ON questions(grade_level);

CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amended_name VARCHAR(255),
    psn VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    grade_level VARCHAR(100) NOT NULL,
    mda VARCHAR(255) DEFAULT 'General Department',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_candidates_psn ON candidates(psn);

CREATE TABLE IF NOT EXISTS candidate_roster (
    id SERIAL PRIMARY KEY,
    psn VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    amended_name VARCHAR(255),
    code_1 VARCHAR(50),
    mda VARCHAR(255) DEFAULT 'General Department',
    exam_code VARCHAR(100),
    proposed_rank VARCHAR(255),
    proposed_gl VARCHAR(50),
    group_category VARCHAR(50),
    exam_date VARCHAR(100),
    batch_session VARCHAR(50),
    batch_time VARCHAR(50),
    accreditation_time VARCHAR(50),
    test_duration_minutes INT DEFAULT 60,
    phone VARCHAR(50),
    email VARCHAR(255),
    passport_photo TEXT,
    registration_status VARCHAR(50) DEFAULT 'unverified',
    registered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amended_psn VARCHAR(50),
    amended_rank VARCHAR(255),
    amended_gl VARCHAR(50),
    amended_group VARCHAR(50),
    amended_exam_code VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_roster_psn ON candidate_roster(psn);

CREATE TABLE IF NOT EXISTS exam_tokens (
    id SERIAL PRIMARY KEY,
    token_code VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'unassigned',
    assigned_to_psn VARCHAR(50),
    activated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_token_code ON exam_tokens(token_code);
CREATE INDEX IF NOT EXISTS idx_token_psn ON exam_tokens(assigned_to_psn);

CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    candidate_id INT,
    candidate_name VARCHAR(255) NOT NULL,
    amended_name VARCHAR(255),
    psn VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    grade_level VARCHAR(100) NOT NULL,
    mda VARCHAR(255) DEFAULT 'General Department',
    total_questions INT NOT NULL,
    correct_count INT NOT NULL,
    score_percentage NUMERIC(6,2) NOT NULL,
    grade_remark VARCHAR(100) NOT NULL,
    time_taken_seconds INT DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answers_json TEXT,
    email_status VARCHAR(50) DEFAULT 'pending',
    email_sent_at TIMESTAMP,
    violations_count INT DEFAULT 0,
    security_flags TEXT
);
CREATE INDEX IF NOT EXISTS idx_submissions_psn ON submissions(psn);
"""

print("3. Creating tables in Neon...")
p_cur.execute(ddl)
p_conn.commit()

# Tables to migrate from SQLite to Neon
tables = [
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
]

for table, cols in tables:
    s_cur.execute(f"PRAGMA table_info({table})")
    sqlite_cols = [r["name"] for r in s_cur.fetchall()]
    active_cols = [c for c in cols if c in sqlite_cols]
    
    s_cur.execute(f"SELECT {', '.join(active_cols)} FROM {table}")
    rows = s_cur.fetchall()
    print(f"\nMigrating {table} ({len(rows)} rows from SQLite)...")
    
    # Truncate in postgres
    p_cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
    p_conn.commit()
    
    if rows:
        batch = [[r[c] for c in active_cols] for r in rows]
        insert_sql = f"INSERT INTO {table} ({', '.join(active_cols)}) VALUES %s"
        psycopg2.extras.execute_values(p_cur, insert_sql, batch, page_size=500)
        p_conn.commit()
        print(f"-> Successfully inserted {len(batch)} rows into Neon {table}!")

# Verification
print("\n=== NEON POSTGRESQL VERIFICATION ===")
for table, _ in tables:
    p_cur.execute(f"SELECT count(*) FROM {table}")
    cnt = p_cur.fetchone()[0]
    print(f"Table {table}: {cnt} rows")

s_conn.close()
p_conn.close()
print("\nALL DATA SUCCESSFULLY SYNCHRONIZED TO NEON POSTGRESQL!")
