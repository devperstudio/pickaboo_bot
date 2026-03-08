import re
import json
import os

TARGET_MODELS = [
    "realme note 70 4gb/64gb",
    "realme note 60x 4gb/64gb",
]


def load_buy_list(filepath: str = "buy.json") -> list[str]:
    if not os.path.exists(filepath):
        print(f"[WARN] {filepath} not found. No products will be clicked.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item.strip().lower() for item in data]


def clean_price(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def clean_rating(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def scroll_to_bottom(page) -> None:
    previous = 0
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        current = page.locator("h4.product-title").count()
        print(f"  [{current}] products loaded...")
        if current == previous:
            break
        previous = current


def parse_products(page, buy_list: list[str]) -> tuple[list[dict], bool]:
    """
    Returns (products, clicked) — clicked=True means a buy-list product
    was found and navigated to. Caller should stop the search loop.
    """
    page.wait_for_selector("h4.product-title", timeout=20000)
    scroll_to_bottom(page)

    titles = page.locator("h4.product-title")
    total  = titles.count()
    print(f"  Scanning {total} products...")

    results = []
    seen    = set()

    for i in range(total):
        try:
            title       = titles.nth(i).inner_text().strip()
            title_lower = title.lower()

            if not any(model in title_lower for model in TARGET_MODELS):
                continue

            if title_lower in seen:
                continue
            seen.add(title_lower)

            try:
                price = clean_price(
                    page.locator(".product-price span").nth(i).inner_text().strip()
                )
            except Exception:
                price = 0

            try:
                rating = clean_rating(
                    page.locator("div.stars-rating").nth(i).inner_text().strip()
                )
            except Exception:
                rating = 0

            product = {
                "title":        title,
                "variant":      title,
                "price":        price,
                "rating_count": rating,
            }

            print(f"  [MATCH] {title} | {price} BDT | {rating} ratings")
            results.append(product)

            # If this product is in buy list — click and stop everything
            if title_lower in buy_list:
                print(f"  [BUY]   '{title}' is in buy list — navigating to product page...")
                titles.nth(i).click()
                page.wait_for_load_state("networkidle", timeout=15000)
                print(f"  [BUY]   Product page loaded: {page.url}")
                return results, True  # Signal caller to stop search loop

        except Exception as e:
            print(f"  [ERROR] #{i}: {e}")

    return results, False