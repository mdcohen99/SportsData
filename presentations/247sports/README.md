# 247Sports Recruit Rankings scraper

This folder contains a Playwright-based scraper and output CSV for high school basketball recruit rankings from 247Sports.

Files include:

- `recruit_scrape_2019_playwright.py` — Playwright scraper that renders the page, parses the DOM with BeautifulSoup, and writes `recruit_rankings_2019.csv`.
- `recruit_rankings_2019.csv` — Scraped dataset (2019 class year) with columns: `class_year, rank, first_name, last_name, position, height, weight, high_school, state, stars, commitment`.

Dependencies

- Python 3.8+ (tested with Python 3.13)
- packages: `playwright`, `beautifulsoup4`, `pandas`, `requests` (install with pip)

Install and setup

```bash
python3 -m pip install --user playwright beautifulsoup4 pandas requests
# install browser binaries for playwright (only need to run once)
/Users/mattcohen/Library/Python/3.13/bin/playwright install chromium
```

Usage

```bash
python3 data/247sports/recruit_scrape_2019_playwright.py
# Output: data/247sports/recruit_rankings_2019.csv (or the CSV will be created in the current working directory)
```

Notes

- The scraper uses a headless Chromium browser to render JavaScript-heavy pages. This is more reliable than requests-only scraping but requires downloading browser binaries.
- Respect 247Sports' Terms of Service and robots.txt before running the scraper at scale. This script is intended for personal/educational use.
- If you want the CSV saved into a different directory, update the `df.to_csv(...)` path in the script or run from the target directory.

