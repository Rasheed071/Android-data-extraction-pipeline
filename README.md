# Android Mobile Data Extraction Pipeline

Automated pipeline for extracting attendee/contact data from Android mobile applications using Appium UI automation, with storage in SQLite and export to Excel.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Folder Structure](#4-folder-structure)
5. [Prerequisites](#5-prerequisites)
6. [Step-by-Step Setup](#6-step-by-step-setup)
   - [Step 1 — Install Node.js](#step-1--install-nodejs)
   - [Step 2 — Install Appium](#step-2--install-appium)
   - [Step 3 — Install Android Studio & SDK](#step-3--install-android-studio--sdk)
   - [Step 4 — Set Environment Variables](#step-4--set-environment-variables)
   - [Step 5 — Verify ADB](#step-5--verify-adb)
   - [Step 6 — Install Appium UiAutomator2 Driver](#step-6--install-appium-uiautomator2-driver)
   - [Step 7 — Prepare Android Device](#step-7--prepare-android-device)
   - [Step 8 — Install Python Dependencies](#step-8--install-python-dependencies)
7. [Running the Pipeline](#7-running-the-pipeline)
8. [How the Scripts Work](#8-how-the-scripts-work)
9. [Adapting to a Different Android App](#9-adapting-to-a-different-android-app)
10. [Performance Optimizations](#10-performance-optimizations)
11. [Troubleshooting](#11-troubleshooting)
12. [Example Output](#12-example-output)

---

## 1. Project Overview

This project was built to extract attendee/contact information from the **SAP Events** Android mobile application using automated UI scraping.

**Fields extracted:**
- Name
- Organization
- Profession / Designation

**Example record:**
```json
{
  "Name": "Suli Abas",
  "Organization": "NSIGHT, INC.",
  "Profession": "Business Development Manager"
}
```

---

## 2. Architecture

```
Android Mobile App
        ↓
  Appium Server
        ↓
ADB (Android Debug Bridge)
        ↓
 Python Automation Script
        ↓
 XML Hierarchy Extraction
        ↓
   PII Parsing Logic
        ↓
  SQLite Database Storage
        ↓
     Excel Export
```

---

## 3. Technology Stack

| Technology              | Purpose                              |
|-------------------------|--------------------------------------|
| Appium                  | Mobile UI automation framework       |
| ADB (Android Debug Bridge) | Communication between PC and Android device |
| Android Studio          | Provides the Android SDK             |
| Python 3.x              | Automation scripting                 |
| SQLite                  | Lightweight local database           |
| Pandas                  | Data processing and Excel export     |
| openpyxl                | Excel file writing backend           |
| XML / ElementTree       | Android UI hierarchy parsing         |

---

## 4. Folder Structure

```
data_scrap/
├── test.py                    # Main extraction script
├── export_to_excel.py         # Exports SQLite data to Excel
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This guide
│
│   (generated at runtime — not committed to git)
├── sap_contacts.db            # SQLite database
├── sap_contacts_export.xlsx   # Final Excel output
└── live_page_source.xml       # Android XML dump (debug artifact)
```

---

## 5. Prerequisites

Make sure the following are installed before starting:

| Requirement         | Version Tested | Download Link |
|---------------------|---------------|---------------|
| Node.js             | v18+          | https://nodejs.org |
| npm                 | v9+           | (bundled with Node.js) |
| Appium              | 3.4.2         | via npm |
| Android Studio      | Latest        | https://developer.android.com/studio |
| Python              | 3.9+          | https://python.org |
| pip                 | Latest        | (bundled with Python) |
| USB Drivers         | Device-specific | From device manufacturer |

---

## 6. Step-by-Step Setup

### Step 1 — Install Node.js

Download and install Node.js from https://nodejs.org (LTS version recommended).

Verify:
```powershell
node -v
npm -v
```

---

### Step 2 — Install Appium

Install Appium globally via npm:
```powershell
npm i --location=global appium
```

Verify installation:
```powershell
appium -v
```
Expected output:
```
3.4.2
```

---

### Step 3 — Install Android Studio & SDK

1. Download Android Studio from https://developer.android.com/studio
2. During setup, install:
   - **Android SDK**
   - **Android SDK Platform-Tools**
   - **Android Emulator** (optional, only needed if using a virtual device)
3. Note your SDK path — default location:
   ```
   C:\Users\<YourUsername>\AppData\Local\Android\Sdk
   ```

---

### Step 4 — Set Environment Variables

**Option A — Permanent (recommended for regular use)**

Open **System Properties → Environment Variables** and add/update:

| Variable           | Value                                                    |
|--------------------|----------------------------------------------------------|
| `ANDROID_HOME`     | `C:\Users\<YourUsername>\AppData\Local\Android\Sdk`      |
| `ANDROID_SDK_ROOT` | `C:\Users\<YourUsername>\AppData\Local\Android\Sdk`      |

Then add these to the **Path** variable:
```
C:\Users\<YourUsername>\AppData\Local\Android\Sdk\platform-tools
C:\Users\<YourUsername>\AppData\Local\Android\Sdk\emulator
```

**Option B — Temporary (current PowerShell session only)**

```powershell
$env:ANDROID_HOME     = "C:\Users\Rasheed\AppData\Local\Android\Sdk"
$env:ANDROID_SDK_ROOT = "C:\Users\Rasheed\AppData\Local\Android\Sdk"
$env:Path            += ";C:\Users\Rasheed\AppData\Local\Android\Sdk\platform-tools"
$env:Path            += ";C:\Users\Rasheed\AppData\Local\Android\Sdk\emulator"
```

> **Note:** Replace `Rasheed` with your actual Windows username throughout this guide.

---

### Step 5 — Verify ADB

Check ADB is working:
```powershell
adb version
```
Expected output:
```
Android Debug Bridge version 1.0.41
```

Connect your Android device via USB, then verify it is detected:
```powershell
adb devices
```
Expected output:
```
List of devices attached
R5CT824QT2E    device
```

> If you see `unauthorized` instead of `device`, unlock your Android phone and tap **Allow** on the USB debugging popup.

---

### Step 6 — Install Appium UiAutomator2 Driver

```powershell
appium driver install uiautomator2
```

Verify the driver is installed:
```powershell
appium driver list --installed
```
Expected output:
```
✔ uiautomator2
```

---

### Step 7 — Prepare Android Device

On your Android device:

1. Enable **Developer Options**:
   - Go to **Settings → About Phone**
   - Tap **Build Number** 7 times until Developer Options unlocks

2. Inside **Developer Options**, enable:
   - **USB Debugging**
   - **Stay Awake** (prevents screen off during scraping)

3. For faster rendering (speeds up scraping), set all animation scales to **Off**:
   - **Window animation scale → Animation off**
   - **Transition animation scale → Animation off**
   - **Animator duration scale → Animation off**

4. Connect the device to your PC via USB and approve the **Allow USB Debugging** popup.

---

### Step 8 — Install Python Dependencies

From the project folder, run:
```powershell
pip install -r requirements.txt
```

Or install individually:
```powershell
pip install Appium-Python-Client pandas openpyxl
```

---

## 7. Running the Pipeline

**You need two terminal windows.**

### Terminal 1 — Start Appium Server

```powershell
appium
```

Wait until you see:
```
Appium REST http interface listener started on http://0.0.0.0:4723
```

Keep this terminal running throughout the session.

---

### Terminal 2 — Run the Extraction Script

Make sure the target Android app is **open and on the attendee/contact list screen**, then run:

```powershell
cd C:\Users\Rasheed\Desktop\data_scrap
python test.py
```

The script will:
- Connect to the Appium server
- Capture Android screen XML
- Parse contact records
- Auto-scroll through the list
- Save records to `sap_contacts.db`
- Stop automatically when the end of the list is detected

---

### Terminal 2 — Export to Excel

After extraction is complete:

```powershell
python export_to_excel.py
```

This will generate `sap_contacts_export.xlsx` in the project folder.

---

## 8. How the Scripts Work

### `test.py` — Main Extraction Script

| Phase | What it does |
|-------|-------------|
| **Connect** | Connects Python → Appium Server → Android Device |
| **Setup DB** | Creates SQLite `contacts` table with WAL mode |
| **XML Capture** | Calls `driver.page_source` to get full Android UI XML |
| **Parse** | Iterates XML elements, matches `resource-id` for title/subtitle |
| **Split** | Splits `"NSIGHT, INC. - Business Development Manager"` into org + profession |
| **Buffer** | Accumulates 100 records in memory before batch insert |
| **Batch Insert** | `INSERT OR IGNORE` prevents duplicate records |
| **Scroll** | Calls `driver.swipe()` to scroll the list |
| **Loop** | Repeats until 10 consecutive identical screens detected (end of list) |
| **Cleanup** | Flushes remaining buffer, closes DB and driver |

### `export_to_excel.py` — Excel Exporter

| Phase | What it does |
|-------|-------------|
| **Connect DB** | Opens `sap_contacts.db` |
| **Fetch** | `SELECT * FROM contacts` into a Pandas DataFrame |
| **Clean** | Removes duplicates, empty names, strips whitespace |
| **Export** | Saves to `sap_contacts_export.xlsx` |

---

## 9. Adapting to a Different Android App

To scrape a different Android app, follow these steps:

### Step A — Find the correct `resource-id` values

1. Start Appium and connect your device.
2. Open the target app on the device and navigate to the list/screen you want to scrape.
3. Use **Appium Inspector** (download from https://github.com/appium/appium-inspector) to inspect UI elements.
4. Tap on the element containing the name or data you want — note the `resource-id` shown in the inspector panel.

### Step B — Update `test.py`

Replace the resource IDs in the parsing section:

```python
# Change these to match your target app
if resource_id == "com.sap.events:id/title":       # → name/title field
    titles.append(text)

elif resource_id == "com.sap.events:id/subtitle":  # → subtitle/detail field
    subtitles.append(text)
```

### Step C — Update the split logic (if needed)

If the subtitle format is different, update the split:

```python
# Current: "NSIGHT, INC. - Business Development Manager"
parts = subtitle.split(" - ", 1)

# Change the delimiter to match your app's format
# e.g., parts = subtitle.split("|", 1)
# e.g., parts = subtitle.split(",", 1)
```

### Step D — Update the SQLite table (if extracting different fields)

If you need different columns, update the `CREATE TABLE` and `INSERT` statements in `test.py` to match.

### Step E — Adjust scroll coordinates

The default swipe coordinates assume a 1080×2400 screen:
```python
driver.swipe(
    start_x=500,
    start_y=1800,   # start near bottom of screen
    end_x=500,
    end_y=700,      # end near top of screen
    duration=250
)
```
Adjust `start_y` and `end_y` based on your device's screen resolution.

---

## 10. Performance Optimizations

| Optimization | Setting | Impact |
|-------------|---------|--------|
| Batch SQLite inserts | Every 100 records | Huge speed gain vs. 1-by-1 inserts |
| WAL journal mode | `PRAGMA journal_mode=WAL` | Faster concurrent writes |
| Fast swipe | `duration=250ms` | More screens per minute |
| Low sleep delay | `time.sleep(0.4)` | Higher throughput |
| Animation off | Android Developer Options | Faster screen transitions |
| Stay Awake | Android Developer Options | No interruptions during long runs |
| `INSERT OR IGNORE` | SQLite constraint | Deduplication at DB level |

---

## 11. Troubleshooting

### `Connection refused at 127.0.0.1:4723`
**Cause:** Appium server is not running.  
**Fix:** Start Appium in a separate terminal:
```powershell
appium
```

---

### `ANDROID_HOME not set` or `adb not recognized`
**Cause:** Environment variables are not configured.  
**Fix:** Set them in your session (see [Step 4](#step-4--set-environment-variables)) or permanently via System Properties.

---

### `adb devices` shows `unauthorized`
**Cause:** USB debugging not approved on the device.  
**Fix:** Unlock your Android phone and tap **Allow** on the USB debugging popup. If the popup doesn't appear, revoke and re-grant USB debugging permissions in Developer Options.

---

### `No device found` / `Could not find a connected Android device`
**Cause:** Device not detected by ADB.  
**Fix:**
1. Try a different USB cable (data cable, not charge-only).
2. Try a different USB port.
3. Install your device's official USB drivers.
4. Run `adb kill-server` then `adb start-server`.

---

### Script runs but no records are saved
**Cause:** The `resource-id` values don't match the app's current version.  
**Fix:** Use Appium Inspector to re-inspect the elements and update the IDs in `test.py`.

---

### Script never stops (end of list not detected)
**Cause:** The list has dynamic loading or the screen hash keeps changing.  
**Fix:** Increase the threshold or add a max iteration count:
```python
MAX_ITERATIONS = 500  # safety cap
iteration = 0

while iteration < MAX_ITERATIONS:
    ...
    iteration += 1
```

---

### `ModuleNotFoundError: No module named 'appium'`
**Fix:**
```powershell
pip install Appium-Python-Client
```

---

## 12. Example Output

### SQLite — `sap_contacts.db`

| id | name | organization | profession |
|----|------|-------------|-----------|
| 1  | Suli Abas | NSIGHT, INC. | Business Development Manager |
| 2  | Jane Doe | Acme Corp | Software Engineer |

### Excel — `sap_contacts_export.xlsx`

Same columns exported into a formatted Excel file, with duplicates removed and whitespace trimmed.

---

## Quick Reference — Full Command Sequence

```powershell
# Terminal 1 — Start Appium
appium

# Terminal 2 — Set env vars (if not set permanently)
$env:ANDROID_HOME     = "C:\Users\Rasheed\AppData\Local\Android\Sdk"
$env:ANDROID_SDK_ROOT = "C:\Users\Rasheed\AppData\Local\Android\Sdk"
$env:Path            += ";C:\Users\Rasheed\AppData\Local\Android\Sdk\platform-tools"

# Verify device
adb devices

# Run extraction (open the app on the list screen first)
python test.py

# Export to Excel
python export_to_excel.py
```

---

## Architecture — Scale-Up Potential

This pipeline can be extended into:

| Future Use Case | Description |
|----------------|-------------|
| Mobile RPA | Automate multi-step workflows inside apps |
| AI-powered extraction | Use LLMs to parse unstructured screen text |
| Lead harvesting | Extract leads from event/directory apps |
| CRM automation | Push extracted data directly to CRM APIs |
| Event scraping | Batch-extract from multiple event apps |
| Mobile workflow automation | End-to-end mobile process automation |
| AI agent systems | Plug into multi-agent pipelines |
