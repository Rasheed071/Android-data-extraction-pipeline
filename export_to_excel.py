import sqlite3
import pandas as pd

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_FILE = "sap_contacts.db"

OUTPUT_EXCEL = "sap_contacts_export.xlsx"

# ==========================================
# CONNECT TO SQLITE DATABASE
# ==========================================

try:

    conn = sqlite3.connect(DB_FILE)

    print("✅ Connected to SQLite Database")

except Exception as e:

    print("❌ Database Connection Failed")
    print(e)

    exit()

# ==========================================
# FETCH DATA
# ==========================================

try:

    query = """
    SELECT *
    FROM contacts
    """

    df = pd.read_sql_query(query, conn)

    print(f"✅ Total Records Fetched: {len(df)}")

except Exception as e:

    print("❌ Error Fetching Data")
    print(e)

    conn.close()

    exit()

# ==========================================
# OPTIONAL DATA CLEANING
# ==========================================

# Remove duplicates if any
df.drop_duplicates(inplace=True)

# Remove empty names
df = df[df["name"].notna()]

# Strip spaces
df["name"] = df["name"].astype(str).str.strip()
df["organization"] = df["organization"].astype(str).str.strip()
df["profession"] = df["profession"].astype(str).str.strip()

# ==========================================
# EXPORT TO EXCEL
# ==========================================

try:

    df.to_excel(
        OUTPUT_EXCEL,
        index=False
    )

    print("\n✅ EXCEL EXPORT SUCCESSFUL")
    print(f"📄 File: {OUTPUT_EXCEL}")

except Exception as e:

    print("❌ Excel Export Failed")
    print(e)

# ==========================================
# CLOSE CONNECTION
# ==========================================

conn.close()

print("\n✅ Database Connection Closed")