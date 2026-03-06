import subprocess
from pathlib import Path


def capture_screenshots(url: str, desktop_path: Path, mobile_path: Path):

    script = f"""
const {{ chromium }} = require('playwright');

(async() => {{

  const browser = await chromium.launch({{ headless: true }});

  // Desktop screenshot
  const desktopPage = await browser.newPage({{
    viewport: {{ width: 1440, height: 2200 }}
  }});

  await desktopPage.goto('{url}', {{ waitUntil: 'networkidle', timeout: 30000 }});

  await desktopPage.screenshot({{
    path: '{desktop_path}',
    fullPage: true
  }});

  // Mobile screenshot
  const mobilePage = await browser.newPage({{
    viewport: {{ width: 390, height: 844 }},
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'
  }});

  await mobilePage.goto('{url}', {{ waitUntil: 'networkidle', timeout: 30000 }});

  await mobilePage.screenshot({{
    path: '{mobile_path}',
    fullPage: true
  }});

  await browser.close();

}})();
"""

    subprocess.run(["node", "-e", script], check=True)