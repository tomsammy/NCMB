with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add toggle_anti_cheat and get_anti_cheat_status endpoints right after toggle_exam_status
anti_cheat_endpoints = """@router.post("/api/admin/toggle-exam-status")
def toggle_exam_status(auth: dict = Depends(verify_superadmin_auth)):
    current = get_setting("exam_status", "open")
    new_status = "closed" if current == "open" else "open"
    set_setting("exam_status", new_status)
    return {
        "success": True,
        "exam_status": new_status,
        "message": f"CBT Examination is now officially {'OPEN' if new_status == 'open' else 'CLOSED'}."
    }

@router.get("/api/admin/anti-cheat-status")
def get_anti_cheat_status(auth: dict = Depends(verify_superadmin_auth)):
    status = get_setting("anti_cheat_status", "enabled")
    return {
        "success": True,
        "anti_cheat_status": status,
        "anti_cheat_enabled": (status == "enabled"),
        "max_strikes": 3
    }

@router.post("/api/admin/toggle-anti-cheat")
def toggle_anti_cheat(auth: dict = Depends(verify_superadmin_auth)):
    current = get_setting("anti_cheat_status", "enabled")
    new_status = "disabled" if current == "enabled" else "enabled"
    set_setting("anti_cheat_status", new_status)
    is_enabled = (new_status == "enabled")
    return {
        "success": True,
        "anti_cheat_status": new_status,
        "anti_cheat_enabled": is_enabled,
        "max_strikes": 3,
        "message": f"Anti-Cheat Proctor Shield is now {'ACTIVE (3 Strikes Auto-Submit)' if is_enabled else 'DISABLED (Navigation Permitted)'}."
    }"""

old_toggle_target = """@router.post("/api/admin/toggle-exam-status")
def toggle_exam_status(auth: dict = Depends(verify_superadmin_auth)):
    current = get_setting("exam_status", "open")
    new_status = "closed" if current == "open" else "open"
    set_setting("exam_status", new_status)
    return {
        "success": True,
        "exam_status": new_status,
        "message": f"CBT Examination is now officially {'OPEN' if new_status == 'open' else 'CLOSED'}."
    }"""

code = code.replace(old_toggle_target, anti_cheat_endpoints)

# 2. Update get_exam_info
old_info_target = """    status = get_setting("exam_status", "open")
    
    return {
        "title": EXAM_TITLE,
        "org_name": ORGANIZATION_NAME,
        "grade_levels": levels if levels else ["Category A", "Category B", "General"],
        "default_duration_minutes": DEFAULT_DURATION_MINUTES,
        "questions_per_exam": QUESTIONS_PER_EXAM,
        "marks_per_question": MARKS_PER_QUESTION,
        "total_marks": TOTAL_MARKS,
        "exam_status": status
    }"""

new_info_target = """    status = get_setting("exam_status", "open")
    ac_status = get_setting("anti_cheat_status", "enabled")
    
    return {
        "title": EXAM_TITLE,
        "org_name": ORGANIZATION_NAME,
        "grade_levels": levels if levels else ["Category A", "Category B", "General"],
        "default_duration_minutes": DEFAULT_DURATION_MINUTES,
        "questions_per_exam": QUESTIONS_PER_EXAM,
        "marks_per_question": MARKS_PER_QUESTION,
        "total_marks": TOTAL_MARKS,
        "exam_status": status,
        "anti_cheat_status": ac_status,
        "anti_cheat_enabled": (ac_status == "enabled"),
        "max_strikes": 3
    }"""

code = code.replace(old_info_target, new_info_target)

# 3. Update start_exam_with_token response
old_start_target = """        "paper_code": loaded_paper,
        "total_questions": len(questions),
        "duration_minutes": DEFAULT_DURATION_MINUTES,
        "questions": questions
    }"""

new_start_target = """        "paper_code": loaded_paper,
        "total_questions": len(questions),
        "duration_minutes": DEFAULT_DURATION_MINUTES,
        "questions": questions,
        "anti_cheat_status": get_setting("anti_cheat_status", "enabled"),
        "anti_cheat_enabled": (get_setting("anti_cheat_status", "enabled") == "enabled"),
        "max_strikes": 3
    }"""

code = code.replace(old_start_target, new_start_target)

# 4. Update get_admin_dashboard_stats response
old_dash_target = """"exam_status": get_setting("exam_status", "open"),"""
new_dash_target = """"exam_status": get_setting("exam_status", "open"),
        "anti_cheat_status": get_setting("anti_cheat_status", "enabled"),
        "anti_cheat_enabled": (get_setting("anti_cheat_status", "enabled") == "enabled"),"""

code = code.replace(old_dash_target, new_dash_target)

with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app.py updated successfully with Anti-Cheat endpoints and settings!")
