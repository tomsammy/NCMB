import os
import sqlite3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(current_dir, "cbt.db")

# 30 Candidate IDs
candidate_ids = [f"NCDMB-2026-{i:03d}" for i in range(1, 31)]

# The exact 40 PINs (30 candidate + 10 spare)
candidate_pins = [
    "27150", "48947", "81098", "73051", "96590",
    "78930", "72719", "91626", "40190", "51604",
    "39031", "64531", "91958", "81568", "41598",
    "58035", "36168", "23917", "67231", "75718",
    "81298", "75326", "64324", "58793", "56641",
    "65379", "94688", "83793", "69470", "32674"
]

spare_pins = [
    "29774", "67537", "24335", "30821", "58604",
    "47116", "30907", "95470", "79234", "67287"
]

all_40_pins = candidate_pins + spare_pins

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Clear existing candidates
cur.execute("DELETE FROM candidate_roster WHERE psn LIKE 'NCDMB-2026-%'")
cur.execute("DELETE FROM candidates WHERE psn LIKE 'NCDMB-2026-%'")
cur.execute("DELETE FROM submissions WHERE psn LIKE 'NCDMB-2026-%'")

# Populate candidate_roster and candidates with ONLY Candidate ID as identifier (no personal names)
exam_paper = "Part 1: Digital Productivity & Statistics (Q1-60)"

for i, cid in enumerate(candidate_ids):
    pin = candidate_pins[i]
    cur.execute("""
        INSERT INTO candidate_roster (
            psn, name, code_1, mda, exam_code, proposed_rank, proposed_gl,
            group_category, exam_date, batch_session, batch_time, accreditation_time,
            test_duration_minutes, phone, email, registration_status, registered_at
        ) VALUES (?, ?, ?, 'NCDMB', ?, 'Candidate', 'Module 1',
                  'GROUP A', '2026-11-07', 'Session 1', '09:00 AM', '08:30 AM',
                  60, '', '', 'registered', CURRENT_TIMESTAMP)
    """, (cid, cid, pin, exam_paper))

    cur.execute("""
        INSERT INTO candidates (
            name, psn, email, grade_level, mda
        ) VALUES (?, ?, '', 'Module 1', 'NCDMB')
    """, (cid, cid))

# Ensure all 40 tokens are unassigned in exam_tokens
for pin in all_40_pins:
    cur.execute("SELECT id FROM exam_tokens WHERE token_code = ?", (pin,))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO exam_tokens (token_code, status) VALUES (?, 'unassigned')", (pin,))
    else:
        cur.execute("UPDATE exam_tokens SET status = 'unassigned', assigned_to_psn = NULL WHERE token_code = ?", (pin,))

conn.commit()
conn.close()
print("Database updated: 30 candidates with NO personal names, identifier is Candidate ID only.")

# ----------------- CREATE EXCEL WORKBOOK -----------------
wb = openpyxl.Workbook()

# NCDMB Corporate Palette
NCDMB_GREEN = "00563F"
NCDMB_DARK_GREEN = "003627"
NCDMB_GOLD = "E5A823"
LIGHT_GREEN_BG = "F0FDF4"
LIGHT_GOLD_BG = "FEF9C3"
BORDER_COLOR = "CBD5E1"
DARK_GRAY = "1E293B"

font_title = Font(name="Calibri", size=15, bold=True, color=NCDMB_GREEN)
font_subtitle = Font(name="Calibri", size=10, italic=True, color="475569")
font_th = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_cid = Font(name="Consolas", size=12, bold=True, color=NCDMB_DARK_GREEN)
font_pin = Font(name="Consolas", size=13, bold=True, color="B91C1C")
font_bold = Font(name="Calibri", size=11, bold=True, color=DARK_GRAY)
font_regular = Font(name="Calibri", size=11, color=DARK_GRAY)

fill_th = PatternFill(start_color=NCDMB_GREEN, end_color=NCDMB_GREEN, fill_type="solid")
fill_spare_th = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
fill_pin = PatternFill(start_color=LIGHT_GOLD_BG, end_color=LIGHT_GOLD_BG, fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color=BORDER_COLOR),
    right=Side(style='thin', color=BORDER_COLOR),
    top=Side(style='thin', color=BORDER_COLOR),
    bottom=Side(style='thin', color=BORDER_COLOR)
)

