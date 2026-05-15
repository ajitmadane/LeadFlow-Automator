# ============================================================
# scraper.py - Lead collection layer
#
# Network policy note:
# Some execution environments only allow outbound requests to approved
# domains such as api.anthropic.com. Public scraping targets like
# quotes.toscrape.com can be blocked there, so this module uses a
# restricted-network mode by default and generates realistic synthetic
# lead data with the same shape a real scraper would return.
#
# To use live scraping later, set ENABLE_LIVE_SCRAPING = True and update
# base_url / CSS selectors in scrape_live() for your target website.
# ============================================================

import logging
import random
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("LeadGenerator")

# Kept visible because some hosted/sandboxed environments only allow
# traffic to approved API domains. This project does not call this API;
# the constant documents why local synthetic generation is the default.
ALLOWED_NETWORK_DOMAIN = "https://api.anthropic.com"
ENABLE_LIVE_SCRAPING = False

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


SYNTHETIC_COMPANIES = [
    ("Aarav Mehta", "Product Manager", "BluePeak Analytics", "bluepeakanalytics.com", "Bengaluru, India"),
    ("Priya Sharma", "Founder", "GreenGrid Energy", "greengridenergy.io", "Pune, India"),
    ("Rohan Iyer", "Operations Head", "NovaCart Retail", "novacartretail.com", "Mumbai, India"),
    ("Neha Kapoor", "Marketing Director", "CloudNest CRM", "cloudnestcrm.com", "Delhi, India"),
    ("Karan Malhotra", "Sales Lead", "FinRise Advisors", "finriseadvisors.com", "Gurugram, India"),
    ("Ananya Rao", "HR Manager", "SkillBridge Labs", "skillbridgelabs.com", "Hyderabad, India"),
    ("Vikram Sinha", "Business Development Manager", "MedAxis Care", "medaxiscare.in", "Chennai, India"),
    ("Meera Nair", "Partnerships Lead", "EduSpark Learning", "edusparklearning.com", "Kochi, India"),
    ("Siddharth Jain", "Procurement Manager", "UrbanBuild Supply", "urbanbuildsupply.com", "Jaipur, India"),
    ("Isha Verma", "Customer Success Manager", "DataHarbor Systems", "dataharborsystems.com", "Noida, India"),
    ("Arjun Reddy", "Technology Consultant", "SecureByte Solutions", "securebytesolutions.com", "Hyderabad, India"),
    ("Tanvi Desai", "Growth Manager", "BrightPath Media", "brightpathmedia.co", "Ahmedabad, India"),
    ("Kabir Khan", "Regional Manager", "SwiftFleet Logistics", "swiftfleetlogistics.com", "Lucknow, India"),
    ("Ritika Bose", "Finance Controller", "NorthStar Capital", "northstarcapital.in", "Kolkata, India"),
    ("Manav Gupta", "Director", "AgroPulse Foods", "agropulsefoods.com", "Indore, India"),
    ("Aisha Thomas", "Program Lead", "CareCircle Foundation", "carecirclefoundation.org", "Thiruvananthapuram, India"),
    ("Dev Patel", "IT Manager", "ZenWorks Automation", "zenworksautomation.com", "Surat, India"),
    ("Nisha Menon", "Brand Manager", "FreshLeaf Organics", "freshleaforganics.in", "Coimbatore, India"),
    ("Aditya Chawla", "Founder", "HireLoop Talent", "hirelooptalent.com", "Chandigarh, India"),
    ("Sara D'Souza", "Community Manager", "OpenAid Network", "openaidnetwork.org", "Goa, India"),
    ("Rahul Bansal", "Enterprise Sales Manager", "MetricWorks SaaS", "metricworkssaas.com", "Bhopal, India"),
    ("Pooja Kulkarni", "Supply Chain Lead", "PrimeSource Traders", "primesourcetraders.com", "Nagpur, India"),
    ("Mohit Arora", "Strategy Manager", "Elevate Consulting", "elevateconsulting.co", "Delhi, India"),
    ("Sneha Pillai", "Admissions Head", "FutureMinds Academy", "futuremindsacademy.edu", "Mysuru, India"),
    ("Yash Agarwal", "Channel Partner Lead", "SolarMint Power", "solarmintpower.com", "Vadodara, India"),
    ("Aditi Saxena", "Communications Manager", "ImpactBridge NGO", "impactbridgengo.org", "Patna, India"),
    ("Nikhil Joshi", "CTO", "CodeCraft Studios", "codecraftstudios.dev", "Bengaluru, India"),
    ("Farah Ali", "Retail Expansion Lead", "StyleStreet Apparel", "stylestreetapparel.com", "Mumbai, India"),
    ("Omkar Patil", "Plant Manager", "PrecisionForge Metals", "precisionforge.co", "Nashik, India"),
    ("Simran Kaur", "Client Success Lead", "LegalEase Services", "legaleaseservices.in", "Amritsar, India"),
    ("Harsh Vardhan", "General Manager", "TravelMint Holidays", "travelmintholidays.com", "Udaipur, India"),
    ("Lavanya Krishnan", "Research Coordinator", "BioQuest Labs", "bioquestlabs.com", "Chennai, India"),
    ("Raghav Bhatia", "Franchise Manager", "CafeOrbit Foods", "cafeorbitfoods.com", "Gurugram, India"),
    ("Maya Fernandes", "CSR Lead", "HopeHarbor Trust", "hopeharbortrust.org", "Mangalore, India"),
    ("Tushar Mehta", "Account Executive", "PayWise Fintech", "paywisefintech.com", "Pune, India"),
    ("Kavya Ramesh", "Training Manager", "LearnSphere Pro", "learnspherepro.com", "Bengaluru, India"),
    ("Sameer Qureshi", "Logistics Coordinator", "RouteMax Express", "routemaxexpress.com", "Hyderabad, India"),
    ("Bhavna Shah", "Merchandising Lead", "CraftHive Marketplace", "crafthivemarket.com", "Ahmedabad, India"),
    ("Neil Dutta", "Analytics Lead", "InsightLake AI", "insightlakeai.com", "Kolkata, India"),
    ("Diya Narang", "Public Relations Manager", "CityCare Hospitals", "citycarehospitals.in", "Delhi, India"),
    ("Varun Prakash", "Real Estate Consultant", "HomeVista Realty", "homevistarealty.com", "Noida, India"),
    ("Shreya Ghosh", "Event Partnerships Lead", "StageLine Events", "stagelineevents.com", "Kolkata, India"),
    ("Aman Sheikh", "Security Manager", "VaultEdge Systems", "vaultedgesystems.com", "Bhopal, India"),
    ("Riya Chatterjee", "Donor Relations Lead", "BrightFuture Trust", "brightfuturetrust.org", "Ranchi, India"),
    ("Gaurav Mishra", "Purchase Officer", "BuildCore Materials", "buildcorematerials.com", "Kanpur, India"),
    ("Malini Rao", "Principal Consultant", "PeopleFirst HR", "peoplefirsthr.co", "Hyderabad, India"),
    ("Zoya Khan", "Digital Marketing Lead", "MarketMosaic", "marketmosaic.in", "Lucknow, India"),
    ("Akash Jain", "Founder", "QuickDesk Support", "quickdesksupport.com", "Jaipur, India"),
    ("Reema Sen", "Program Director", "WaterWise Initiative", "waterwiseinitiative.org", "Bhubaneswar, India"),
    ("Pranav Nambiar", "Solutions Architect", "StackBridge Cloud", "stackbridgecloud.com", "Kochi, India"),
]


