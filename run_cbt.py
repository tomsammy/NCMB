import os
import sys
import webbrowser
import threading
import time
import uvicorn

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
os.chdir(current_dir)

from database import init_db, load_env_file
from parser import seed_database

load_env_file()

ORG_NAME = os.environ.get("ORGANIZATION_NAME", "Nigerian Content Development and Monitoring Board (NCDMB)")
EXAM_TITLE = os.environ.get("EXAM_TITLE", "Assessment on Module 1: Digital Foundations")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))


def open_browser():
    time.sleep(1.8)
    url = f"http://{HOST}:{PORT}"
    print("\n" + "=" * 65)
    print(f"  {ORG_NAME}")
    print(f"  {EXAM_TITLE}")
    print(f"  Live Server URL: {url}")
    print(f"  Admin Dashboard: {url}/#admin")
    print("=" * 65)
    print("Opening browser automatically...\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")


def main():
    print(f"Initializing {ORG_NAME} CBT Examination Platform...")
    init_db()
    seed_database()

    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch Uvicorn server
    uvicorn.run("app:app", host=HOST, port=PORT, log_level="info", reload=False)


if __name__ == "__main__":
    main()
