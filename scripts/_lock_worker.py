import json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from deli_autoresearch.state_store import StateStore
from deli_autoresearch.file_lock import ProcessFileLock, LockHeldError
ws, owner, hold = sys.argv[1], sys.argv[2], float(sys.argv[3])
store = StateStore(Path(ws))
try:
    lock = store.acquire_workspace_lock(owner)
    with lock:
        print(json.dumps({"status": "LOCK_ACQUIRED", "owner": owner}))
        time.sleep(hold)
except LockHeldError as e:
    print(json.dumps({"status": "LOCK_HELD", "existing_pid": e.existing_meta.get("pid")}))
except Exception as e:
    print(json.dumps({"status": "ERROR", "error": str(e)}))
sys.exit(0)
