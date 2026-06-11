import csv
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_trotters():
    stealth_engine = Stealth()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await stealth_engine.apply_stealth_async(context)
        page = await context.new_page()

        print("Navigating to Trotters clothing collection...")
        await page.goto("https://trotters.co.uk", wait_until="commit", timeout=60000)

        print("Scrolling to load products...")
        for _ in range(4):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(1)

        print("Extracting product links...")
        raw_links = await page.locator("main a[href*='/products/']").evaluate_all(
            "links => links.map(a => a.href)"
        )
        
        target_links = list(set(raw_links))[:60] 
        print(f"Found {len(target_links)} unique product links. Extracting details...")
        
        if not target_links:
            print("Error: No product links found.")
            await browser.close()
            return

        products = []

        for index, link in enumerate(target_links, start=1):
            try:
                # FIX 1: Change wait_until to 'commit' so the page doesn't hang on slow image loads
                await page.goto(link, wait_until="commit", timeout=20000)
                
                # Wait directly for the actual title container class
                await page.wait_for_selector(".template-product__title", timeout=10000)

                # FIX 2: Target the specific product title class to avoid strict mode errors
                name = await page.locator(".template-product__title").first.inner_text()
                
                price_el = page.locator(".price-item--regular, .price, [class*='price']").first
                price = await price_el.inner_text() if await price_el.count() > 0 else "0.00"

                size_elements = page.locator("select[id*='Option'] option, label[for*='Option'], fieldset input + label, .variant-input label")
                sizes = await size_elements.all_inner_texts()
                sizes = [s.strip() for s in sizes if s.strip() and not s.lower().startswith("select")]

                if not sizes:
                    sizes = ["One Size"]

                img_el = page.locator("img[src*='/products/'], .product__media img").first
                image_url = await img_el.get_attribute("src") if await img_el.count() > 0 else ""
                
                if image_url and image_url.startswith("//"):
                    image_url = f"https:{image_url}"

                products.append({
                    "Title": name.strip(),
                    "Price": price.strip(),
                    "Link": link,
                    "Sizes": ", ".join(sizes),
                    "Image": image_url
                })
                print(f"[{index}/{len(target_links)}] Extracted: {name.strip()}")

            except Exception as e:
                print(f"Error extracting {link}: {e}")
            
        if products:
            with open("trotters_products.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=products[0].keys())
                writer.writeheader()
                writer.writerows(products)
            print("\nSuccess! Data safely saved to 'trotters_products.csv'")
        else:
            print("\nError: No item data collected.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_trotters())





              