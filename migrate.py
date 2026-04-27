"""
migrate.py — one-time script to upload knowledge_index.json to Supabase.
Run once from your project folder:
    python migrate.py
"""

import json
import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
INDEX_PATH   = "knowledge_index.json"

def migrate():
    print("Starting migration...")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY are not set.")
        print(f"  SUPABASE_URL = '{SUPABASE_URL}'")
        print(f"  SUPABASE_KEY = '{SUPABASE_KEY[:10]}...' " if SUPABASE_KEY else "  SUPABASE_KEY = ''")
        return

    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Supabase Key: {SUPABASE_KEY[:10]}...")

    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: {INDEX_PATH} not found in current directory: {os.getcwd()}")
        return

    with open(INDEX_PATH, "r") as f:
        entries = json.load(f)

    print(f"Found {len(entries)} entries in {INDEX_PATH}")

    if not entries:
        print("No entries to migrate.")
        return

    print("Connecting to Supabase...")
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected.")

    success = 0
    skipped = 0
    failed  = 0

    for entry in entries:
        try:
            if isinstance(entry.get("tags"), str):
                entry["tags"] = json.loads(entry["tags"])
            if isinstance(entry.get("key_concepts"), str):
                entry["key_concepts"] = json.loads(entry["key_concepts"])

            if "domain" in entry and not entry.get("category"):
                entry["category"] = entry.pop("domain")
            elif "domain" in entry:
                entry.pop("domain")

            sb.table("knowledge_index").upsert(entry).execute()
            success += 1
            print(f"  ✓ {entry.get('title', entry['id'])[:60]}")

        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                skipped += 1
                print(f"  — skipped (already exists): {entry.get('title', entry['id'])[:60]}")
            else:
                failed += 1
                print(f"  ✗ FAILED: {entry.get('title', entry['id'])[:60]}")
                print(f"    Error: {e}")

    print(f"\nDone. {success} migrated, {skipped} skipped, {failed} failed.")

if __name__ == "__main__":
    migrate()