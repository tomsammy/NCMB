import os
import re
import sqlite3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

raw_file = r'C:\Users\hp\Desktop\NCMB\sample_questions\raw_questions_with_answers.txt'
db_file = r'C:\Users\hp\Desktop\NCMB\cbt.db'

with open(raw_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse answers
answers = {}
lines = text.split('\n')
for line in lines:
    if '|' in line:
        parts = [p.strip() for p in line.split('|') if p.strip()]
        for i in range(0, len(parts)-1, 2):
            q_str = parts[i]
            ans_str = parts[i+1].upper()
            if q_str.isdigit() and ans_str in ['A', 'B', 'C', 'D']:
                answers[int(q_str)] = ans_str

# 2. Parse questions
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
        part_name = "Part 1 (Digital Productivity & Statistics)"
        part_num = 1
        part_idx = q_num
    elif 61 <= q_num <= 120:
        part_name = "Part 2 (SQL & Relational Databases)"
        part_num = 2
        part_idx = q_num - 60
    else:
        part_name = "Part 3 (Data Governance & Oil and Gas Analytics)"
        part_num = 3
        part_idx = q_num - 120

    parsed_questions.append({
        'number': q_num,
        'part_num': part_num,
        'part_name': part_name,
        'part_idx': part_idx,
        'question': q_text,
        'option_a': opts.get('A', ''),
        'option_b': opts.get('B', ''),
        'option_c': opts.get('C', ''),
        'option_d': opts.get('D', ''),
        'answer': ans
    })

print(f"Parsed {len(parsed_questions)} questions successfully.")

# 3. Seed into SQLite database
conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Clear existing questions
cur.execute("DELETE FROM questions;")

# Insert Set 1: Full Assessment (All 180 questions)
full_category = "Module 1: Digital Foundations (Full 180 Questions)"
for q in parsed_questions:
    cur.execute("""
        INSERT INTO questions (
            grade_level, question_number, question_text,
            option_a, option_b, option_c, option_d, correct_answer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_category, q['number'], q['question'],
        q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer']
    ))

# Insert Set 2: Part 1 (Q1 - Q60)
p1_cat = "Part 1: Digital Productivity & Statistics (Q1-60)"
for q in [x for x in parsed_questions if x['part_num'] == 1]:
    cur.execute("""
        INSERT INTO questions (
            grade_level, question_number, question_text,
            option_a, option_b, option_c, option_d, correct_answer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p1_cat, q['part_idx'], q['question'],
        q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer']
    ))

# Insert Set 3: Part 2 (Q61 - Q120)
p2_cat = "Part 2: SQL & RDBMS (Q61-120)"
for q in [x for x in parsed_questions if x['part_num'] == 2]:
    cur.execute("""
        INSERT INTO questions (
            grade_level, question_number, question_text,
            option_a, option_b, option_c, option_d, correct_answer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p2_cat, q['part_idx'], q['question'],
        q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer']
    ))

# Insert Set 4: Part 3 (Q121 - Q180)
p3_cat = "Part 3: Data Governance & Oil and Gas (Q121-180)"
for q in [x for x in parsed_questions if x['part_num'] == 3]:
    cur.execute("""
        INSERT INTO questions (
            grade_level, question_number, question_text,
            option_a, option_b, option_c, option_d, correct_answer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p3_cat, q['part_idx'], q['question'],
        q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['answer']
    ))

conn.commit()

# Check count
cur.execute("SELECT grade_level, count(*) FROM questions GROUP BY grade_level ORDER BY grade_level")
counts = cur.fetchall()
print("\nQuestions seeded into database:")
for cat, cnt in counts:
    print(f"  {cat}: {cnt} questions")

conn.close()

# 4. Generate Master Excel File
excel_path = r'C:\Users\hp\Desktop\NCMB\sample_questions\NCDMB_Module_1_Digital_Foundations_180_Questions.xlsx'
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "NCDMB Module 1 Questions"

headers = ["Question #", "Module & Part", "Question Stem", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
ws.append(headers)

# Styling header
green_fill = PatternFill(start_color="00563F", end_color="00563F", fill_type="solid")
white_bold = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left = Alignment(horizontal="left", vertical="center", wrap_text=True)

for col_idx in range(1, len(headers)+1):
    cell = ws.cell(row=1, column=col_idx)
    cell.fill = green_fill
    cell.font = white_bold
    cell.alignment = center

ws.row_dimensions[1].height = 28

for q in parsed_questions:
    ws.append([
        q['number'],
        q['part_name'],
        q['question'],
        q['option_a'],
        q['option_b'],
        q['option_c'],
        q['option_d'],
        q['answer']
    ])

# Adjust column widths
ws.column_dimensions['A'].width = 12
ws.column_dimensions['B'].width = 30
ws.column_dimensions['C'].width = 65
ws.column_dimensions['D'].width = 35
ws.column_dimensions['E'].width = 35
ws.column_dimensions['F'].width = 35
ws.column_dimensions['G'].width = 35
ws.column_dimensions['H'].width = 15

wb.save(excel_path)
print(f"\nGenerated master Excel spreadsheet: {excel_path}")

# 5. Generate Master Word Document
docx_path = r'C:\Users\hp\Desktop\NCMB\sample_questions\NCDMB_Module_1_Digital_Foundations_180_Questions.docx'
doc = Document()

# Add Title
p_title = doc.add_paragraph()
r_title = p_title.add_run("NIGERIAN CONTENT DEVELOPMENT AND MONITORING BOARD (NCDMB)")
r_title.bold = True
r_title.font.size = Pt(16)
r_title.font.color.rgb = RGBColor(0x00, 0x56, 0x3F)
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

p_sub = doc.add_paragraph()
r_sub = p_sub.add_run("ASSESSMENT ON MODULE 1: DIGITAL FOUNDATIONS\nOfficial Master Question Bank & Answer Keys")
r_sub.bold = True
r_sub.font.size = Pt(13)
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

p_inst = doc.add_paragraph()
p_inst.add_run("Instructions: Answer all questions. Each question carries equal marks (1.0 mark each). Select the single most appropriate option from A–D.").italic = True
doc.add_paragraph()

current_part = None
for q in parsed_questions:
    if q['part_name'] != current_part:
        current_part = q['part_name']
        p_part = doc.add_paragraph()
        r_part = p_part.add_run(f"\n--- {current_part.upper()} ---")
        r_part.bold = True
        r_part.font.size = Pt(13)
        r_part.font.color.rgb = RGBColor(0x00, 0x56, 0x3F)
        
    p_q = doc.add_paragraph()
    r_q = p_q.add_run(f"{q['number']}. {q['question']}")
    r_q.bold = True
    
    doc.add_paragraph(f"A. {q['option_a']}")
    doc.add_paragraph(f"B. {q['option_b']}")
    doc.add_paragraph(f"C. {q['option_c']}")
    doc.add_paragraph(f"D. {q['option_d']}")
    
    p_ans = doc.add_paragraph()
    r_ans = p_ans.add_run(f"Correct Answer: {q['answer']}")
    r_ans.bold = True
    r_ans.font.color.rgb = RGBColor(0x00, 0x7A, 0x58)

doc.save(docx_path)
print(f"Generated master Word document: {docx_path}")
print("ALL DONE SUCCESSFULLY!")
