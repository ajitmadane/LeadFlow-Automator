# ============================================================
# cleaner.py — Cleans raw lead data and generates email estimates
# ============================================================

import pandas as pd
import logging
import re
from datetime import datetime

logger = logging.getLogger("LeadGenerator")


# ─────────────────────────────────────────────
# Email format templates used for estimation
# Mirrors common corporate email patterns
# ─────────────────────────────────────────────
EMAIL_TEMPLATES = [
    "{first}.{last}@{domain}",
    "{first}@{domain}",
    "{first}{last}@{domain}",
    "info@{domain}",
]


def extract_domain_from_url(url: str) -> str | None:
    """
    Pulls the bare domain name from a full URL.
    Example: 'https://quotes.toscrape.com/author/albert-einstein/' → 'quotes.toscrape.com'
    Returns None if URL is empty or malformed.
    """
    if not url or pd.isna(url):
        return None
    # Strip protocol and path, keep only the domain part
    domain = re.sub(r"https?://", "", str(url))
    domain = domain.split("/")[0]   # Remove path
    return domain if domain else None


def generate_email_estimate(name: str, domain: str) -> str:
    """
    Generates the most common email format: firstname.lastname@domain
    Falls back to info@domain if the name can't be parsed cleanly.

    Example: "Albert Einstein" + "toscrape.com" → "albert.einstein@toscrape.com"
    """
    if not name or not domain:
        return "Not Available"

    # Split name into parts and sanitize
    parts = str(name).strip().lower().split()
    parts = [re.sub(r"[^a-z]", "", p) for p in parts]   # Remove non-alpha chars
    parts = [p for p in parts if p]                       # Drop empty strings

    if len(parts) >= 2:
        first, last = parts[0], parts[-1]
        return EMAIL_TEMPLATES[0].format(first=first, last=last, domain=domain)
    elif len(parts) == 1:
        return EMAIL_TEMPLATES[1].format(first=parts[0], domain=domain)
    else:
        return EMAIL_TEMPLATES[3].format(domain=domain)   # Fallback: info@domain


def clean_leads(raw_leads: list[dict]) -> pd.DataFrame:
    """
    Master cleaning function:
    1. Converts raw list → DataFrame
    2. Removes rows with missing names
    3. Drops exact duplicates
    4. Fills missing emails (real or estimated)
    5. Adds timestamp column
    6. Resets index cleanly

    Returns a clean pandas DataFrame ready for export.
    """
    logger.info("Starting data cleaning pipeline ...")

    # ── Step 1: Load raw data into DataFrame ──────────────────
    df = pd.DataFrame(raw_leads)
    logger.info(f"Raw records loaded: {len(df)}")

    # ── Step 2: Strip whitespace from all string columns ──────
    str_cols = ["Name", "Email", "Website", "Location"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Convert "None" strings (from str cast) back to actual NaN
            df[col] = df[col].replace({"None": pd.NA, "nan": pd.NA, "": pd.NA})

    # ── Step 3: Remove rows where Name is missing ─────────────
    before = len(df)
    df.dropna(subset=["Name"], inplace=True)
    dropped_nameless = before - len(df)
    if dropped_nameless:
        logger.info(f"Removed {dropped_nameless} rows with missing names.")
        print(f"   🗑  Removed {dropped_nameless} rows with no name.")

    # ── Step 4: Remove duplicate entries ──────────────────────
    before = len(df)
    df.drop_duplicates(subset=["Name"], keep="first", inplace=True)
    dropped_dupes = before - len(df)
    logger.info(f"Duplicates removed: {dropped_dupes}")
    print(f"   🗑  Duplicates removed: {dropped_dupes} entries.")

    # ── Step 5: Handle missing emails ─────────────────────────
    # If email exists, keep it. If missing but website exists, generate estimate.
    # Otherwise, mark as "Not Available".
    def resolve_email(row):
        if pd.notna(row.get("Email")):
            return str(row["Email"])

        website = row.get("Website")
        domain = extract_domain_from_url(website)

        if domain:
            estimated = generate_email_estimate(row.get("Name"), domain)
            logger.debug(f"Estimated email for {row['Name']}: {estimated}")
            return estimated

        return "Not Available"

    df["Email"] = df.apply(resolve_email, axis=1)

    # ── Step 6: Fill remaining missing values ─────────────────
    df["Website"] = df["Website"].fillna("Not Available")
    df["Location"] = df["Location"].fillna("Not Available")

    # ── Step 7: Add timestamp column ──────────────────────────
    df["Scraped At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Step 8: Add a serial Lead ID column ───────────────────
    df.reset_index(drop=True, inplace=True)
    df.insert(0, "Lead ID", range(1, len(df) + 1))

    # ── Step 9: Reorder columns for clean export ───────────────
    column_order = ["Lead ID", "Name", "Email", "Website", "Location", "Scraped At"]
    df = df[[c for c in column_order if c in df.columns]]

    logger.info(f"Cleaning complete — {len(df)} clean leads ready.")
    print(f"   ✅ Cleaning complete — {len(df)} leads after deduplication.\n")
    return df
