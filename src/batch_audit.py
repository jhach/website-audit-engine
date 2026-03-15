from __future__ import annotations

import csv
import logging
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from src.main import run_audit


INPUT_CSV = Path("businesses.csv")
REPORTS_DIR = Path("reports")
LOGS_DIR = Path("logs")
FAILED_SITES_FILE = LOGS_DIR / "failed_sites.txt"
BATCH_RESULTS_FILE = LOGS_DIR / "batch_results.csv"
BATCH_LOG_FILE = LOGS_DIR / "batch_run.log"

MAX_WORKERS = 5
MAX_PAGES = 5
GENERATE_PDF = True
GENERATE_SCREENSHOTS = True


@dataclass
class BusinessRecord:
    business_name: str
    website: str

    @property
    def slug(self) -> str:
        return slugify(self.business_name)

    @property
    def output_dir(self) -> Path:
        return REPORTS_DIR / self.slug


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(BATCH_LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def load_businesses(csv_path: Path) -> list[BusinessRecord]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    businesses: list[BusinessRecord] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required_columns = {"business_name", "website"}
        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

        for row in reader:
            business_name = (row.get("business_name") or "").strip()
            website = (row.get("website") or "").strip()

            if not business_name or not website:
                logging.warning("Skipping incomplete row: %s", row)
                continue

            businesses.append(BusinessRecord(
                business_name=business_name,
                website=website,
            ))

    return businesses


def append_failure(record: BusinessRecord, reason: str) -> None:
    with FAILED_SITES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{record.business_name} | {record.website} | {reason}\n")


def write_batch_result(row: dict) -> None:
    file_exists = BATCH_RESULTS_FILE.exists()

    with BATCH_RESULTS_FILE.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "business_name",
                "website",
                "status",
                "site_score",
                "grade",
                "output_folder",
                "markdown_report",
                "pdf_report",
                "error",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def extract_score_fields(result: dict) -> tuple[str, str]:
    homepage_summary = result.get("homepage_summary") or {}
    scorecard = homepage_summary.get("scorecard") or {}

    site_score = scorecard.get("total_score", "")
    grade = scorecard.get("grade", "")

    return str(site_score), str(grade)


def audit_business(record: BusinessRecord) -> tuple[BusinessRecord, bool, str]:
    try:
        time.sleep(random.uniform(0.8, 2.0))

        record.output_dir.mkdir(parents=True, exist_ok=True)

        result = run_audit(
            url=record.website,
            output_root=record.output_dir,
            business_name=record.business_name,
            max_pages=MAX_PAGES,
            generate_pdf=GENERATE_PDF,
            generate_screenshots=GENERATE_SCREENSHOTS,
        )

        site_score, grade = extract_score_fields(result)

        write_batch_result({
            "business_name": record.business_name,
            "website": record.website,
            "status": result.get("status", "unknown"),
            "site_score": site_score,
            "grade": grade,
            "output_folder": str(record.output_dir),
            "markdown_report": result.get("markdown_report_path", ""),
            "pdf_report": result.get("pdf_report_path", ""),
            "error": "",
        })

        return record, True, "ok"

    except Exception as e:
        append_failure(record, str(e))

        write_batch_result({
            "business_name": record.business_name,
            "website": record.website,
            "status": "failed",
            "site_score": "",
            "grade": "",
            "output_folder": str(record.output_dir),
            "markdown_report": "",
            "pdf_report": "",
            "error": str(e),
        })

        logging.exception("Audit failed for %s", record.business_name)
        return record, False, str(e)


def main() -> None:
    setup_logging()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    businesses = load_businesses(INPUT_CSV)
    logging.info("Loaded %d businesses", len(businesses))

    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {
            executor.submit(audit_business, business): business
            for business in businesses
        }

        for future in as_completed(future_map):
            record = future_map[future]
            try:
                _, success, message = future.result()
                if success:
                    success_count += 1
                    logging.info("Completed: %s", record.business_name)
                else:
                    failure_count += 1
                    logging.error("Failed: %s | %s", record.business_name, message)
            except Exception as e:
                failure_count += 1
                append_failure(record, f"Unhandled future error: {e}")
                logging.exception("Unhandled error for %s", record.business_name)

    logging.info("Batch complete. Success=%d Failed=%d", success_count, failure_count)
    print(f"Batch complete. Success={success_count} Failed={failure_count}")


if __name__ == "__main__":
    main()