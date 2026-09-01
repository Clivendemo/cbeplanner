"""
Curriculum Pipeline — PDF → AI Extraction → JSON → Seed Script → Database

Usage:
    python scripts/curriculum_pipeline.py                    # Process all PDFs in /pdfs/
    python scripts/curriculum_pipeline.py --file path.pdf    # Process a single PDF
    python scripts/curriculum_pipeline.py --run-seeds        # Run all generated seed scripts
"""

import pdfplumber
import os
import sys
import json
import hashlib
import asyncio
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load env from backend root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_extractor import extract_with_gemini_chunked
from seed_script_generator import generate_seed_script


# Directories
PDF_DIR = os.path.join(ROOT_DIR, "pdfs")
PROCESSED_DIR = os.path.join(ROOT_DIR, "pdfs_processed")
JSON_OUTPUT_DIR = os.path.join(ROOT_DIR, "curriculum_data")
SEED_OUTPUT_DIR = ROOT_DIR  # Seed scripts go in backend root (same as existing ones)
TRACK_FILE = os.path.join(JSON_OUTPUT_DIR, "processed_files.json")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)


def load_tracking():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    return {}


def save_tracking(data):
    with open(TRACK_FILE, "w") as f:
        json.dump(data, f, indent=2)


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def extract_text_from_pdf(path: str) -> str:
    """Extract all text from a PDF file."""
    all_text = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append(f"--- Page {i+1} ---\n{text}")
    return "\n\n".join(all_text)


def extract_metadata_from_filename(path: str) -> tuple:
    """Extract grade and subject hints from filename/path."""
    filename = os.path.basename(path).replace(".pdf", "")
    parts = path.lower().split(os.sep)

    # Try to find grade from path
    grade = "Grade 10"
    for p in parts:
        if "grade" in p:
            num = "".join(filter(str.isdigit, p))
            if num:
                grade = f"Grade {num}"
                break

    return grade, filename


async def process_single_pdf(path: str, grade_hint: str = "", subject_hint: str = "") -> dict:
    """Process a single PDF: extract text → AI extraction → JSON → seed script."""
    filename = os.path.basename(path)
    name_no_ext = os.path.splitext(filename)[0]

    print(f"\n{'=' * 60}")
    print(f"Processing: {filename}")
    print(f"{'=' * 60}")

    # Step 1: Extract text
    print("  Step 1: Extracting text from PDF...")
    text = extract_text_from_pdf(path)
    if not text.strip():
        print(f"  ERROR: No text found in {filename}")
        return None

    print(f"  Extracted {len(text)} characters from {filename}")

    # Detect grade/subject from filename if not provided
    if not grade_hint or not subject_hint:
        auto_grade, auto_subject = extract_metadata_from_filename(path)
        grade_hint = grade_hint or auto_grade
        subject_hint = subject_hint or auto_subject

    print(f"  Grade: {grade_hint}, Subject: {subject_hint}")

    # Step 2: AI extraction
    print("  Step 2: AI extraction with Gemini 2.5 Flash...")
    extracted = await extract_with_gemini_chunked(text, subject_hint, grade_hint)

    if not extracted or not extracted.get("strands"):
        print(f"  ERROR: AI extraction returned no data for {filename}")
        return None

    strand_count = len(extracted.get("strands", []))
    ss_count = sum(len(s.get("substrands", [])) for s in extracted.get("strands", []))
    slo_count = sum(
        sum(len(ss.get("slos", [])) for ss in s.get("substrands", []))
        for s in extracted.get("strands", [])
    )
    print(f"  Extracted: {strand_count} strands, {ss_count} substrands, {slo_count} SLOs")

    # Step 3: Save JSON
    safe_name = name_no_ext.lower().replace(" ", "_").replace("-", "_")
    json_path = os.path.join(JSON_OUTPUT_DIR, f"extracted_{safe_name}.json")
    with open(json_path, "w") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
    print(f"  Step 3: JSON saved to {json_path}")

    # Step 4: Generate seed script
    script_name = f"seed_{safe_name}.py"
    script_path = os.path.join(SEED_OUTPUT_DIR, script_name)
    generate_seed_script(extracted, script_path)
    print(f"  Step 4: Seed script saved to {script_path}")

    return {
        "filename": filename,
        "grade": extracted.get("grade", grade_hint),
        "subject": extracted.get("subject_name", subject_hint),
        "strands": strand_count,
        "substrands": ss_count,
        "slos": slo_count,
        "json_path": json_path,
        "script_path": script_path,
    }


async def process_all_pdfs():
    """Process all PDFs in the pdfs/ directory."""
    tracking = load_tracking()
    results = []

    pdf_files = []
    for root, _, files in os.walk(PDF_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    if not pdf_files:
        print(f"No PDFs found in {PDF_DIR}")
        return results

    print(f"\nFound {len(pdf_files)} PDF(s) to process\n")

    for path in pdf_files:
        filename = os.path.basename(path)
        h = file_hash(path)

        if h in tracking:
            print(f"Skipping (already processed): {filename}")
            continue

        result = await process_single_pdf(path)
        if result:
            results.append(result)
            tracking[h] = {
                "file": filename,
                "processed_at": str(datetime.now()),
                "result": result,
            }
            # Move to processed
            dest = os.path.join(PROCESSED_DIR, filename)
            os.rename(path, dest)

    save_tracking(tracking)

    # Print summary
    if results:
        print(f"\n{'=' * 60}")
        print("EXTRACTION SUMMARY")
        print(f"{'=' * 60}")
        for r in results:
            print(f"  {r['subject']} ({r['grade']}): {r['strands']} strands, {r['substrands']} substrands, {r['slos']} SLOs")
            print(f"    JSON: {r['json_path']}")
            print(f"    Script: {r['script_path']}")
        print(f"\nTo load data into DB, run the generated seed scripts:")
        for r in results:
            print(f"  python {r['script_path']}")
    else:
        print("\nNo new PDFs were processed.")

    return results


async def run_seed_scripts():
    """Find and run all auto-generated seed scripts."""
    import subprocess
    seed_files = [
        f for f in os.listdir(SEED_OUTPUT_DIR)
        if f.startswith("seed_") and f.endswith(".py")
    ]
    print(f"Found {len(seed_files)} seed scripts")
    for sf in sorted(seed_files):
        path = os.path.join(SEED_OUTPUT_DIR, sf)
        print(f"\nRunning: {sf}")
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Curriculum PDF Extraction Pipeline")
    parser.add_argument("--file", help="Process a single PDF file")
    parser.add_argument("--grade", help="Grade hint (e.g., 'Grade 10')", default="")
    parser.add_argument("--subject", help="Subject name hint", default="")
    parser.add_argument("--run-seeds", action="store_true", help="Run all generated seed scripts")
    args = parser.parse_args()

    if args.run_seeds:
        asyncio.run(run_seed_scripts())
    elif args.file:
        result = asyncio.run(process_single_pdf(args.file, args.grade, args.subject))
        if result:
            print(f"\nTo load into DB: python {result['script_path']}")
    else:
        asyncio.run(process_all_pdfs())


if __name__ == "__main__":
    main()
