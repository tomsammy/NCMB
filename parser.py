import os
import re
import sys
import logging
import sqlite3
from database import get_db_connection, init_db, IS_POSTGRES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ncdmb_cbt_parser")

RAW_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "sample_questions", "raw_questions_with_answers.txt")


def seed_database(force_reseed: bool = False):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM questions")
    row = cursor.fetchone()
    count = row["cnt"] if isinstance(row, dict) else row[0]

    if count > 0 and not force_reseed:
        logger.info(f"Database already contains {count} questions. Skipping seed.")
        conn.close()
        return

    if force_reseed:
        logger.info("Force reseed: Clearing existing questions...")
        cursor.execute("DELETE FROM questions")
        conn.commit()

    if not os.path.exists(RAW_QUESTIONS_FILE):
        logger.warning(f"Raw question file not found at {RAW_QUESTIONS_FILE}")
        conn.close()
        return

    with open(RAW_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse answers
    answers = {}
    for line in text.split("\n"):
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            for i in range(0, len(parts)-1, 2):
                q_str = parts[i]
                ans_str = parts[i+1].upper()
                if q_str.isdigit() and ans_str in ["A", "B", "C", "D"]:
                    answers[int(q_str)] = ans_str

    # Parse questions
    q_blocks = re.split(r'\n(?=\d+\.\s+)', text)
    parsed_questions = []

    for block in q_blocks:
        m_num = re.match(r'^(\d+)\.\s+(.*)', block.strip(), re.DOTALL)
        if not m_num:
            continue
        q_num = int(m_num.group(1))
        body = m_num.group(2).strip()

        m_opt = re.search(r'(?=\bA\.\s*)', body)
        if not m_opt:
            continue
        
        q_text = body[:m_opt.start()].strip()
        options_str = body[m_opt.start():].strip()

        opt_parts = re.split(r'(?=[A-D]\.\s*)', options_str)
        opts = {}
        for op in opt_parts:
            op = op.strip()
            m_letter = re.match(r'^([A-D])\.\s*(.*)', op, re.DOTALL)
            if m_letter:
                letter = m_letter.group(1).upper()
                val = m_letter.group(2).strip()
                if '\nPART ' in val or '\nSECTION ' in val or '\nANSWER' in val:
                    val = re.split(r'\n(?:PART|SECTION|ANSWER)', val)[0].strip()
                opts[letter] = val

        ans = answers.get(q_num, 'A')

        if 1 <= q_num <= 60:
            part_num = 1
            part_idx = q_num
        elif 61 <= q_num <= 120:
            part_num = 2
            part_idx = q_num - 60
        else:
            part_num = 3
            part_idx = q_num - 120

        parsed_questions.append({
            'number': q_num,
            'part_num': part_num,
            'part_idx': part_idx,
            'question': q_text,
            'option_a': opts.get('A', ''),
            'option_b': opts.get('B', ''),
            'option_c': opts.get('C', ''),
            'option_d': opts.get('D', ''),
            'answer': ans
        })

    logger.info(f"Parsed {len(parsed_questions)} questions from NCDMB question bank.")

    def insert_q(gl, num, stem, a, b, c, d, ans):
        if IS_POSTGRES:
            cursor.execute("""
                INSERT INTO questions (
                    grade_level, question_number, question_text,
                    option_a, option_b, option_c, option_d, correct_answer
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (gl, num, stem, a, b, c, d, ans))
        else:
            cursor.execute("""
                INSERT INTO questions (
                    grade_level, question_number, question_text,
                    option_a, option_b, option_c, option_d, correct_answer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (gl, num, stem, a, b, c, d, ans))

    # Seed All 180 Questions under Full Assessment
    for q in parsed_questions:
        insert_q("Module 1: Digital Foundations (Full 180 Questions)", q['number'], q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer'])

    # Seed Part 1 (Q1 - Q60)
    for q in [x for x in parsed_questions if x['part_num'] == 1]:
        insert_q("Part 1: Digital Productivity & Statistics (Q1-60)", q['part_idx'], q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer'])

    # Seed Part 2 (Q61 - Q120)
    for q in [x for x in parsed_questions if x['part_num'] == 2]:
        insert_q("Part 2: SQL & RDBMS (Q61-120)", q['part_idx'], q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer'])

    # Seed Part 3 (Q121 - Q180)
    for q in [x for x in parsed_questions if x['part_num'] == 3]:
        insert_q("Part 3: Data Governance & Oil and Gas (Q121-180)", q['part_idx'], q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer'])

    conn.commit()
    conn.close()
    logger.info("NCDMB questions successfully seeded into database.")


if __name__ == "__main__":
    reseed = "--reseed" in sys.argv or "--force" in sys.argv
    seed_database(force_reseed=reseed)
