"""
Research data export — dumps all tables to CSV files in an `export/` directory.
Run from the project root:
    python export_data.py
or from the backend directory:
    python ../export_data.py
"""

import csv
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_CANDIDATES = [
    Path("backend/llms_with_llms.db"),
    Path("llms_with_llms.db"),
]

TABLES = [
    "students",
    "sessions",
    "dialogue_messages",
    "application_tasks",
    "quiz_results",
    "revisit_logs",
    "survey_responses",
    "layer_progress",
]


def find_db() -> Path:
    for p in DB_CANDIDATES:
        if p.exists():
            return p
    print("ERROR: database not found. Run from the project root.", file=sys.stderr)
    sys.exit(1)


def export(db_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    for table in TABLES:
        cur.execute(f"SELECT * FROM {table}")  # noqa: S608 — local research tool, no user input
        rows = cur.fetchall()
        if not rows:
            print(f"  {table}: 0 rows — skipped")
            continue

        out_file = out_dir / f"{table}.csv"
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows([dict(r) for r in rows])
        print(f"  {table}: {len(rows)} rows → {out_file}")

    conn.close()


def main() -> None:
    db_path = find_db()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("export") / timestamp
    print(f"Database : {db_path}")
    print(f"Output   : {out_dir}/")
    export(db_path, out_dir)
    print("Done.")


if __name__ == "__main__":
    main()
