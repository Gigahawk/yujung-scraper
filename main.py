from time import sleep
from pathlib import Path
import os

from playwright.sync_api import sync_playwright, Page

EXPORT_DIR = Path("export")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def accept_cookies(page: Page):
    print("Accepting cookies")
    page.goto("https://www.yujung.me")
    page.click("button.accept")

def login(page: Page):
    print("Navigating to login page")
    page.goto("https://www.yujung.me/account/login")
    print(
        "Enter credentials and press Sign In, then press continue in the "
        "Playwright Inspector"
    )
    page.pause()

def get_recipe_links(page: Page) -> list[str]:
    print("Looking up recipe links")
    next_page = "https://www.yujung.me/from-the-heart-recipes"
    recipes = []
    while True:
        if next_page is None:
            print("Out of pages")
            return list(set(recipes))
        print(f"Going to {next_page}")
        page.goto(next_page)
        next_page = None
        all_a_tags = page.query_selector_all("a")
        for tag in all_a_tags:
            href = tag.get_attribute("href")
            if not href.startswith("/from-the-heart-recipes"):
                continue
            if "category" in href:
                continue
            if "reversePaginate" in href:
                continue
            if "?offset" in href:
                print(f"found next page: {href}")
                next_page = f"https://www.yujung.me{href}"
                continue
            recipes.append(href)
            print(href)

def download_recipes(page: Page, links: list[str]):
    for link in links:
        url = f"https://www.yujung.me{link}"
        name = EXPORT_DIR / f"{Path(link).name}.pdf"
        print(f"Navigating to {url} and saving to {name}")
        page.goto(url)
        page.add_style_tag(content="x-pw-glass { display: none !important; }")
        page.add_style_tag(content="header { display: none !important; }")
        page.emulate_media(media="print")
        page.pdf(
            path=name,
            format="letter",
            margin={
                key: "1in" for key in ["top", "right", "bottom", "left"]
            },
            outline=True
        )


with sync_playwright() as p:
    print("Opening chromium")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    accept_cookies(page)
    login(page)
    recipe_links = get_recipe_links(page)
    download_recipes(page, recipe_links)
    print("Done exporting")

