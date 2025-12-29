import sys
import time

print("Starting import test...")
sys.path.insert(0, ".")

start = time.time()
try:
    from api.main import app
    print(f"Imported app in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Import failed: {e}")
