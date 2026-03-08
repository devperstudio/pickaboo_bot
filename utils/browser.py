from playwright.sync_api import sync_playwright

def start_browser():

    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=False,
        slow_mo=50
    )

    context = browser.new_context()

    page = context.new_page()

    return page, browser, playwright