import sys
sys.path.insert(0, r'C:\Users\hp\Desktop\NCMB')
from fastapi.testclient import TestClient
from app import app
import sqlite3

conn = sqlite3.connect(r'C:\Users\hp\Desktop\NCMB\cbt.db')
cur = conn.cursor()
cur.execute("SELECT token_code FROM exam_tokens WHERE status = 'unassigned' LIMIT 1")
row = cur.fetchone()
tok = row[0] if row else "12345"
conn.close()

client = TestClient(app)
res = client.post('/api/exam/start-with-token', json={'psn': 'NCDMB-999-001', 'token_code': tok})
print('Status:', res.status_code)
if res.status_code == 200:
    data = res.json()
    print('Paper:', data.get('paper_code'))
    print('Questions count:', len(data.get('questions', [])))
    print('Duration minutes:', data.get('duration_minutes'))
    print('Q1:', data['questions'][0]['question'][:70], '...')
else:
    print('Error:', res.text)
