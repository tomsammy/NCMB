app_path = r'C:\Users\hp\Desktop\NCMB\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update fetch_cbt_questions
old_fetch = """def fetch_cbt_questions(cursor, paper_code, mda, group_category):
    clean_paper = (paper_code or "").strip()
    clean_mda = (mda or "").strip()
    clean_group = (group_category or "").replace("GROUP ", "").strip()
    
    rows = []
    matched_paper = clean_paper
    source_table = "cbt_questions"

    # 1. Exact paper_code match with normalization variants
    if clean_paper:
        alt_paper1 = clean_paper.replace("/", "-")
        alt_paper2 = clean_paper.replace("-", "/")
        alt_paper3 = clean_paper.replace("&CD", "")
        alt_paper4 = clean_paper.replace("/AI", "/A1").replace("-AI", "-A1")
        cursor.execute(\"\"\"
            SELECT id, paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE paper_code = ? OR paper_code = ? OR paper_code = ? OR paper_code = ? OR paper_code = ?
            ORDER BY question_number ASC
            LIMIT 40
        \"\"\", (clean_paper, alt_paper1, alt_paper2, alt_paper3, alt_paper4))
        rows = cursor.fetchall()

    # 2. Same MDA match
    if not rows and clean_mda:
        cursor.execute(\"\"\"
            SELECT id, paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE mda = ?
            ORDER BY question_number ASC
            LIMIT 40
        \"\"\", (clean_mda,))
        rows = cursor.fetchall()
        if rows:
            matched_paper = f"{clean_mda} Cadre"

    # 3. Same Group Category in OHOS (Civil Service General)
    if not rows and clean_group:
        cursor.execute(\"\"\"
            SELECT id, paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE mda = 'OHOS' AND group_category = ?
            ORDER BY question_number ASC
            LIMIT 40
        \"\"\", (clean_group,))
        rows = cursor.fetchall()
        if rows:
            matched_paper = f"OHOS/{clean_group}1"

    # 4. Fallback to questions table
    if not rows:
        cursor.execute(\"\"\"
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            ORDER BY question_number ASC
            LIMIT 40
        \"\"\" )
        rows = cursor.fetchall()
        matched_paper = "Civil Service General"
        source_table = "questions"

    rows = [dict(r) for r in rows]

    # Renumber sequentially 1..40 so palette and scoring are always 1 to 40
    renumbered = []
    for idx, r in enumerate(rows[:40], start=1):
        r["question_number"] = idx
        renumbered.append(r)

    return renumbered, matched_paper"""

new_fetch = """def fetch_cbt_questions(cursor, paper_code, mda, group_category):
    clean_paper = (paper_code or "").strip()
    
    rows = []
    matched_paper = clean_paper

    if clean_paper:
        cursor.execute(\"\"\"
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE grade_level = ?
            ORDER BY question_number ASC
        \"\"\", (clean_paper,))
        rows = cursor.fetchall()

    if not rows:
        # Default to Part 1: Digital Productivity & Statistics (Q1-60)
        default_paper = "Part 1: Digital Productivity & Statistics (Q1-60)"
        cursor.execute(\"\"\"
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE grade_level = ?
            ORDER BY question_number ASC
        \"\"\", (default_paper,))
        rows = cursor.fetchall()
        matched_paper = default_paper

    if not rows:
        # Fallback to any questions
        cursor.execute(\"\"\"
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            ORDER BY question_number ASC
            LIMIT 60
        \"\"\")
        rows = cursor.fetchall()
        matched_paper = "Module 1 Assessment"

    rows = [dict(r) for r in rows]
    renumbered = []
    for idx, r in enumerate(rows, start=1):
        r["question_number"] = idx
        renumbered.append(r)

    return renumbered, matched_paper"""

code = code.replace(old_fetch, new_fetch)

# 2. Auto-provision in start-with-token if candidate not found in candidate_roster
old_raise = """        else:
            conn.close()
            raise HTTPException(status_code=404, detail=f"No candidate record found for PSN {psn}.")"""

new_raise = """        else:
            # Auto-provision candidate in candidate_roster for NCDMB examination
            cursor.execute(\"\"\"
                INSERT INTO candidate_roster (
                    psn, name, mda, exam_code, proposed_rank, proposed_gl,
                    group_category, registration_status, test_duration_minutes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'registered', ?)
            \"\"\", (
                psn, f"Staff ({psn})", "NCDMB Operations", "Part 1: Digital Productivity & Statistics (Q1-60)",
                "Staff", "Module 1", "GROUP A", DEFAULT_DURATION_MINUTES
            ))
            conn.commit()
            cursor.execute("SELECT * FROM candidate_roster WHERE psn = ?", (psn,))
            cand = cursor.fetchone()"""

code = code.replace(old_raise, new_raise)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated fetch_cbt_questions and auto-provisioning in app.py successfully!")
