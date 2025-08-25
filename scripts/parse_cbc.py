import pdfplumber
import csv
import os
import re
from pathlib import Path

# Define your input/output
PDF_DIR = Path("pdfs")
OUT_CSV = Path("output/cbc_entries.csv")

# Table headers
FIELDS = [
    "RowId", "CBC_Level", "Grade", "Subject",
    "Strand", "Substrand", "SLO",
    "KICD_RefURL"
]

def clean_text(text):
    if not text: return ""
    return re.sub(r"\s+", " ", text.strip())

def parse_pdf(pdf_path, subject, grade, ref_url):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue

            # Very naive: look for "Strand", "Sub-strand", "Specific Learning Outcomes"
            # CBC PDFs usually structure SLOs in bullet points or numbered lists
            lines = text.splitlines()
            strand, substrand = None, None
            for line in lines:
                line = clean_text(line)

                # Capture strand
                if line.lower().startswith("strand"):
                    strand = line
                # Capture substrand
                elif line.lower().startswith("sub-strand"):
                    substrand = line
                # Capture SLO
                elif re.match(r"^\d+\. ", line):  # like "1. Solve linear equations..."
                    slo = line
                    rowid = f"{subject[:4].upper()}-G{grade}-{len(rows)+1:03d}"
                    rows.append({
                        "RowId": rowid,
                        "CBC_Level": "Junior School" if grade <= 9 else "Senior School",
                        "Grade": grade,
                        "Subject": subject,
                        "Strand": strand,
                        "Substrand": substrand,
                        "SLO": slo,
                        "KICD_RefURL": ref_url
                    })
    return rows

def main():
    all_rows = []
    # Example: parse Grade 7 Math
    rows = parse_pdf(PDF_DIR/"GRADE-7-MATHEMATICS.pdf",
                     subject="Mathematics",
                     grade=7,
                     ref_url="https://kicd.ac.ke/cbc-materials/curriculum-designs/grade-seven-designs/")
    all_rows.extend(rows)

    # TODO: Add Grade 8–12, other subjects

    # Write CSV
    os.makedirs(OUT_CSV.parent, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"✅ Wrote {len(all_rows)} rows → {OUT_CSV}")

if __name__ == "__main__":
    main()
