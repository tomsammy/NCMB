import os
import sys
import sqlite3
import random
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure directory is on path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(current_dir, "cbt.db")

candidates_data = [
    ("NCDMB-2026-001", "Tariere Briggs", "Monitoring & Evaluation", "Senior Officer", "GL 10"),
    ("NCDMB-2026-002", "Tamunotonye Lawson", "Planning, Research & Statistics", "Principal Officer", "GL 12"),
    ("NCDMB-2026-003", "Diepreye Amadi", "Directorate of Capacity Building", "Senior Officer", "GL 10"),
    ("NCDMB-2026-004", "Ebiere Okoyen", "Corporate Services & Administration", "Officer I", "GL 09"),
    ("NCDMB-2026-005", "Ibifubara Jumbo", "ICT & Digital Transformation Division", "Senior Officer", "GL 10"),
    ("NCDMB-2026-006", "Tonbara Douglas", "Upstream Monitoring Directorate", "Principal Officer", "GL 12"),
    ("NCDMB-2026-007", "Ayebatari George", "Midstream & Downstream Directorate", "Officer I", "GL 09"),
    ("NCDMB-2026-008", "Chinedu Eze", "Project Certification & Authorisation", "Senior Officer", "GL 10"),
    ("NCDMB-2026-009", "Amina Bello", "Finance & Accounts Directorate", "Principal Officer", "GL 12"),
    ("NCDMB-2026-010", "Babatunde Adeleke", "Legal Services Directorate", "Senior Legal Officer", "GL 10"),
    ("NCDMB-2026-011", "Preye Kuro", "Nigerian Content Development Fund (NCDF)", "Officer I", "GL 09"),
    ("NCDMB-2026-012", "Ovie Oghenekaro", "Capacity Building & Training", "Senior Officer", "GL 10"),
    ("NCDMB-2026-013", "Ngozi Okonkwo", "Strategy & Development Division", "Assistant Manager", "GL 13"),
    ("NCDMB-2026-014", "Yakubu Mohammed", "Gas Monitoring & Compliance", "Officer I", "GL 09"),
    ("NCDMB-2026-015", "Folashade Adeyemi", "Human Resources Division", "Senior Officer", "GL 10"),
    ("NCDMB-2026-016", "Ebikeme Williams", "Pipelines & Facility Monitoring", "Principal Officer", "GL 12"),
    ("NCDMB-2026-017", "Ifeanyi Nwosu", "Data Analytics & Research Unit", "Senior Analyst", "GL 10"),
    ("NCDMB-2026-018", "Zainab Suleiman", "Corporate Communications Unit", "Officer I", "GL 09"),
    ("NCDMB-2026-019", "Biobelema Jack", "Internal Audit Division", "Senior Officer", "GL 10"),
    ("NCDMB-2026-020", "Oluwaseun Fashola", "Procurement Division", "Officer I", "GL 09"),
    ("NCDMB-2026-021", "Kemebradikumo Clark", "Offshore Operations Monitoring", "Principal Officer", "GL 12"),
    ("NCDMB-2026-022", "Halima Garba", "Records & Documentation Division", "Officer II", "GL 08"),
    ("NCDMB-2026-023", "Emeka Nnamdi", "Petroleum Technology Development", "Senior Officer", "GL 10"),
    ("NCDMB-2026-024", "Blessing Diri", "Corporate Services Directorate", "Officer I", "GL 09"),
    ("NCDMB-2026-025", "Usman Danladi", "Information Technology Services", "Senior Systems Officer", "GL 10"),
    ("NCDMB-2026-026", "Sotonye Peters", "Quality Assurance & Compliance", "Principal Officer", "GL 12"),
    ("NCDMB-2026-027", "Abiodun Bakare", "Downstream Compliance Division", "Officer I", "GL 09"),
    ("NCDMB-2026-028", "Timipre Spiff", "Local Content Operations Unit", "Senior Officer", "GL 10"),
    ("NCDMB-2026-029", "Chinwe Anya", "Planning & Strategic Initiatives", "Assistant Manager", "GL 13"),
    ("NCDMB-2026-030", "Godswill Epelle", "Field Operations & Logistics", "Officer I", "GL 09")
]

# Generate 40 clean, distinct 5-digit PINs
random.seed(42819)
pins = []
seen = set()
while len(pins) < 40:
    pin_val = random.randint(23145, 98765)
    pin_str = str(pin_val)
    if len(set(pin_str)) >= 4 and pin_str not in seen:
        seen.add(pin_str)
        pins.append(pin_str)

