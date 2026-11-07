import re
import sqlite3
import os

filepath = r'C:\Users\hp\Desktop\NCMB\sample_questions\raw_questions_with_answers.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse answers
answers = {}
# Look for tables with | 1 | C | 21 | C | ...
lines = text.split('\n')
for line in lines:
    if '|' in line:
        parts = [p.strip() for p in line.split('|') if p.strip()]
        # Check pairs
        # e.g., ['1', 'C', '21', 'C', '41', 'A']
        for i in range(0, len(parts)-1, 2):
            q_str = parts[i]
            ans_str = parts[i+1].upper()
            if q_str.isdigit() and ans_str in ['A', 'B', 'C', 'D']:
                answers[int(q_str)] = ans_str

print(f"Total parsed answers: {len(answers)}")
print(f"Sample answers: Q1={answers.get(1)}, Q60={answers.get(60)}, Q61={answers.get(61)}, Q180={answers.get(180)}")

# 2. Parse questions
# Split by numbering: e.g. "1. ", "2. ", ..., "180. "
q_blocks = re.split(r'\n(?=\d+\.\s+)', text)

parsed_questions = []

for block in q_blocks:
    m_num = re.match(r'^(\d+)\.\s+(.*)', block.strip(), re.DOTALL)
    if not m_num:
        continue
    q_num = int(m_num.group(1))
    body = m_num.group(2).strip()

    # Split question text from options
    # Options start with A.
    m_opt = re.search(r'(?=\bA\.\s*)', body)
    if not m_opt:
        continue
    
    q_text = body[:m_opt.start()].strip()
    options_str = body[m_opt.start():].strip()

    # Split options by A., B., C., D.
    opt_parts = re.split(r'(?=[A-D]\.\s*)', options_str)
    opts = {}
    for op in opt_parts:
        op = op.strip()
        m_letter = re.match(r'^([A-D])\.\s*(.*)', op, re.DOTALL)
        if m_letter:
            letter = m_letter.group(1).upper()
            val = m_letter.group(2).strip()
            # Clean trailing table or section headers if any in last option
            if '\nPART ' in val or '\nSECTION ' in val or '\nANSWER' in val:
                val = re.split(r'\n(?:PART|SECTION|ANSWER)', val)[0].strip()
            opts[letter] = val

    ans = answers.get(q_num, 'A')

    # Determine Part / Category
    if 1 <= q_num <= 60:
        category = "Module 1 - Part 1: Digital Foundations & Statistics"
        short_cat = "Part 1"
    elif 61 <= q_num <= 120:
        category = "Module 1 - Part 2: RDBMS & SQL Querying"
        short_cat = "Part 2"
    else:
        category = "Module 1 - Part 3: Data Governance & Oil and Gas Analytics"
        short_cat = "Part 3"

    parsed_questions.append({
        'number': q_num,
        'category': category,
        'short_cat': short_cat,
        'question': q_text,
        'option_a': opts.get('A', ''),
        'option_b': opts.get('B', ''),
        'option_c': opts.get('C', ''),
        'option_d': opts.get('D', ''),
        'answer': ans
    })

print(f"Total parsed questions: {len(parsed_questions)}")

# Verify first and last question
if parsed_questions:
    q1 = parsed_questions[0]
    print(f"\nQ1 ({q1['category']}):")
    print(f"  Stem: {q1['question'][:80]}...")
    print(f"  A: {q1['option_a'][:50]}")
    print(f"  B: {q1['option_b'][:50]}")
    print(f"  C: {q1['option_c'][:50]}")
    print(f"  D: {q1['option_d'][:50]}")
    print(f"  Answer: {q1['answer']}")

    q180 = parsed_questions[-1]
    print(f"\nQ180 ({q180['category']}):")
    print(f"  Stem: {q180['question'][:80]}...")
    print(f"  A: {q180['option_a'][:50]}")
    print(f"  B: {q180['option_b'][:50]}")
    print(f"  C: {q180['option_c'][:50]}")
    print(f"  D: {q180['option_d'][:50]}")
    print(f"  Answer: {q180['answer']}")

# Check any missing options or answers
missing = [q for q in parsed_questions if not q['option_a'] or not q['option_b'] or not q['option_c'] or not q['option_d'] or not q['answer']]
print(f"\nQuestions with incomplete options/answers: {len(missing)}")
if missing:
    for m in missing:
        print(f"  Incomplete Q{m['number']}: opts={m}")
