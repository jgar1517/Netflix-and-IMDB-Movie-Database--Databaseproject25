import pandas as pd
import sqlite3
from pathlib import Path

# Define paths
DB_PATH = Path("netflix_db.db")
MERGED_PATH = Path("merged_netflix_imdb.csv")

# Check that both exist
if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found at {DB_PATH.resolve()}")
if not MERGED_PATH.exists():
    raise FileNotFoundError(f"Merged file not found at {MERGED_PATH.resolve()}")

print(f"✅ Database found: {DB_PATH.resolve()}")
print(f"✅ CSV found: {MERGED_PATH.resolve()}")

# Load the merged CSV
print("\n📥 Loading merged file...")
df = pd.read_csv(MERGED_PATH)
print(f"Loaded {len(df)} rows and {len(df.columns)} columns")

# Connect to the SQLite database
print("\n🔌 Connecting to database...")
conn = sqlite3.connect(DB_PATH)

# Write the DataFrame to a new table
TABLE_NAME = "Netflix_IMDB"
df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
print(f"\n✅ Imported into table '{TABLE_NAME}'")

# Verify row count
rows = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
print(f"📊 Row count in '{TABLE_NAME}': {rows}")

conn.close()
print("\n🎬 Done! Table now available in your SQLite DB.")