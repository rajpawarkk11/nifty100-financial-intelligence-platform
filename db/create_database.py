import sqlite3
from pathlib import Path

DB_FILE = Path("db/nifty100.db")
SCHEMA_FILE = Path("db/schema.sql")

conn = sqlite3.connect(DB_FILE)

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema = f.read()

conn.executescript(schema)

conn.commit()
conn.close()

print("Database created successfully")
print(DB_FILE)