# ----------------- SHEET 1: CANDIDATE ID & LOGIN PIN ROSTER -----------------
ws1 = wb.active
ws1.title = "Candidate ID Roster"

# Title Header
ws1.merge_cells("A1:F1")
ws1["A1"] = "NIGERIAN CONTENT DEVELOPMENT AND MONITORING BOARD (NCDMB)"
ws1["A1"].font = font_title
ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[1].height = 28

ws1.merge_cells("A2:F2")
ws1["A2"] = "Assessment on Module 1: Digital Foundations — Official Candidate ID & CBT Login PIN Roster (No Personal Names)"
ws1["A2"].font = font_subtitle
ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[2].height = 18

ws1.append([]) # Row 3 blank

headers1 = [
    "S/N",
    "Candidate ID",
    "Assigned Assessment Paper",
    "Duration",
    "5-Digit CBT Login PIN",
    "Candidate Sign-in / Verification"
]
ws1.append(headers1)
ws1.row_dimensions[4].height = 28

for col_idx in range(1, len(headers1) + 1):
    cell = ws1.cell(row=4, column=col_idx)
    cell.font = font_th
    cell.fill = fill_th
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

for idx, cid in enumerate(candidate_ids, start=1):
    r_idx = idx + 4
    pin = candidate_pins[idx - 1]
    ws1.append([idx, cid, exam_paper, "60 Minutes", pin, ""])
    ws1.row_dimensions[r_idx].height = 24

    c_sn = ws1.cell(row=r_idx, column=1)
    c_sn.alignment = Alignment(horizontal="center", vertical="center")
    c_sn.font = font_regular

    c_cid = ws1.cell(row=r_idx, column=2)
    c_cid.font = font_cid
    c_cid.alignment = Alignment(horizontal="center", vertical="center")

    c_paper = ws1.cell(row=r_idx, column=3)
    c_paper.font = font_regular
    c_paper.alignment = Alignment(horizontal="left", vertical="center")

    c_dur = ws1.cell(row=r_idx, column=4)
    c_dur.font = font_bold
    c_dur.alignment = Alignment(horizontal="center", vertical="center")

    c_pin = ws1.cell(row=r_idx, column=5)
    c_pin.font = font_pin
    c_pin.fill = fill_pin
    c_pin.alignment = Alignment(horizontal="center", vertical="center")

    c_sig = ws1.cell(row=r_idx, column=6)
    c_sig.alignment = Alignment(horizontal="center", vertical="center")

    for col in range(1, 7):
        ws1.cell(row=r_idx, column=col).border = thin_border
        if idx % 2 == 0 and col != 5:
            ws1.cell(row=r_idx, column=col).fill = fill_zebra

ws1.column_dimensions['A'].width = 8
ws1.column_dimensions['B'].width = 22
ws1.column_dimensions['C'].width = 46
ws1.column_dimensions['D'].width = 16
ws1.column_dimensions['E'].width = 24
ws1.column_dimensions['F'].width = 30

# ----------------- SHEET 2: SUPERVISOR RESERVE PINS (10 SPARE) -----------------
ws2 = wb.create_sheet(title="Supervisor Reserve PINs")

ws2.merge_cells("A1:E1")
ws2["A1"] = "NCDMB CBT PORTAL — SUPERVISOR RESERVE CBT LOGIN PINS"
ws2["A1"].font = font_title
ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 28