def make_email(name: str, domain: str, index: int) -> str | None:
    """Return a mix of real-looking and missing emails for cleaning demos."""
    if index % 4 == 0:
        return None

    cleaned_parts = ["".join(ch for ch in part.lower() if ch.isalpha()) for part in name.split()]
    cleaned_parts = [part for part in cleaned_parts if part]

    if len(cleaned_parts) >= 2:
        return f"{cleaned_parts[0]}.{cleaned_parts[-1]}@{domain}"
    if cleaned_parts:
        return f"{cleaned_parts[0]}@{domain}"
    return f"info@{domain}"


def generate_synthetic_leads(total: int = 50) -> list[dict]:
    """
    Creates realistic lead data locally.

    This mirrors a real scraping result: names, role/company page URLs,
    company domains, locations, occasional missing emails, and duplicates
    for the cleaner to remove.
    """
    leads = []

    for index, (name, title, company, domain, location) in enumerate(SYNTHETIC_COMPANIES[:total], start=1):
        slug = "-".join(name.lower().replace("'", "").split())
        website = f"https://{domain}/team/{slug}"
        email = make_email(name, domain, index)

        leads.append(
            {
                "Name": name,
                "Email": email,
                "Website": website,
                "Location": location,
                "Source": "Synthetic restricted-network dataset",
                "Company": company,
                "Title": title,
            }
        )

    # Intentional duplicates demonstrate the cleaning stage.
    if len(leads) >= 20:
        leads.insert(8, dict(leads[1]))
        leads.insert(21, dict(leads[14]))

    return leads


