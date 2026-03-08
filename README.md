# Pickaboo E-Commerce Bot

An automated bot that searches for products on **Pickaboo**, matches them against a buy list, selects a color variant, and completes the full checkout flow — including auto-login.

---

# Project Structure

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

# Requirements

* Python **3.10+**
* pip

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/your-username/ecommerce_bot.git
cd ecommerce_bot
```

## 2. Create and activate a virtual environment

Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Python dependencies

```bash
pip install playwright
```

---

## 4. Install Playwright browsers

```bash
playwright install chromium
```

---

# Configuration

## config.json — Login Credentials

```
{
    "phone": "01798589910",
    "password": "k1h1a1n1"
}
```

---

## buy.json — Products to Buy

```
[
    {
        "title": "realme Note 70 4GB/64GB",
        "variant": "Obsidian Black"
    }
]
```

Notes:

* `title` must match the **exact product title** shown on Pickaboo.
* `variant` is the **color name tooltip** (e.g. *Obsidian Black*, *Beach Gold*).

---

# Usage

Run the bot:

```bash
python bot.py
```

---

# Full Bot Flow

1. Load `buy.json` and `config.json`
2. Open Pickaboo in Chromium browser
3. Attach global auto-login watcher

For each keyword in `SEARCH_LIST`:

1. Search for the product

2. Scroll to load all results

3. Scan and match against `TARGET_MODELS`

4. If matched product exists in `buy.json`:

   * Click the product
   * Scrape and save full product details → `data/buydetails.json`
   * Select color variant (example: **Obsidian Black**)
   * Click **Buy Now**

   If redirected to login page:

   * Auto login using credentials

   Continue checkout:

   * Click **Proceed to checkout**
   * Click **Place Order**
   * Select **Cash on Delivery**
   * Click **Confirm Order**
   * Verify order success page

5. Save all scanned products → `data/products.json`

---

# Auto-Login

The bot attaches a **global login watcher** to the browser page when it starts.

If a login page is detected at any moment during the flow, the bot automatically:

1. Enters the phone number from `config.json`
2. Clicks **Sign Up / Login**
3. Enters the password
4. Presses **Enter** to submit

No manual interaction required.

---

# Output Files

| File                   | Description                                    |
| ---------------------- | ---------------------------------------------- |
| `data/products.json`   | All matched products with title, price, rating |
| `data/buydetails.json` | Full detail page data of the purchased product |

---

# Git Setup

Initialize repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/ecommerce_bot.git
git push -u origin main
```

Update after changes:

```bash
git add .
git commit -m "your message"
git push
```

---

# .gitignore (Recommended)

Create a `.gitignore` file:

```
.venv/
__pycache__/
data/
config.json
*.pyc
.DS_Store
```
