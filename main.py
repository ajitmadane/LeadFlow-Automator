# ============================================================
# main.py — Entry point for the Lead Generation Automation script
#
# Orchestrates: Scraping → Cleaning → Exporting
# Bonus features included:
#   ✔ Logging system (logs.txt)
#   ✔ Timestamp column (added in cleaner.py)
#   ✔ Estimated email generation (added in cleaner.py)
#   ✔ Scheduled automation (runs once, then every 24 hours)
# ============================================================

import logging
import os
import sys
import schedule
import time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────
# Local module imports
# ─────────────────────────────────────────────
from scraper  import collect_leads
from cleaner  import clean_leads
from exporter import export_to_excel


# ─────────────────────────────────────────────
# Logging configuration
# Writes to both terminal (console) AND logs.txt file simultaneously
# ─────────────────────────────────────────────
def setup_logging(log_file: str = "logs.txt") -> None:
    """
    Configures the root 'LeadGenerator' logger with two handlers:
    1. FileHandler  → writes INFO+ messages to logs.txt
    2. StreamHandler → prints WARNING+ messages to terminal (keeps terminal clean)
    """
    logger = logging.getLogger("LeadGenerator")
    logger.setLevel(logging.DEBUG)        # Capture everything at logger level

    # File handler — detailed logs saved to disk
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler — only warnings and errors shown in terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("⚠️  %(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ─────────────────────────────────────────────
# Core pipeline — one complete run
# ─────────────────────────────────────────────
def run_pipeline() -> None:
    """
    Executes the full lead generation pipeline in three stages:
        Stage 1 → Scrape raw leads from the web
        Stage 2 → Clean, deduplicate, and enrich the data
        Stage 3 → Export the final DataFrame to leads.xlsx

    Logs each stage to logs.txt and prints status to terminal.
    """
    logger = logging.getLogger("LeadGenerator")
    run_start = datetime.now()

    print("=" * 60)
    print("   🚀  LEAD GENERATION AUTOMATION — STARTING")
    print(f"   🕒  Run started at: {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    logger.info("=" * 50)
    logger.info(f"Pipeline run started at {run_start.strftime('%Y-%m-%d %H:%M:%S')}")

    # ─────────────────────────────────────────
    # STAGE 1: Scraping
    # ─────────────────────────────────────────
    print("\n📡 STAGE 1 — Scraping data from the web ...")
    logger.info("Stage 1: Scraping started.")

    try:
        raw_leads = collect_leads()
        logger.info(f"Stage 1 complete — {len(raw_leads)} raw leads collected.")
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        print(f"❌ Scraping failed: {e}")
        return

    if not raw_leads:
        logger.warning("No leads collected. Aborting pipeline.")
        print("⚠️  No leads collected. Check your internet connection or the target site.")
        return

    # ─────────────────────────────────────────
    # STAGE 2: Cleaning
    # ─────────────────────────────────────────
    print("🧹 STAGE 2 — Cleaning and enriching data ...")
    logger.info("Stage 2: Data cleaning started.")

    try:
        clean_df = clean_leads(raw_leads)
        logger.info(f"Stage 2 complete — {len(clean_df)} clean leads ready.")
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        print(f"❌ Cleaning failed: {e}")
        return

    # ─────────────────────────────────────────
    # STAGE 3: Exporting
    # ─────────────────────────────────────────
    print("📊 STAGE 3 — Exporting to Excel ...")
    logger.info("Stage 3: Excel export started.")

    try:
        output_path = export_to_excel(clean_df, filepath="leads.xlsx")
        logger.info(f"Stage 3 complete — file saved to {output_path}")
    except Exception as e:
        logger.error(f"Stage 3 failed: {e}")
        print(f"❌ Export failed: {e}")
        return

    # ─────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────
    run_end   = datetime.now()
    duration  = (run_end - run_start).seconds

    print("=" * 60)
    print("   ✅  PIPELINE COMPLETED SUCCESSFULLY")
    print(f"   📁  Output file : {os.path.basename(output_path)}")
    print(f"   🔢  Total leads : {len(clean_df)}")
    print(f"   ⏱  Time taken  : {duration}s")
    print(f"   📝  Logs saved  : logs.txt")
    print("=" * 60)

    logger.info(
        f"Pipeline completed — {len(clean_df)} leads, "
        f"duration {duration}s, file: {output_path}"
    )
    logger.info("=" * 50)


# ─────────────────────────────────────────────
# Scheduled automation (BONUS FEATURE)
# ─────────────────────────────────────────────
def run_scheduled() -> None:
    """
    Runs the pipeline once immediately, then schedules it to
    repeat every 24 hours automatically.

    Use Ctrl+C to stop the scheduler.
    """
    print("\n⏰  Scheduled mode enabled.")
    print("    Pipeline will run once now, then every 24 hours.")
    print("    Press Ctrl+C to stop the scheduler.\n")

    # Run once immediately before waiting for the schedule
    run_pipeline()

    # Schedule subsequent runs every 24 hours
    schedule.every(24).hours.do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)   # Check every minute if a job is due


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Set up logging before anything else
    setup_logging(log_file="logs.txt")

    # Check for --schedule flag to enable recurring runs
    if "--schedule" in sys.argv:
        run_scheduled()
    else:
        # Default: single run
        run_pipeline()
