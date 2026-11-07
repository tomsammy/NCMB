with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace read_index to add aggressive anti-cache headers
old_read_index = '''@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def read_index():
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html"),
        os.path.join(os.getcwd(), "kwara_cbt_app", "static", "index.html"),
        os.path.join(os.getcwd(), "public", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            with open(c, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>KWARA STATE CIVIL SERVICE COMMISSION - 2026 Promotion Evaluation CBT Examination</h1>"'''

new_read_index = '''@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def read_index():
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html"),
        os.path.join(os.getcwd(), "kwara_cbt_app", "static", "index.html"),
        os.path.join(os.getcwd(), "public", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            with open(c, "r", encoding="utf-8") as f:
                content = f.read()
                return HTMLResponse(
                    content=content,
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )
    return "<h1>Nigerian Content Development and Monitoring Board (NCDMB) CBT Portal</h1>"'''

if old_read_index in code:
    code = code.replace(old_read_index, new_read_index)
    print("Updated read_index with anti-cache headers!")
else:
    print("Could not match old_read_index directly")

# 2. Replace auto-provisioning "Staff"
old_prov = 'psn, f"Staff ({psn})", "NCDMB Operations", "Part 1: Digital Productivity & Statistics (Q1-60)",\n                "Staff", "Module 1", "GROUP A", DEFAULT_DURATION_MINUTES'
new_prov = 'psn, psn, "NCDMB Operations", "Part 1: Digital Productivity & Statistics (Q1-60)",\n                "Candidate", "Module 1", "GROUP A", DEFAULT_DURATION_MINUTES'

if old_prov in code:
    code = code.replace(old_prov, new_prov)
    print("Updated candidate auto-provisioning to remove Staff!")
else:
    print("Could not match old_prov")

with open(r'C:\Users\hp\Desktop\NCMB\app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved app.py updates!")
