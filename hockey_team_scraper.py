from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import logging

logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


filename = f"Hockey_Team_Data_{datetime.now().strftime('%Y_%m_%d')}.csv"


def scrape_teams(page, base_url):
    all_data = []
    page_num = 1

    while True:

        if page_num == 1:
            page.goto(base_url)
        else:
            page.goto(f"{base_url}?page_num={page_num}")

        
        teams = page.query_selector_all(".team")

        
        if not teams:
            break

        
        for t in teams:
            try:
                name = t.query_selector(".name").inner_text().strip()
                year = int(t.query_selector(".year").inner_text().strip())
                wins = int(t.query_selector(".wins").inner_text().strip())
                losses = int(t.query_selector(".losses").inner_text().strip())

                win_pct_tag = t.query_selector(".pct")
                win_pct = float(win_pct_tag.inner_text().strip()) if win_pct_tag else None

                all_data.append({
                    "Name": name,
                    "Year": year,
                    "Wins": wins,
                    "Losses": losses,
                    "Win Percentage": win_pct
                })

            except Exception as e:
                logging.error(f"Error extracting row: {e}")
                continue


        page_num += 1

    return all_data


def save_to_csv(data):
    if not data:
        print("No data found!")
        return

    headers = data[0].keys()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def main():
    base_url = "https://www.scrapethissite.com/pages/forms/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()

        print("Scraping started...")
        data = scrape_teams(page, base_url)

        print(f"Scraped {len(data)} records")

        save_to_csv(data)

        print(f"Data saved to {filename}")

        browser.close()


if __name__ == "__main__":
    main()