import subprocess
from pathlib import Path


def capture_desktop_screenshot(url: str, output_path: Path) -> None:
    script = f"""
const {{ chromium }} = require('playwright');

(async() => {{
  const browser = await chromium.launch({{ headless: true }});
  const page = await browser.newPage({{
    viewport: {{ width: 1440, height: 2200 }}
  }});

  await page.goto('{url}', {{
    waitUntil: 'networkidle',
    timeout: 30000
  }});

  await page.screenshot({{
    path: '{output_path}',
    fullPage: true
  }});

  await browser.close();
}})();
"""

    subprocess.run(
        ["node", "-e", script],
        check=True
    )