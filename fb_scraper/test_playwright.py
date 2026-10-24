from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # headless=False lets you watch the browser window open
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://quotes.toscrape.com")
    print("Title:", page.title())
    browser.close()
print("Playwright is ready!")