ws2.merge_cells("A2:E2")
ws2["A2"] = "Emergency reserve PINs for technical device swaps, replacement logins, or makeup candidate evaluations."
ws2["A2"].font = font_subtitle
ws2["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[2].height = 18

ws2.append([])

headers2 = [
    "Reserve S/N",
    "5-Digit CBT Login PIN",
    "Status",
    "Assigned Candidate ID (Emergency Issue)",
    "Supervisor Sign-off"
]
ws2.append(headers2)
ws2.row_dimensions[4].height = 28

for col_idx in range(1, len(headers2) + 1):
    cell = ws2.cell(row=4, column=col_idx)
    cell.font = font_th
    cell.fill = fill_spare_th
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

for j, pin in enumerate(spare_pins, start=1):
    r_idx = j + 4
    ws2.append([f"SPARE-{j:02d}", pin, "Available / Unassigned", "", ""])
    ws2.row_dimensions[r_idx].height = 24

    ws2.cell(row=r_idx, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=r_idx, column=1).font = font_bold

    ws2.cell(row=r_idx, column=2).font = font_pin
    ws2.cell(row=r_idx, column=2).fill = fill_pin
    ws2.cell(row=r_idx, column=2).alignment = Alignment(horizontal="center", vertical="center")

    ws2.cell(row=r_idx, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=r_idx, column=3).font = font_bold

    for col in range(1, 6):
        ws2.cell(row=r_idx, column=col).border = thin_border
        if j % 2 == 0 and col != 2:
            ws2.cell(row=r_idx, column=col).fill = fill_zebra

ws2.column_dimensions['A'].width = 16
ws2.column_dimensions['B'].width = 24
ws2.column_dimensions['C'].width = 26
ws2.column_dimensions['D'].width = 38
ws2.column_dimensions['E'].width = 26

# ----------------- SHEET 3: PRINTABLE CANDIDATE CUTOUT SLIPS -----------------
ws3 = wb.create_sheet(title="Printable Hall Slips")

ws3.merge_cells("A1:D1")
ws3["A1"] = "NCDMB CBT ASSESSMENT — PRINTABLE CANDIDATE LOGIN SLIPS"
ws3["A1"].font = font_title
ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[1].height = 26

ws3.merge_cells("A2:D2")
ws3["A2"] = "Cut along cell borders to distribute individual slips to candidates in the examination hall."
ws3["A2"].font = font_subtitle
ws3["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[2].height = 18

ws3.append([])

slip_border_thick = Border(
    left=Side(style='medium', color=NCDMB_GREEN),
    right=Side(style='medium', color=NCDMB_GREEN),
    top=Side(style='medium', color=NCDMB_GREEN),
    bottom=Side(style='medium', color=NCDMB_GREEN)
)

row_start = 4
for i, cid in enumerate(candidate_ids):
    pin = candidate_pins[i]
    col_start = 1 if i % 2 == 0 else 3
    r = row_start + (i // 2) * 5

    # Header line of slip
    c_head = ws3.cell(row=r, column=col_start)
    c_head.value = "NIGERIAN CONTENT DEVELOPMENT & MONITORING BOARD"
    c_head.font = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    c_head.fill = fill_th
    c_head.alignment = Alignment(horizontal="center", vertical="center")

    # Assessment title
    c_sub = ws3.cell(row=r+1, column=col_start)
    c_sub.value = "Module 1 Assessment: Digital Foundations (60 Mins)"
    c_sub.font = Font(name="Calibri", size=9, bold=True, color=NCDMB_DARK_GREEN)
    c_sub.alignment = Alignment(horizontal="center", vertical="center")

    # Candidate ID
    c_id = ws3.cell(row=r+2, column=col_start)
    c_id.value = f"Candidate ID: {cid}"
    c_id.font = Font(name="Consolas", size=13, bold=True, color=DARK_GRAY)
    c_id.alignment = Alignment(horizontal="center", vertical="center")

    # Login PIN
    c_p = ws3.cell(row=r+3, column=col_start)
    c_p.value = f"5-Digit Login PIN: {pin}"
    c_p.font = Font(name="Consolas", size=14, bold=True, color="B91C1C")
    c_p.fill = fill_pin
    c_p.alignment = Alignment(horizontal="center", vertical="center")

    # Apply borders
    for offset in range(4):
        ws3.cell(row=r+offset, column=col_start).border = thin_border
        ws3.row_dimensions[r+offset].height = 20

ws3.column_dimensions['A'].width = 44
ws3.column_dimensions['B'].width = 4
ws3.column_dimensions['C'].width = 44
ws3.column_dimensions['D'].width = 4

# Save workbook
excel_path = os.path.join(current_dir, "NCDMB_Candidates_and_CBT_PINs.xlsx")
wb.save(excel_path)
print(f"Excel workbook regenerated successfully at: {excel_path}")