def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Downloads a webpage and returns a BeautifulSoup object.
    Returns None on any network / HTTP error.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        logger.info(f"Fetched: {url}")
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as exc:
        logger.warning(f"Could not fetch {url} - {exc}")
        return None


def scrape_live() -> list[dict]:
    """
    Optional live scraper for a public static HTML site.
    Disabled by default because restricted environments block most domains.
    """
    base_url = "https://quotes.toscrape.com"
    leads = []
    page_num = 1

    logger.info("Attempting live scrape on quotes.toscrape.com ...")

    while True:
        page_url = f"{base_url}/page/{page_num}/"
        soup = fetch_page(page_url)

        if soup is None:
            break

        quote_blocks = soup.find_all("div", class_="quote")
        if not quote_blocks:
            break

        for block in quote_blocks:
            author_tag = block.find("small", class_="author")
            name = author_tag.get_text(strip=True) if author_tag else None
            link_tag = block.find("a", href=True)
            profile_path = link_tag["href"] if link_tag else ""
            website = urljoin(base_url, profile_path) if profile_path else None
            tags = block.find_all("a", class_="tag")
            location = ", ".join(t.get_text(strip=True) for t in tags) if tags else None

            leads.append({"Name": name, "Email": None, "Website": website, "Location": location})

        logger.info(f"Page {page_num}: {len(quote_blocks)} entries")
        print(f"   Page {page_num} scraped ({len(quote_blocks)} entries)")
        page_num += 1
        time.sleep(0.5)

        if len(leads) >= 50:
            break

    return leads


def collect_leads() -> list[dict]:
    """
    Master function called by main.py.

    Strategy:
    1. Use local synthetic lead generation when network policy is restricted.
    2. Optionally try live scraping when ENABLE_LIVE_SCRAPING is set to True.
    3. Always return the same field names expected by cleaner.py/exporter.py.
    """
    print("\nScraping started - restricted network compatible mode ...")
    logger.info("collect_leads() called.")

    if ENABLE_LIVE_SCRAPING:
        live_leads = scrape_live()
        if live_leads:
            logger.info(f"Live scraping successful - {len(live_leads)} raw leads.")
            print(f"\nData collected - {len(live_leads)} raw entries scraped.\n")
            return live_leads

        logger.warning("Live scraping returned 0 results. Falling back to synthetic data.")

    print(
        f"   Network is restricted to allowed domains such as {ALLOWED_NETWORK_DOMAIN}.\n"
        "   External scraping targets may be blocked in this environment.\n"
        "   Generating realistic synthetic leads with the same structure as scraped data.\n"
    )

    leads = generate_synthetic_leads(total=50)
    random.shuffle(leads)

    for page in range(1, 6):
        batch = leads[(page - 1) * 10: page * 10]
        print(f"   Page {page} generated ({len(batch)} entries)")
        time.sleep(0.1)

    logger.info(f"Synthetic restricted-network dataset generated - {len(leads)} entries.")
    print(f"\nData collected - {len(leads)} entries loaded.\n")
    return leads
