with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if line.startswith("def fetch_cbt_questions("):
        start_idx = i
    if start_idx is not None and line.startswith("@router.post(\"/submit-exam\")"):
        end_idx = i
        break

print(f"Found function from line {start_idx+1} to {end_idx+1}")

replacement = [
    "def fetch_cbt_questions(cursor, paper_code, mda, group_category):\n",
    "    clean_paper = (paper_code or \"\").strip()\n",
    "    rows = []\n",
    "    matched_paper = clean_paper or \"Part 1: Digital Productivity & Statistics (Q1-60)\"\n",
    "    source_table = \"questions\"\n",
    "\n",
    "    # 1. Match specific part or exam code in questions table\n",
    "    if clean_paper:\n",
    "        cursor.execute(\"\"\"\n",
    "            SELECT id, grade_level AS paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer\n",
    "            FROM questions\n",
    "            WHERE grade_level = ?\n",
    "            ORDER BY question_number ASC\n",
    "        \"\"\", (clean_paper,))\n",
    "        rows = cursor.fetchall()\n",
    "        \n",
    "        if not rows:\n",
    "            cursor.execute(\"\"\"\n",
    "                SELECT id, grade_level AS paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer\n",
    "                FROM questions\n",
    "                WHERE grade_level LIKE ?\n",
    "                ORDER BY question_number ASC\n",
    "            \"\"\", (f\"%{clean_paper}%\",))\n",
    "            rows = cursor.fetchall()\n",
    "\n",
    "    # 2. Match in cbt_questions view\n",
    "    if not rows and clean_paper:\n",
    "        try:\n",
    "            cursor.execute(\"\"\"\n",
    "                SELECT id, paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer\n",
    "                FROM cbt_questions\n",
    "                WHERE paper_code LIKE ?\n",
    "                ORDER BY question_number ASC\n",
    "            \"\"\", (f\"%{clean_paper}%\",))\n",
    "            rows = cursor.fetchall()\n",
    "        except Exception:\n",
    "            pass\n",
    "\n",
    "    # 3. Default fallback: Part 1: Digital Productivity & Statistics (Q1-60)\n",
    "    if not rows:\n",
    "        cursor.execute(\"\"\"\n",
    "            SELECT id, grade_level AS paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer\n",
    "            FROM questions\n",
    "            WHERE grade_level LIKE 'Part 1%'\n",
    "            ORDER BY question_number ASC\n",
    "        \"\"\")\n",
    "        rows = cursor.fetchall()\n",
    "        matched_paper = \"Part 1: Digital Productivity & Statistics (Q1-60)\"\n",
    "\n",
    "    # 4. Fallback to any questions\n",
    "    if not rows:\n",
    "        cursor.execute(\"\"\"\n",
    "            SELECT id, grade_level AS paper_code, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer\n",
    "            FROM questions\n",
    "            ORDER BY id ASC\n",
    "            LIMIT 60\n",
    "        \"\"\")\n",
    "        rows = cursor.fetchall()\n",
    "        matched_paper = \"Module 1: Digital Foundations\"\n",
    "\n",
    "    rows = [dict(r) for r in rows]\n",
    "\n",
    "    # Renumber sequentially 1..N\n",
    "    renumbered = []\n",
    "    for idx, r in enumerate(rows, start=1):\n",
    "        item = dict(r)\n",
    "        item[\"question_number\"] = idx\n",
    "        item[\"table\"] = source_table\n",
    "        if \"paper_code\" not in item or not item[\"paper_code\"]:\n",
    "            item[\"paper_code\"] = matched_paper\n",
    "        renumbered.append(item)\n",
    "\n",
    "    return renumbered, matched_paper\n",
    "\n"
]

new_lines = lines[:start_idx] + replacement + lines[end_idx:]

with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully replaced fetch_cbt_questions in app.py!")
