#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

ID = "b2438451-0cb4-419b-978c-99fb4764748d"


def main(candidate_id: str):
    base = Path(__file__).resolve().parents[1]
    db_path = base / "dev.db"
    if not db_path.exists():
        print(json.dumps({"error": "dev.db not found", "path": str(db_path)}))
        return 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cur.fetchone()
    if not row:
        print(json.dumps({"found": False, "id": candidate_id}))
        return 0

    result = {k: row[k] for k in row.keys()}
    # Some JSON types (like lists stored as JSON) may be strings; attempt to parse
    for k, v in list(result.items()):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                result[k] = parsed
            except Exception:
                pass

    print(json.dumps({"found": True, "candidate": result}, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(ID))
