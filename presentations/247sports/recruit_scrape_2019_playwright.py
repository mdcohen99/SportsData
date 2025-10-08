from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://247sports.com/season/2019-basketball/RecruitRankings/?InstitutionGroup=HighSchool"

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"]) 
        # create a realistic context with headers and user agent
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        extra_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        context = browser.new_context(user_agent=ua, locale='en-US', extra_http_headers=extra_headers)
        page = context.new_page()
        # try a two-step navigation: visit the homepage first to establish any cookies, then the target
        try:
            page.goto('https://247sports.com/', timeout=60000, wait_until='networkidle')
        except Exception:
            # ignore failures on the root; proceed to target
            pass
        try:
            page.goto(URL, timeout=90000, wait_until='networkidle')
        except Exception:
            # final attempt with a longer timeout and looser wait
            try:
                page.goto(URL, timeout=120000, wait_until='load')
            except Exception:
                # give up after retries
                pass
        # wait for the player list items to appear (if they will)
        try:
            page.wait_for_selector('li.rankings-page__list-item', timeout=45000)
        except Exception:
            # if selector doesn't appear, proceed to capture whatever is there
            pass
        html = page.content()
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass

    soup = BeautifulSoup(html, 'html.parser')
    players = soup.find_all('li', class_='rankings-page__list-item')

    data = []
    for player in players:
        # Rank: look for rank column primary, fallback to score or ranking links
        rank = None
        rank_col = player.select_one('.rank-column .primary')
        if rank_col and rank_col.text.strip():
            rank = rank_col.text.strip()
        else:
            score_tag = player.select_one('.rankings-page__star-and-score .score')
            if score_tag:
                rank = score_tag.text.strip()
        # Name
        name_tag = player.select_one('a.rankings-page__name-link')
        if name_tag:
            name_text = name_tag.text.strip()
            name_parts = name_text.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        else:
            first_name = last_name = None
        # Position
        position_tag = player.select_one('.position')
        position = position_tag.text.strip() if position_tag else None
        # Metrics: height / weight
        metrics_tag = player.select_one('.metrics')
        height = weight = None
        if metrics_tag:
            metrics = metrics_tag.text.strip()
            if '/' in metrics:
                parts = [p.strip() for p in metrics.split('/')]
                if len(parts) >= 2:
                    height = parts[0]
                    weight = parts[1]
        # High school and state: in .recruit .meta
        school_meta = player.select_one('.recruit .meta')
        hs = state = None
        if school_meta:
            school_info = school_meta.text.strip()
            if '(' in school_info and ')' in school_info:
                hs = school_info.split('(')[0].strip()
                state = school_info.split('(')[1].replace(')', '').split(',')[-1].strip()
            else:
                hs = school_info
        # Stars count
        stars = len(player.select('.icon-starsolid.yellow'))
        # Commitment: look for image alt inside status
        commitment = None
        commit_img = player.select_one('.status img[alt]')
        if commit_img and commit_img.get('alt'):
            commitment = commit_img.get('alt').strip()
        else:
            commitment = 'Pro' if player.find('span', string='PRO') else None
        data.append({
            'class_year': 2019,
            'rank': rank,
            'first_name': first_name,
            'last_name': last_name,
            'position': position,
            'height': height,
            'weight': weight,
            'high_school': hs,
            'state': state,
            'stars': stars,
            'commitment': commitment
        })

    df = pd.DataFrame(data)
    df.to_csv('recruit_rankings_2019.csv', index=False)
    print('✅ Playwright CSV created: recruit_rankings_2019.csv')

if __name__ == '__main__':
    scrape()
