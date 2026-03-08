import json
import os


CONFIG_FILE = "config.json"


def load_credentials(filepath: str = CONFIG_FILE) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[AUTH] {filepath} not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def is_login_page(page) -> bool:
    try:
        return page.locator("input[name='userNumber']").is_visible(timeout=2000)
    except Exception:
        return False


def login(page) -> bool:
    """
    Two-step login:
      Step 1 — phone number + Sign Up/Login button
      Step 2 — password + Enter
    """
    creds    = load_credentials()
    phone    = creds.get("phone", "")
    password = creds.get("password", "")

    print(f"\n  [AUTH] Login page detected — logging in as {phone}...")

    # Step 1: phone number
    try:
        phone_input = page.locator("input[name='userNumber']")
        phone_input.wait_for(timeout=10000)
        phone_input.fill(phone)

        submit_btn = page.locator("button.custom-buttons").filter(has_text="Sign Up/Login")
        submit_btn.click()
        page.wait_for_timeout(2000)
        print(f"  [AUTH] Phone submitted.")
    except Exception as e:
        print(f"  [AUTH][ERROR] Step 1 failed: {e}")
        return False

    # Step 2: password
    try:
        pass_input = page.locator("input[name='userPassword']")
        pass_input.wait_for(timeout=10000)
        pass_input.fill(password)
        pass_input.press("Enter")
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [AUTH] Password submitted. URL: {page.url}")
    except Exception as e:
        print(f"  [AUTH][ERROR] Step 2 failed: {e}")
        return False

    if is_login_page(page):
        print(f"  [AUTH][ERROR] Still on login page — check credentials.")
        return False

    print(f"  [AUTH] Login successful.\n")
    return True


def handle_login_if_needed(page) -> bool:
    """
    Call this after any navigation.
    If login page is visible, performs auto-login and returns True.
    Otherwise does nothing and returns False.
    """
    if is_login_page(page):
        return login(page)
    return False


def attach_login_watcher(page):
    """
    Attaches a global listener to the page so that ANY navigation
    that lands on the login page triggers auto-login immediately.
    """
    creds = load_credentials()

    def on_navigation(frame):
        # Only handle main frame navigations, not iframes
        if frame != page.main_frame:
            return

        try:
            if is_login_page(page):
                print(f"\n  [AUTH] Login page intercepted at: {page.url}")
                login(page)
        except Exception:
            pass

    page.on("framenavigated", on_navigation)
    print(f"[AUTH] Login watcher attached.")