import requests
from bs4 import BeautifulSoup
import csv
import re

"""
Here the code demonstrates the approach to fetch category wise product details.
Only 5 categories are shown here and 5 products for each category.
To view all the categories and products need to remove the count condition from the line 35th,
and also need to remove slicing condition from the line 54.
This will provide you all the details.

At the last there is a code to store data in CSV file which is commented right now, if you want to store uncomment it.
"""

# Proxy setup
proxy = 'geo.iproyal.com:12321'
proxy_auth = 'Qp2YvQ9hRCyienEj:GVPXaVCFvaFoMgZc_country-cl'
proxies = {
    'http': f'http://{proxy_auth}@{proxy}',
    'https': f'http://{proxy_auth}@{proxy}'
}

headers = {
    'User-Agent': 'Mozilla/5.0'
}

url = "https://www.lider.cl/inicio"
base_url = "https://www.lider.cl"

response = requests.get(url, headers=headers, proxies=proxies)
soup = BeautifulSoup(response.text, "html.parser")

pattern = re.compile(r".*/(\d+_)+\d+$")

category_links = []
count =1
for tag in soup.find_all("a", href=True):
    if pattern.search(tag["href"]) and count!=6:
        category_links.append(tag)
        count+=1

products = []

for link in category_links:
    href = link.get('href')
    if href:
        products.append(href if href.startswith('http') else base_url + href)

product_data = []

for url in products:
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.text, "html.parser")

        script_tag = soup.find_all('div', attrs={'role': 'group'})[:5]
        if script_tag:
            for item in script_tag:

                name_tag = item.find(attrs={"data-automation-id": "product-title"})
                name = name_tag.get_text(strip=True) if name_tag else None

                link_tag = item.find("a", href=True)
                product_link = base_url + link_tag["href"] if link_tag else None

                img_tag = item.find("img", attrs={"data-testid": "productTileImage"})
                image = img_tag["src"] if img_tag else None

                brand_tag = None
                for div in item.find_all("div"):
                    if div.string and div.string.strip() and not div.find():
                        text = div.get_text(strip=True)
                        if not text.startswith("$") and "Ahorra" not in text and len(text) < 30:
                            brand_tag = text
                            break

                brand = brand_tag if brand_tag else None

                prices = item.find_all("div", string=re.compile(r"\$\d+"))
                price = prices[1].get_text(strip=True) if len(prices) > 1 else None  # original price
                promotion_price = prices[0].get_text(strip=True) if prices else None  # discounted price

                promo = item.find("span", string=re.compile(r"Ahorra.*"))
                promotion_details = promo.get_text(strip=True) if promo else None

                print(f"Name: {name}")
                print(f"Product Link: {product_link}")
                print(f"Image: {image}")
                print(f"Brand: {brand}")
                print(f"Price: {price}")
                print(f"Promotion Price: {promotion_price}")
                print(f"Promotion Details: {promotion_details}")
                print("-" * 40)

                product_data.append({
                    "name": name,
                    "product_link": product_link,
                    "image": image,
                    "brand": brand,
                    "price": price,
                    "promotion_price": promotion_price,
                    "promotion_details": promotion_details
                })

    except Exception as e:
        print(f"Error scraping {url}: {e}")

# If want to save the data into csv file.

with open("lider_product_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "product_link", "image", "brand", "price", "promotion_price", "promotion_details"])
    writer.writeheader()
    writer.writerows(product_data)

