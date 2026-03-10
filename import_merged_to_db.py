import pandas as pd
import sqlite3
from pathlib import Path

# Paths
DB_PATH = Path("netflix_db.db")
MERGED_PATH = Path("merged_netflix_imdb.csv")

# Check that both files exist
if not DB_PATH.exists():
    print(f"❌ Database not found at {DB_PATH.resolve()}")
else:
    print(f"✅ Found database: {DB_PATH.resolve()}")

if not MERGED_PATH.exists():
    print(f"❌ Merged CSV not found at {MERGED_PATH.resolve()}")
else:
    print(f"✅ Found merged CSV: {MERGED_PATH.resolve()}")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Read CSV into pandas
df = pd.read_csv(MERGED_PATH)

# Write to database
table_name = "Netflix_IMDB"
df.to_sql(table_name, conn, if_exists="replace", index=False)

# Confirm import
print(f"\n✅ Imported {len(df)} rows into table '{table_name}' in {DB_PATH.name}")

# Preview first few rows
print(df.head(5))

conn.close()
print("\n🎬 Done!")