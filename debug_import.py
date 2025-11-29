import sys
import traceback

try:
    print("Importing app.main...")
    from app.main import app
    print("Import successful")
except Exception:
    print("Import failed")
    traceback.print_exc()
