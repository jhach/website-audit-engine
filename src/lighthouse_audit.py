import json
import subprocess
from pathlib import Path


def run_lighthouse(url: str, output_dir: Path, slug: str) -> dict:
    output_path = output_dir / f"{slug}_lighthouse.json"

    cmd = [
        "npx",
        "lighthouse",
        url,
        "--output=json",
        f"--output-path={output_path}",
        "--quiet",
        '--chrome-flags=--headless'
    ]

    subprocess.run(cmd, check=True)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    categories = data.get("categories", {})
    audits = data.get("audits", {})

    return {
        "performance": _score_to_100(categories.get("performance", {}).get("score")),
        "accessibility": _score_to_100(categories.get("accessibility", {}).get("score")),
        "best_practices": _score_to_100(categories.get("best-practices", {}).get("score")),
        "seo": _score_to_100(categories.get("seo", {}).get("score")),
        "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("displayValue"),
        "cumulative_layout_shift": audits.get("cumulative-layout-shift", {}).get("displayValue"),
        "speed_index": audits.get("speed-index", {}).get("displayValue"),
        "total_blocking_time": audits.get("total-blocking-time", {}).get("displayValue"),
        "raw_report_path": str(output_path)
    }


def _score_to_100(value):
    if value is None:
        return None
    return int(round(value * 100))