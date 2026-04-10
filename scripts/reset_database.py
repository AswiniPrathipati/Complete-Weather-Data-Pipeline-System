#!/usr/bin/env python3
# scripts/reset_database.py — Reset DB to clean state
# =====================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.logging_config  # noqa
from config.config import DB_PATH
from src.database import setup_database

def reset():
    confirm = input(f"⚠️  This will DELETE all data in '{DB_PATH}'. Type YES to confirm: ")
    if confirm.strip().upper() != 'YES':
        print("Cancelled.")
        return
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Deleted: {DB_PATH}")
    setup_database()
    print("✅ Database reset and re-initialised.")

if __name__ == "__main__":
    reset()
