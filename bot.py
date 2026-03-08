from playwright.sync_api import sync_playwright
from scraper.search import open_site, search_product
from scraper.product_parser import parse_products, load_buy_list
from scraper.product_detail import scrape_product_detail, save_buy_details, click_buy_now
from scraper.auth import attach_login_watcher
import json
import os

SEARCH_LIST   = [
    "realme Note 70",
    "realme Note 60x",
]

OUTPUT_FILE   = "data/products.json"
BUY_LIST_FILE = "buy.json"


def load_raw_buy_list(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(products: list):
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)
    print(f"  [SAVE] {len(products)} product(s) → {OUTPUT_FILE}")


def main():
    # Load buy list as raw dicts to access variant info
    raw_buy_list  = load_raw_buy_list(BUY_LIST_FILE)
    buy_list      = [item["title"].strip().lower() for item in raw_buy_list]
    variant_map   = {
        item["title"].strip().lower(): item.get("variant", "")
        for item in raw_buy_list
    }

    all_products  = []

    print(f"[INFO] Buy list: {buy_list}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page    = browser.new_page()

        # Attach global login watcher — intercepts login page on any navigation
        attach_login_watcher(page)

        try:
            open_site(page)

            for keyword in SEARCH_LIST:
                print(f"\n{'='*50}")
                print(f"[SEARCH] {keyword}")
                print(f"{'='*50}")

                search_product(page, keyword)
                page.wait_for_timeout(2000)

                products, clicked = parse_products(page, buy_list)
                all_products.extend(products)
                save_products(all_products)

                if clicked:
                    print(f"\n[INFO] Target product found. Stopping search loop.")

                    # Scrape full product detail page
                    print(f"[INFO] Scraping product details...")
                    details = scrape_product_detail(page)
                    save_buy_details(details)

                    print(f"\n[DETAILS]")
                    print(f"  Title   : {details['title']}")
                    print(f"  Price   : {details['price']}")
                    print(f"  Brand   : {details['brand']}")
                    print(f"  Sold by : {details['sold_by']}")
                    print(f"  URL     : {details['url']}")

                    # Get the variant for this product and click Buy Now
                    matched_title   = products[-1]["title"].strip().lower()
                    variant_to_pick = variant_map.get(matched_title, "")
                    print(f"\n[INFO] Variant to select: '{variant_to_pick}'")

                    click_buy_now(page, variant=variant_to_pick)
                    break

                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(500)

        except Exception as e:
            print(f"\n[FATAL] {e}")
            if all_products:
                save_products(all_products)

        finally:
            print(f"\n{'='*50}")
            print(f"[DONE] {len(all_products)} product(s) scanned")
            for item in all_products:
                print(f"  • {item['title']} | {item['price']} BDT | {item['rating_count']} ratings")
            print(f"{'='*50}\n")

            input("Press ENTER to close browser...")
            browser.close()


if __name__ == "__main__":
    main()