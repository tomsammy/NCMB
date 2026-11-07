import re
import os

path = r"C:\Users\hp\Desktop\NCMB\app.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add middleware
cors_target = """app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

middleware_code = """app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel serverless path adaptation middleware
@app.middleware("http")
async def vercel_path_rewrite_middleware(request: Request, call_next):
    raw_path = request.scope.get("path", "")
    if raw_path.startswith("/api/index.py"):
        new_path = raw_path[len("/api/index.py"):] or "/"
        request.scope["path"] = new_path
    elif raw_path.startswith("/api/index"):
        new_path = raw_path[len("/api/index"):] or "/"
        request.scope["path"] = new_path
    return await call_next(request)"""

if cors_target in text:
    text = text.replace(cors_target, middleware_code, 1)
    print("Added vercel_path_rewrite_middleware!")
else:
    print("CORS target not found!")

# 2. Add extra routes to read_index
routes_target = """@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def read_index():"""

routes_replacement = """@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
def read_index():"""

if routes_target in text:
    text = text.replace(routes_target, routes_replacement, 1)
    print("Added extra Vercel route aliases to read_index!")
else:
    print("Routes target not found!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Saved app.py updates!")
