# scraper/search.py

def open_site(page):
    page.goto("https://www.pickaboo.com/")
    page.wait_for_load_state("domcontentloaded")


def search_product(page, keyword):

    # search input
    search_box = page.locator("input.searchInput").first
    search_box.click()
    search_box.fill(keyword)

    # click search icon (image inside button)
    page.locator("img[src*='menu-search']").first.click()

    page.wait_for_load_state("networkidle")