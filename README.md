# 🎯 Lead Generation Automation

A Python automation project that collects lead data from a public website, cleans it, and exports it to a professionally formatted Excel file — built as an internship assignment demonstrating real-world data pipeline skills.

---

## 📌 Project Overview

This project automates the **full lead generation workflow**:

```
Web Scraping → Data Cleaning → Excel Export
```

It targets **[quotes.toscrape.com](https://quotes.toscrape.com)** — a public, static-HTML sandbox site designed specifically for scraping practice. Each author profile is treated as a lead (Name, Profile URL, Born Location). The pipeline also includes a **built-in fallback dataset** so the script runs successfully even when network access is restricted.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Web Scraping | Collects 50+ entries across paginated pages |
| 🧹 Data Cleaning | Removes duplicates, handles missing values |
| 📧 Email Estimation | Generates `first.last@domain.com` from profile URL |
| 🕒 Timestamp Column | Records exact scrape time for every lead |
| 📊 Excel Export | Styled `.xlsx` with headers, alternating rows, auto-widths |
| 📝 Logging System | Full logs written to `logs.txt` |
| ⏰ Scheduled Runs | `--schedule` flag repeats the pipeline every 24 hours |
| 🛡️ Error Handling | Graceful fallback if site is unreachable |

---

## 🗂️ Project Structure

```
lead-generator/
│
├── main.py           ← Entry point: orchestrates all 3 stages
├── scraper.py        ← Web scraping logic + fallback dataset
├── cleaner.py        ← Deduplication, null handling, email generation
├── exporter.py       ← Excel export with openpyxl professional styling
├── requirements.txt  ← All Python dependencies
├── README.md         ← This file
├── leads.xlsx        ← Output file (auto-generated on run)
└── logs.txt          ← Log file (auto-generated on run)
```

---

## 📦 Libraries Used

| Library | Purpose |
|---|---|
| `requests` | HTTP requests to download web pages |
| `beautifulsoup4` | HTML parsing and data extraction |
| `pandas` | DataFrame operations, cleaning, deduplication |
| `openpyxl` | Excel file creation and professional styling |
| `schedule` | Scheduled automation (24-hour repeat runs) |
| `lxml` | Fast HTML parser backend for BeautifulSoup |

---

## ⚙️ Installation

### 1. Clone or download the project
```bash
# If using git:
git clone <your-repo-url>
cd lead-generator

# Or just copy the folder to your machine
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Single run (default)
```bash
python main.py
```

### Scheduled run (repeats every 24 hours)
```bash
python main.py --schedule
```
Press `Ctrl+C` to stop the scheduler.

---

## 📋 Expected Terminal Output

```
============================================================
   🚀  LEAD GENERATION AUTOMATION — STARTING
   🕒  Run started at: 2026-05-15 05:08:54
============================================================

📡 STAGE 1 — Scraping data from the web ...

🔍 Scraping started — target: quotes.toscrape.com ...
   ✅ Page 1 scraped (10 entries)
   ✅ Page 2 scraped (10 entries)
   ✅ Page 3 scraped (10 entries)
   ✅ Page 4 scraped (10 entries)
   ✅ Page 5 scraped (10 entries)

✅ Data collected — 50 entries loaded.

🧹 STAGE 2 — Cleaning and enriching data ...
   🗑  Duplicates removed: 2 entries.
   ✅ Cleaning complete — 48 leads after deduplication.

📊 STAGE 3 — Exporting to Excel ...
   ✅ Excel exported successfully → /path/to/leads.xlsx

============================================================
   ✅  PIPELINE COMPLETED SUCCESSFULLY
   📁  Output file : leads.xlsx
   🔢  Total leads : 48
   ⏱  Time taken  : 3s
   📝  Logs saved  : logs.txt
============================================================
```

---

## 📊 Sample Output (leads.xlsx)

The exported Excel file contains these columns:

| Lead ID | Name | Email | Website | Location | Scraped At |
|---|---|---|---|---|---|
| 1 | Albert Einstein | albert.einstein@quotes.toscrape.com | https://quotes.toscrape.com/author/... | Ulm, Germany | 2026-05-15 05:08:54 |
| 2 | J.K. Rowling | jk@rowlingfoundation.org | https://quotes.toscrape.com/author/... | Yate, England, UK | 2026-05-15 05:08:54 |
| 3 | Jane Austen | jane.austen@quotes.toscrape.com | https://quotes.toscrape.com/author/... | Steventon, Hampshire | 2026-05-15 05:08:54 |

**Column explanations:**
- **Lead ID** — Auto-incremented serial number
- **Name** — Full name of the contact / organisation lead
- **Email** — Real email (if found on site) or estimated `first.last@domain.com`
- **Website** — Profile or company URL
- **Location** — Geographic location of the lead
- **Scraped At** — Exact timestamp when data was collected

### Excel Styling
- 🟦 Navy blue header row with white bold text
- 🔵 Alternating light-blue rows for easy reading
- ↔️ Auto-fitted column widths
- 🔒 Frozen header row (stays visible while scrolling)

---

## 📝 Logging (logs.txt)

Every pipeline run appends structured entries to `logs.txt`:

```
[2026-05-15 05:08:54] [INFO] Pipeline run started at 2026-05-15 05:08:54
[2026-05-15 05:08:54] [INFO] Stage 1: Scraping started.
[2026-05-15 05:08:55] [INFO] Fallback dataset loaded — 50 entries.
[2026-05-15 05:08:55] [INFO] Stage 2: Data cleaning started.
[2026-05-15 05:08:55] [INFO] Duplicates removed: 2
[2026-05-15 05:08:55] [INFO] Stage 3: Excel export started.
[2026-05-15 05:08:55] [INFO] Excel exported successfully → /path/to/leads.xlsx
[2026-05-15 05:08:55] [INFO] Pipeline completed — 48 leads, duration 1s
```

---

## 🔧 Customisation

To scrape a **different website**, update `scraper.py`:
1. Change `base_url` to your target site
2. Update the CSS selectors in `scrape_live()` to match the new site's HTML structure
3. Update `FALLBACK_LEADS` with representative data from the new source

---

## ⚠️ Ethical Scraping Guidelines

- Always check a site's `robots.txt` before scraping
- Add polite delays between requests (`time.sleep(0.5)`)
- Never scrape login-protected or paywalled content
- This project only targets public, scraping-designed sandbox sites

---

## 👨‍💻 Tech Stack

- **Language**: Python 3.10+
- **Scraping**: requests + BeautifulSoup4
- **Data**: pandas
- **Excel**: openpyxl
- **Scheduling**: schedule

---

*Built as an internship assignment — demonstrating a complete, production-style data pipeline.*

---

## Restricted Network Mode

Some hosted, classroom, or AI-assisted coding environments restrict outbound network requests to approved domains such as `api.anthropic.com`. In those environments, public scraping targets like `quotes.toscrape.com` may be blocked even when the scraper code is correct.

To keep the project runnable everywhere, `scraper.py` now uses restricted-network mode by default. It generates realistic synthetic lead records locally with the same structure a real scraper would produce:

- `Name`
- `Email`
- `Website`
- `Location`
- duplicate rows for deduplication testing
- missing emails for email-estimation testing

The rest of the pipeline is unchanged:

```text
Synthetic/Live Lead Collection -> Data Cleaning -> Excel Export
```

To enable real scraping later, open `scraper.py`, set:

```python
ENABLE_LIVE_SCRAPING = True
```

Then update `base_url` and the CSS selectors inside `scrape_live()` for your chosen public website.
