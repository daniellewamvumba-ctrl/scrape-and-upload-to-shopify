import pandas as pd
import re

def clean_handle(title):
    handle = title.lower().strip()
    handle = re.sub(r'[^a-z0-9\s-]', '', handle)
    handle = re.sub(r'[\s-]+', '-', handle)
    return handle

def transform_to_shopify():
    # Load your scraped file
    df_raw = pd.read_csv('trotters_products.csv')
    
    # Client's required target sizes from the original project prompt
    youth_sizes = ["Youth S", "Youth M", "Youth L", "Youth XL"]
    adult_sizes = ["S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL"]
    all_required_sizes = youth_sizes + adult_sizes

    shopify_rows = []

    for _, row in df_raw.iterrows():
        base_handle = clean_handle(str(row['Title']))
        
        # Handle blank pricing dynamically - Injected standard pricing parameter
        scraped_price = str(row['Price']).strip()
        price = re.sub(r'[^\d.]', '', scraped_price) if scraped_price and scraped_price != 'nan' else "45.00"

        # Explicitly map the client's mandatory sizing variants to every product item
        for index, size in enumerate(all_required_sizes):
            new_row = {
                "Handle": base_handle,
                "Title": row['Title'] if index == 0 else "",  # First row ONLY
                "Body (HTML)": "<p>Ships in 2–4 weeks</p>" if index == 0 else "",  # Injected Client Shipping Note
                "Vendor": "Practice Custom Store",
                "Tags": "Jersey, Team, Apparel" if index == 0 else "",
                "Published": "TRUE",
                "Option1 Name": "Size",
                "Option1 Value": size,
                "Variant SKU": f"{base_handle}-{size.replace(' ', '')}".upper(),
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Qty": 150,
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": price,
                "Image Src": row['Image'] if (index == 0 and pd.notna(row['Image'])) else "", # Injected image safely
                "Status": "active"
            }
            shopify_rows.append(new_row)

    # Save to standard Shopify CSV Matrix format
    df_shopify = pd.DataFrame(shopify_rows)
    df_shopify.to_csv('shopify_final_import.csv', index=False)
    print(f"Success! Processed {len(df_raw)} source entries into {len(df_shopify)} Shopify database rows.")

if __name__ == "__main__":
    transform_to_shopify()






              