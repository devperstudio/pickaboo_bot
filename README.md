# Pickaboo E-Commerce Bot

An automated bot that searches for products on [Pickaboo](https://www.pickaboo.com), matches them against a buy list, selects a color variant, and completes the full checkout flow — including auto-login.

---

## Project Structure
```
ecommerce_bot/
│
├── bot.py                  # Entry point — run this
├── buy.json                # Products to buy (title + variant)
├── config.json             # Login credentials
│
├── scraper/
│   ├── __init__.py
│   ├── search.py           # Opens site and searches for products
│   ├── product_parser.py   # Scans search results, matches buy list
│   ├── product_detail.py   # Full checkout flow (variant → buy → order)
│   └── auth.py             # Auto-login handler
│
└── data/
    ├── products.json       # Scanned product results (auto-generated)
    └── buydetails.json     # Detail page data of purchased product (auto-generated)
```

---

## Requirements

- Python 3.10+
- pip

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ecommerce_bot.git
cd ecommerce_bot
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Install Python dependencies
```bash
pip install playwright
```

### 4. Install Playwright browsers
```bash
playwright install chromium
```

---

## Configuration

### `config.json` — Login credentials
```json
{
    "phone": "01798589910",
    "password": "k1h1a1n1"
}
```

### `buy.json` — Products to buy
```json
[
    {
        "title": "realme Note 70 4GB/64GB",
        "variant": "Obsidian Black"
    }
]
```

- `title` must match the exact product title shown on Pickaboo
- `variant` is the color name shown as tooltip (e.g. `Obsidian Black`, `Beach Gold`)

---

## Usage
```bash
python bot.py
```

---

## Full Bot Flow
```
1. Load buy.json and config.json
2. Open Pickaboo in Chromium browser
3. Attach global auto-login watcher
4. For each keyword in SEARCH_LIST:
   a. Search for the product
   b. Scroll to load all results
   c. Scan and match against TARGET_MODELS
   d. If matched product is in buy.json:
      - Click on the product
      - Scrape and save full product details → data/buydetails.json
      - Select color variant (e.g. Obsidian Black)
      - Click Buy Now
        → Auto-login if redirected to login page
      - Click Proceed to checkout
      - Click Place Order
      - Select Cash on Delivery
      - Click Confirm Order
      - Verify order success page
5. Save all scanned products → data/products.json
```

---

## Auto-Login

The bot attaches a **global login watcher** to the browser page at startup.
If a login page is detected at any point during the flow, it automatically:

1. Enters the phone number from `config.json`
2. Clicks **Sign Up/Login**
3. Enters the password
4. Presses **Enter** to submit

No manual intervention required.

---

## Output Files

| File | Description |
|------|-------------|
| `data/products.json` | All matched products with title, price, rating |
| `data/buydetails.json` | Full detail page data of the purchased product |

---

