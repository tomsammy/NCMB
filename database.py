def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))

import os
import shutil
import json
import re
import logging
from datetime import datetime

logger = logging.getLogger("cbt_database")

# Load environment variables
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"\'')
                    if k and k not in os.environ:
                        os.environ[k] = v

load_env_file()

DATABASE_URL = (
    os.environ.get("DATABASE_URL") or
    os.environ.get("POSTGRES_URL") or
    ""
).strip()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_POSTGRES = bool(DATABASE_URL and ("postgres" in DATABASE_URL or "neon.tech" in DATABASE_URL))
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "cbt.db")

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
        SQLITE_PATH = tmp_db


class PostgresCursorWrapper:
    def __init__(self, raw_cursor):
        self.cursor = raw_cursor
        self.lastrowid = None

    def _convert_sql(self, sql):
        converted = sql.replace("?", "%s")
        sql_upper = converted.upper()
        if "INSERT INTO" in sql_upper and "RETURNING" not in sql_upper:
            table_match = re.search(r"INSERT\s+INTO\s+(\w+)", converted, re.IGNORECASE)
            if table_match and table_match.group(1).lower() in ["candidates", "submissions", "questions", "candidate_roster", "exam_tokens"]:
                converted = converted.rstrip("; ") + " RETURNING id"
        return converted

    def execute(self, sql, params=None):
        sql_pg = self._convert_sql(sql)
        if params is not None:
            self.cursor.execute(sql_pg, params)
        else:
            self.cursor.execute(sql_pg)

        if "RETURNING id" in sql_pg:
            try:
                row = self.cursor.fetchone()
                if row:
                    self.lastrowid = row.get("id") if isinstance(row, dict) else row[0]
            except Exception:
                pass
        return self

    def executemany(self, sql, seq_of_parameters):
        sql_pg = self._convert_sql(sql)
        return self.cursor.executemany(sql_pg, seq_of_parameters)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass


