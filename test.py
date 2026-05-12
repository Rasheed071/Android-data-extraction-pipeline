import time
import sqlite3
from appium import webdriver
from appium.options.android import UiAutomator2Options
from xml.etree import ElementTree as ET

# =====================================================
# APPIUM SETUP
# =====================================================

options = UiAutomator2Options()

options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "Android"

driver = webdriver.Remote(
    "http://127.0.0.1:4723",
    options=options
)

print("✅ Connected")

# =====================================================
# SQLITE SETUP
# =====================================================

conn = sqlite3.connect("sap_contacts.db")
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL")

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    organization TEXT,
    profession TEXT,
    UNIQUE(name, organization, profession)
)
""")

conn.commit()

# =====================================================
# COUNTERS
# =====================================================

total_saved = 0
buffer_records = []

# =====================================================
# PARSER
# =====================================================

def parse_and_store(xml_data):

    global total_saved
    global buffer_records

    root = ET.fromstring(xml_data)

    titles = []
    subtitles = []

    for elem in root.iter():

        resource_id = elem.attrib.get("resource-id", "")
        text = elem.attrib.get("text", "").strip()

        if resource_id == "com.sap.events:id/title":
            titles.append(text)

        elif resource_id == "com.sap.events:id/subtitle":
            subtitles.append(text)

    for name, subtitle in zip(titles, subtitles):

        organization = ""
        profession = ""

        if " - " in subtitle:

            parts = subtitle.split(" - ", 1)

            organization = parts[0].strip()
            profession = parts[1].strip()

        else:

            organization = subtitle

        buffer_records.append(
            (name, organization, profession)
        )

    # BATCH INSERT
    if len(buffer_records) >= 100:

        cursor.executemany("""
        INSERT OR IGNORE INTO contacts
        (name, organization, profession)
        VALUES (?, ?, ?)
        """, buffer_records)

        conn.commit()

        total_saved += len(buffer_records)

        print(f"✅ Total Processed: {total_saved}")

        buffer_records.clear()

# =====================================================
# FAST AUTO SCROLL
# =====================================================

def auto_scroll():

    driver.swipe(
        start_x=500,
        start_y=1800,
        end_x=500,
        end_y=700,
        duration=250
    )

# =====================================================
# MAIN LOOP
# =====================================================

print("🚀 HIGH SPEED EXTRACTION STARTED")

same_screen_count = 0
last_signature = None

try:

    while True:

        xml_source = driver.page_source

        parse_and_store(xml_source)

        current_signature = hash(xml_source)

        if current_signature == last_signature:

            same_screen_count += 1

        else:

            same_screen_count = 0

        if same_screen_count >= 10:

            print("✅ END OF LIST DETECTED")
            break

        last_signature = current_signature

        auto_scroll()

        time.sleep(0.4)

except KeyboardInterrupt:

    print("🛑 STOPPED")

finally:

    # FINAL SAVE
    if buffer_records:

        cursor.executemany("""
        INSERT OR IGNORE INTO contacts
        (name, organization, profession)
        VALUES (?, ?, ?)
        """, buffer_records)

        conn.commit()

    conn.close()

    driver.quit()

    print("✅ FINISHED")