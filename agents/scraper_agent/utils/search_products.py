from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from typing import List


class Product(BaseModel):
    name: str
    price_usd: str
    weight: str
    category: str


def search_products(query: str) -> List[Product]:
    """
    Searches the Grocery Store page using the provided query and returns a list of validated products.

    Steps:
    1. Launch a headless browser and navigate to the page at http://localhost:7070.
    2. Fill in the search input with the provided query.
    3. Wait for the loading spinner to disappear, indicating that results have been rendered.
    4. Extract product details and validate them using the Product Pydantic model.

    Returns:
        List[Product]: A list of products with attributes 'name', 'price_usd', 'weight', and 'category'.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Navigate to the mock page
            page.goto("http://localhost:7070")

            # Fill in the search input with the query
            page.fill("#searchInput", query)

            # Wait for product items to appear:
            page.wait_for_selector("#productList li", timeout=5000)

            # Query all product list items
            product_elements = page.query_selector_all("#productList li")
            results = []

            # Extract product details from each list item
            for product in product_elements:
                name = product.query_selector("h3").inner_text(
                ).strip() if product.query_selector("h3") else ""
                category = product.query_selector(
                    "p.mt-1").inner_text().strip() if product.query_selector("p.mt-1") else ""
                price_text = product.query_selector("div.text-right p:nth-child(1)").inner_text(
                ).strip() if product.query_selector("div.text-right p:nth-child(1)") else ""
                price_usd = price_text.lstrip("$")
                weight = product.query_selector("div.text-right p:nth-child(2)").inner_text(
                ).strip() if product.query_selector("div.text-right p:nth-child(2)") else ""

                results.append({
                    "name": name,
                    "category": category,
                    "price_usd": price_usd,
                    "weight": weight
                })

            browser.close()

            # Validate and convert each result using the Product model
            return [Product(**item) for item in results]
    except:
        return []