class PostgresConnectionWrapper:
    def __init__(self, raw_conn):
        self.conn = raw_conn

    def cursor(self):
        import psycopg2.extras
        raw_cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return PostgresCursorWrapper(raw_cursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db_connection():
    if IS_POSTGRES:
        import psycopg2
        import time
        last_err = None
        for attempt in range(3):
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=10)
                return PostgresConnectionWrapper(conn)
            except Exception as e:
                last_err = e
                time.sleep(1.0 * (attempt + 1))
        logger.warning(f"PostgreSQL connection failed ({last_err}), falling back to local SQLite.")
    
    import sqlite3
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = dict_factory
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if IS_POSTGRES:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            grade_level VARCHAR(50) NOT NULL,
            question_number INT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer VARCHAR(10) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_questions_gl ON questions(grade_level);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            amended_name VARCHAR(255),
            psn VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            grade_level VARCHAR(50) NOT NULL,
            mda VARCHAR(255) DEFAULT 'General Department',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_candidates_psn ON candidates(psn);
        """)

        cursor.execute("""
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
            test_duration_minutes INT DEFAULT 30,
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
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            candidate_id INT,
            candidate_name VARCHAR(255) NOT NULL,
            amended_name VARCHAR(255),
            psn VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            grade_level VARCHAR(50) NOT NULL,
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
        """)

        cursor.execute("""
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
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key VARCHAR(100) PRIMARY KEY,
            setting_value TEXT NOT NULL
        );
        """)

        cursor.execute("""
        INSERT INTO system_settings (setting_key, setting_value)
        VALUES ('exam_status', 'open')
        ON CONFLICT (setting_key) DO NOTHING;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS demo_practice_logs (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100) UNIQUE,
            psn VARCHAR(50),
            candidate_name VARCHAR(255),
            mda VARCHAR(255),
            grade_level VARCHAR(50),
            device_type VARCHAR(50),
            user_agent TEXT,
            ip_address VARCHAR(100),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            total_questions INT DEFAULT 40,
            answered_count INT DEFAULT 0,
            correct_count INT DEFAULT 0,
            score_percentage NUMERIC(6,2) DEFAULT 0.0,
            time_taken_seconds INT DEFAULT 0,
            violations_count INT DEFAULT 0,
            violation_logs TEXT,
            status VARCHAR(50) DEFAULT 'in_progress'
        );
        CREATE INDEX IF NOT EXISTS idx_demo_psn ON demo_practice_logs(psn);
        """)

        conn.commit()

    else:
        # SQLite schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade_level TEXT NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_gl ON questions(grade_level);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amended_name TEXT,
            psn TEXT NOT NULL,
            email TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            mda TEXT DEFAULT 'General Department',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_psn ON candidates(psn);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            psn TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            amended_name TEXT,
            code_1 TEXT,
            mda TEXT DEFAULT 'General Department',
            exam_code TEXT,
            proposed_rank TEXT,
            proposed_gl TEXT,
            group_category TEXT,
            exam_date TEXT,
            batch_session TEXT,
            batch_time TEXT,
            accreditation_time TEXT,
            test_duration_minutes INTEGER DEFAULT 30,
            phone TEXT,
            email TEXT,
            passport_photo TEXT,
            registration_status TEXT DEFAULT 'unverified',
            registered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amended_psn TEXT,
            amended_rank TEXT,
            amended_gl TEXT,
            amended_group TEXT,
            amended_exam_code TEXT
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_roster_psn ON candidate_roster(psn);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            candidate_name TEXT NOT NULL,
            amended_name TEXT,
            psn TEXT NOT NULL,
            email TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            mda TEXT DEFAULT 'General Department',
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            score_percentage REAL NOT NULL,
            grade_remark TEXT NOT NULL,
            time_taken_seconds INTEGER DEFAULT 0,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            answers_json TEXT,
            email_status TEXT DEFAULT 'pending',
            email_sent_at TIMESTAMP,
            violations_count INTEGER DEFAULT 0,
            security_flags TEXT
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_psn ON submissions(psn);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_code TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'unassigned',
            assigned_to_psn TEXT,
            activated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_code ON exam_tokens(token_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_psn ON exam_tokens(assigned_to_psn);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL
        );
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO system_settings (setting_key, setting_value)
        VALUES ('exam_status', 'open');
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS demo_practice_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            psn TEXT,
            candidate_name TEXT,
            mda TEXT,
            grade_level TEXT,
            device_type TEXT,
            user_agent TEXT,
            ip_address TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            total_questions INTEGER DEFAULT 40,
            answered_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            score_percentage REAL DEFAULT 0.0,
            time_taken_seconds INTEGER DEFAULT 0,
            violations_count INTEGER DEFAULT 0,
            violation_logs TEXT,
            status TEXT DEFAULT 'in_progress'
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_demo_psn ON demo_practice_logs(psn);")

        conn.commit()

    # Seed master tokens if available
    _seed_exam_tokens_if_needed(conn, cursor)

    conn.close()
    logger.info("Database initialized successfully.")


def _seed_exam_tokens_if_needed(conn, cursor):
    try:
        cursor.execute("SELECT COUNT(*) AS cnt FROM exam_tokens")
        row = cursor.fetchone()
        current_cnt = row["cnt"] if isinstance(row, dict) else row[0]

        master_json = os.path.join(os.path.dirname(__file__), "master_tokens.json")
        if current_cnt < 100 and os.path.exists(master_json):
            with open(master_json, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            # Seed up to 3500 tokens
            sample_tokens = tokens[:3500]
            if IS_POSTGRES:
                from psycopg2.extras import execute_values
                raw_cur = cursor.cursor if hasattr(cursor, 'cursor') else cursor
                execute_values(raw_cur, """
                    INSERT INTO exam_tokens (token_code, status)
                    VALUES %s
                    ON CONFLICT (token_code) DO NOTHING
                """, [(t, 'unassigned') for t in sample_tokens])
            else:
                cursor.executemany("""
                    INSERT OR IGNORE INTO exam_tokens (token_code, status)
                    VALUES (?, 'unassigned')
                """, [(t,) for t in sample_tokens])
            conn.commit()
            logger.info(f"Seeded {len(sample_tokens)} master exam login PINs.")
    except Exception as e:
        logger.warning(f"Could not seed exam tokens: {e}")


def get_setting(key: str, default: str = "") -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["setting_value"] if row else default
    except Exception:
        return default


def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute("""
        INSERT INTO system_settings (setting_key, setting_value)
        VALUES (%s, %s)
        ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value
        """, (key, value))
    else:
        cursor.execute("""
        INSERT OR REPLACE INTO system_settings (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, value))
    conn.commit()
    conn.close()
