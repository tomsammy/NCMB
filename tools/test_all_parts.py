import sys
sys.path.insert(0, r'C:\Users\hp\Desktop\NCMB')
from fastapi.testclient import TestClient
from app import app
from database import get_db_connection

client = TestClient(app)
papers = [
    'Part 1: Digital Productivity & Statistics (Q1-60)',
    'Part 2: SQL & RDBMS (Q61-120)',
    'Part 3: Data Governance & Oil and Gas (Q121-180)',
    'Module 1: Digital Foundations (Full 180 Questions)'
]

for p in papers:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT token_code FROM exam_tokens WHERE status = 'unassigned' LIMIT 1")
    tok = cur.fetchone()['token_code']
    cur.execute("UPDATE candidate_roster SET exam_code = ? WHERE psn = 'NCDMB-999-001'", (p,))
    conn.commit()
    conn.close()

    res = client.post('/api/exam/start-with-token', json={'psn': 'NCDMB-999-001', 'token_code': tok})
    data = res.json()
    qs_count = len(data.get('questions', []))
    dur = data.get('duration_minutes')
    print(f"{p} -> Status: {res.status_code}, Qs: {qs_count}, Duration: {dur} mins")
