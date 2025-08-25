import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import datetime

# --- Config ---
OUTPUT_DIR = Path("docs")
OUTPUT_FILE = OUTPUT_DIR / "entries.json"

# Map grade → official KICD URL
GRADE_URLS = {
    7: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-seven-designs/",
    8: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-eight-designs/",
    9: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-nine-designs/",
    10: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-ten/",
    11: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-eleven/",
    12: "https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-twelve/",
}

def fetch_page(url):
    """Download and parse a page"""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

def parse_grade(grade, url):
    """Extract subjects & links for a grade page"""
    soup = fetch_page(url)
    subjects = []
    
    # Look for subject links inside content area
    for a in soup.select("a"):
        name = a.get_text(strip=True)
        href = a.get("href")
        if not name or not href:
            continue
        if "design" in href or "curriculum" in href:  # crude filter
            subjects.append({
                "Grade": grade,
                "Subject": name,
                "KICD_RefURL": href
            })
    return subjects

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    entries = []

    # Crawl each grade page
    for grade, url in GRADE_URLS.items():
        try:
            subjects = parse_grade(grade, url)
            for i, subj in enumerate(subjects, start=1):
                entry = {
                    "RowId": f"{subj['Subject']}-G{grade}-{i:03d}",
                    "CBC_Level": "Junior School" if grade <= 9 else "Senior School",
                    "Grade": grade,
                    "Subject": subj["Subject"],
                    "Strand": "",
                    "Substrand": "",
                    "SLO": "",
                    "StudentQuestion": "",
                    "GuidedHint": "",
                    "FollowUp1": "",
                    "FollowUp2": "",
                    "Difficulty": "",
                    "Tags": "",
                    "KICD_RefURL": subj["KICD_RefURL"],
                    "Pathway": "" if grade <= 9 else "TBD"
                }
                entries.append(entry)
            print(f"✅ Grade {grade}: {len(subjects)} subjects found")
        except Exception as e:
            print(f"⚠️ Failed grade {grade}: {e}")

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.datetime.utcnow().isoformat(), "entries": entries}, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(entries)} entries → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