candidate_pins = pins[:30]
spare_pins = pins[30:40]

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Clear old non-test entries or refresh candidate_roster
cur.execute("DELETE FROM candidate_roster WHERE psn LIKE 'NCDMB-2026-%'")
cur.execute("DELETE FROM candidates WHERE psn LIKE 'NCDMB-2026-%'")

# 2. Insert the 30 candidates into candidate_roster and candidates
for i, (cid, name, mda, rank, gl) in enumerate(candidates_data):
    assigned_pin = candidate_pins[i]
    exam_paper = "Part 1: Digital Productivity & Statistics (Q1-60)"
    
    cur.execute("""
        INSERT INTO candidate_roster (
            psn, name, code_1, mda, exam_code, proposed_rank, proposed_gl,
            group_category, exam_date, batch_session, batch_time, accreditation_time,
            test_duration_minutes, phone, email, registration_status, registered_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'registered', CURRENT_TIMESTAMP)
    """, (
        cid, name, assigned_pin, mda, exam_paper, rank, gl,
        "GROUP A", "2026-11-07", "Session 1", "09:00 AM", "08:30 AM",
        60, f"0803{i+1000000:07d}", f"{name.lower().replace(' ', '.')}@ncdmb.gov.ng"
    ))

    cur.execute("""
        INSERT INTO candidates (
            name, psn, email, grade_level, mda
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        name, cid, f"{name.lower().replace(' ', '.')}@ncdmb.gov.ng", gl, mda
    ))

# 3. Insert or update the 40 tokens into exam_tokens
for pin in pins:
    cur.execute("SELECT id FROM exam_tokens WHERE token_code = ?", (pin,))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO exam_tokens (token_code, status) VALUES (?, 'unassigned')", (pin,))
    else:
        cur.execute("UPDATE exam_tokens SET status = 'unassigned', assigned_to_psn = NULL WHERE token_code = ?", (pin,))

conn.commit()
conn.close()
print("Database successfully populated with 30 candidates and 40 tokens!")

# 4. Generate Professional Excel Roster with Styling
wb = openpyxl.Workbook()

# Colors
NCDMB_GREEN = "00563F"
NCDMB_GOLD = "E5A823"
LIGHT_GREEN = "E8F5E9"
LIGHT_GOLD = "FFF9C4"
BORDER_GRAY = "CCCCCC"

header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
title_font = Font(name="Calibri", size=14, bold=True, color=NCDMB_GREEN)
subtitle_font = Font(name="Calibri", size=10, italic=True, color="444444")
bold_font = Font(name="Calibri", size=11, bold=True)
regular_font = Font(name="Calibri", size=11)
code_font = Font(name="Consolas", size=12, bold=True, color="003627")
pin_font = Font(name="Consolas", size=13, bold=True, color="B71C1C")

header_fill = PatternFill(start_color=NCDMB_GREEN, end_color=NCDMB_GREEN, fill_type="solid")
spare_header_fill = PatternFill(start_color="374151", end_color="374151", fill_type="solid")
zebra_fill = PatternFill(start_color="F8FAF9", end_color="F8FAF9", fill_type="solid")
pin_fill = PatternFill(start_color=LIGHT_GOLD, end_color=LIGHT_GOLD, fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color=BORDER_GRAY),
    right=Side(style='thin', color=BORDER_GRAY),
    top=Side(style='thin', color=BORDER_GRAY),
    bottom=Side(style='thin', color=BORDER_GRAY)
)

# ----------------- SHEET 1: CANDIDATE ROSTER & LOGIN PINS -----------------
ws1 = wb.active
ws1.title = "Candidate Roster & PINs"

# Title block
ws1.merge_cells("A1:G1")
ws1["A1"] = "NIGERIAN CONTENT DEVELOPMENT AND MONITORING BOARD (NCDMB)"
ws1["A1"].font = title_font
ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[1].height = 25

ws1.merge_cells("A2:G2")
ws1["A2"] = "Assessment on Module 1: Digital Foundations — Official Candidate Hall Accreditation & CBT Login PIN Roster"
ws1["A2"].font = subtitle_font
ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[2].height = 18

ws1.append([]) # Blank row 3

# Table Headers
headers1 = [
    "S/N", "Candidate ID", "Candidate Full Name", "Directorate / Department",
    "Designation / Rank", "Duration", "5-Digit CBT Login PIN"
]
ws1.append(headers1)
ws1.row_dimensions[4].height = 26

for col_num in range(1, len(headers1) + 1):
    cell = ws1.cell(row=4, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

for i, (cid, name, mda, rank, gl) in enumerate(candidates_data, start=1):
    row_num = i + 4
    pin = candidate_pins[i-1]
    row_data = [i, cid, name, mda, rank, "60 Mins", pin]
    ws1.append(row_data)
    ws1.row_dimensions[row_num].height = 22

    # Formatting cells
    c_sn = ws1.cell(row=row_num, column=1)
    c_sn.alignment = Alignment(horizontal="center", vertical="center")
    
    c_id = ws1.cell(row=row_num, column=2)
    c_id.font = code_font
    c_id.alignment = Alignment(horizontal="center", vertical="center")

    c_name = ws1.cell(row=row_num, column=3)
    c_name.font = bold_font
    c_name.alignment = Alignment(horizontal="left", vertical="center")

    c_dept = ws1.cell(row=row_num, column=4)
    c_dept.font = regular_font
    c_dept.alignment = Alignment(horizontal="left", vertical="center")

    c_rank = ws1.cell(row=row_num, column=5)
    c_rank.font = regular_font
    c_rank.alignment = Alignment(horizontal="left", vertical="center")

    c_dur = ws1.cell(row=row_num, column=6)
    c_dur.font = bold_font
    c_dur.alignment = Alignment(horizontal="center", vertical="center")

    c_pin = ws1.cell(row=row_num, column=7)
    c_pin.font = pin_font
    c_pin.fill = pin_fill
    c_pin.alignment = Alignment(horizontal="center", vertical="center")

    for col in range(1, 8):
        ws1.cell(row=row_num, column=col).border = thin_border
        if i % 2 == 0 and col != 7:
            ws1.cell(row=row_num, column=col).fill = zebra_fill

# Column widths
ws1.column_dimensions['A'].width = 8
ws1.column_dimensions['B'].width = 18
ws1.column_dimensions['C'].width = 28
ws1.column_dimensions['D'].width = 40
ws1.column_dimensions['E'].width = 24
ws1.column_dimensions['F'].width = 14
ws1.column_dimensions['G'].width = 24

# ----------------- SHEET 2: SUPERVISOR RESERVE PINS -----------------
ws2 = wb.create_sheet(title="Supervisor Reserve PINs")

ws2.merge_cells("A1:D1")
ws2["A1"] = "NCDMB CBT PORTAL — SUPERVISOR RESERVE CBT LOGIN PINS"
ws2["A1"].font = title_font
ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 25

ws2.merge_cells("A2:D2")
ws2["A2"] = "Unassigned emergency reserve PINs for candidate technical reassignment, device swaps, or makeup assessments."
ws2["A2"].font = subtitle_font
ws2["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[2].height = 18

ws2.append([])

headers2 = ["Reserve S/N", "5-Digit CBT Login PIN", "Status", "Usage Remarks / Assigned Candidate"]
ws2.append(headers2)
ws2.row_dimensions[4].height = 26

for col_num in range(1, len(headers2) + 1):
    cell = ws2.cell(row=4, column=col_num)
    cell.font = header_font
    cell.fill = spare_header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = thin_border

for j, pin in enumerate(spare_pins, start=1):
    r_num = j + 4
    ws2.append([f"SPARE-{j:02d}", pin, "Available / Unassigned", ""])
    ws2.row_dimensions[r_num].height = 22

    ws2.cell(row=r_num, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=r_num, column=1).font = bold_font

    ws2.cell(row=r_num, column=2).font = pin_font
    ws2.cell(row=r_num, column=2).fill = pin_fill
    ws2.cell(row=r_num, column=2).alignment = Alignment(horizontal="center", vertical="center")

    ws2.cell(row=r_num, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=r_num, column=3).font = bold_font

    for c in range(1, 5):
        ws2.cell(row=r_num, column=c).border = thin_border

ws2.column_dimensions['A'].width = 16
ws2.column_dimensions['B'].width = 24
ws2.column_dimensions['C'].width = 26
ws2.column_dimensions['D'].width = 40

# Save Workbook
excel_out_path = os.path.join(current_dir, "NCDMB_Candidates_and_CBT_PINs.xlsx")
wb.save(excel_out_path)
print(f"Excel file created successfully at: {excel_out_path}")
