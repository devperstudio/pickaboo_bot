import json
import os


OUTPUT_FILE = "data/buydetails.json"


def _text(page, selector: str, fallback: str = "") -> str:
    try:
        el = page.locator(selector).first
        el.wait_for(timeout=5000)
        return el.inner_text().strip()
    except Exception:
        return fallback


def scrape_product_detail(page) -> dict:
    page.wait_for_load_state("networkidle", timeout=15000)

    title  = _text(page, "h1") or _text(page, "h2.title")
    price  = _text(page, ".product-price span") or _text(page, "[class*='price'] span")
    brand  = _text(page, ".brand-view span")

    sold_by = ""
    try:
        for span in page.locator(".desktop-view span").all():
            txt = span.inner_text().strip()
            if txt and txt != "|":
                sold_by = txt
                break
    except Exception:
        pass

    images = []
    try:
        for img in page.locator(".dsn__main-image-container img, .detail-slider-desktop img").all():
            src = img.get_attribute("src") or ""
            if src and src not in images:
                images.append(src)
    except Exception:
        pass

    specs = {}
    try:
        for row in page.locator("table tr, .spec-table tr, [class*='spec'] tr").all():
            cells = row.locator("td").all()
            if len(cells) >= 2:
                key = cells[0].inner_text().strip()
                val = cells[1].inner_text().strip()
                if key:
                    specs[key] = val
    except Exception:
        pass

    return {
        "url":     page.url,
        "title":   title,
        "price":   price,
        "brand":   brand,
        "sold_by": sold_by,
        "images":  images,
        "specs":   specs,
    }


def save_buy_details(details: dict):
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=4, ensure_ascii=False)
    print(f"  [SAVE] Product details → {OUTPUT_FILE}")


def select_color_variant(page, color: str) -> bool:
    page.wait_for_timeout(2000)

    color_lower = color.strip().lower()
    swatches    = page.locator(".color-box center").all()
    print(f"  [VARIANT] Found {len(swatches)} swatch(es). Looking for '{color}'...")

    for i, swatch in enumerate(swatches):
        matched    = False
        match_info = ""

        try:
            tooltip = (swatch.locator("p.tooltiptext").text_content(timeout=2000) or "").strip().lower()
            print(f"  [VARIANT] Swatch [{i}] tooltip: '{tooltip}'")
            if color_lower in tooltip:
                matched    = True
                match_info = f"tooltip='{tooltip}'"
        except Exception:
            pass

        if not matched:
            try:
                src = (swatch.locator("img").get_attribute("src") or "").lower()
                if color_lower in src:
                    matched    = True
                    match_info = f"src='{src[-60:]}'"
            except Exception:
                pass

        if matched:
            print(f"  [VARIANT] Clicking swatch [{i}] matched by {match_info}")
            swatch.click()
            page.wait_for_timeout(1000)
            print(f"  [VARIANT] Color selected.")
            return True

    print(f"  [WARN] Color '{color}' not matched in any swatch.")
    return False


def click_buy_now(page, variant: str = ""):
    page.evaluate("document.querySelector('#variant')?.scrollIntoView()")
    page.wait_for_timeout(500)

    if variant:
        select_color_variant(page, variant)

    print(f"  [BUY NOW] Clicking Buy Now...")
    try:
        buy_btn = page.locator("div[class*='btn-here']").filter(has_text="Buy Now").first
        buy_btn.wait_for(timeout=8000)
        buy_btn.click()
        page.wait_for_load_state("networkidle", timeout=20000)
        page.wait_for_timeout(1000)
        print(f"  [BUY NOW] Navigated to: {page.url}")
    except Exception as e:
        print(f"  [ERROR] Buy Now click failed: {e}")
        return

    # Explicitly check for login page after every navigation
    from scraper.auth import handle_login_if_needed
    if handle_login_if_needed(page):
        # After login, navigate to cart
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [BUY NOW] Post-login URL: {page.url}")

    proceed_to_checkout(page)


def proceed_to_checkout(page):
    from scraper.auth import handle_login_if_needed
    handle_login_if_needed(page)

    print(f"  [CART] Waiting for cart page... URL: {page.url}")
    try:
        btn = page.locator("div.sc-ae21f0fc-0").filter(has_text="Proceed to checkout").first
        btn.wait_for(timeout=15000)
        print(f"  [CART] Clicking 'Proceed to checkout'...")
        btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [CART] Navigated to: {page.url}")
    except Exception as e:
        print(f"  [ERROR] Proceed to checkout failed: {e}")
        return

    place_order(page)


def place_order(page):
    print(f"  [CHECKOUT] Waiting for checkout page...")
    try:
        btn = page.locator("div.sc-ae21f0fc-0").filter(has_text="Place Order").first
        btn.wait_for(timeout=15000)
        print(f"  [CHECKOUT] Clicking 'Place Order'...")
        btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [CHECKOUT] Navigated to: {page.url}")
    except Exception as e:
        print(f"  [ERROR] Place Order failed: {e}")
        return

    select_cash_on_delivery(page)


def select_cash_on_delivery(page):
    print(f"  [PAYMENT] Waiting for payment page...")
    try:
        cod = page.locator("li").filter(has_text="Cash On Delivery").first
        cod.wait_for(timeout=15000)
        print(f"  [PAYMENT] Clicking 'Cash On Delivery'...")
        cod.click()
        page.wait_for_timeout(2000)
        print(f"  [PAYMENT] Cash On Delivery selected.")
    except Exception as e:
        print(f"  [ERROR] Cash On Delivery selection failed: {e}")
        return

    confirm_order(page)


def confirm_order(page):
    print(f"  [PAYMENT] Waiting for Confirm Order button...")
    try:
        btn = page.locator("div.sc-ae21f0fc-0").filter(has_text="Confirm Order").first
        btn.wait_for(timeout=10000)
        print(f"  [PAYMENT] Clicking 'Confirm Order'...")
        btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [PAYMENT] Navigated to: {page.url}")
    except Exception as e:
        print(f"  [ERROR] Confirm Order failed: {e}")
        return

    verify_order_success(page)


def verify_order_success(page):
    print(f"  [ORDER] Checking order status...")
    try:
        page.locator("section.success-message").wait_for(timeout=15000)
        message = page.locator("section.success-message p").first.inner_text().strip()

        print(f"\n{'='*50}")
        print(f"  ORDER SUCCESSFUL!")
        print(f"  {message}")
        print(f"  URL: {page.url}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"  [ERROR] Could not verify order success: {e}")