from bs4 import BeautifulSoup
import requests
from pprint import pprint
import pandas as pd
URL = "https://scrapeme.live/shop/"
page = requests.get(URL)
# Parse the HTML content
soup = BeautifulSoup(page.content, "html.parser")
shops=[]
ul_element=soup.find('ul', class_='products columns-4')
li_element= ul_element.find_all("li")
for li in li_element:
    title= li.find('h2', class_="woocommerce-loop-product__title" ).text
    price= li.find('span', class_='price').text
    url= li.find('a', class_="woocommerce-LoopProduct-link woocommerce-loop-product__link")['href']
    shop={
        "title": title,
        "price": price,
        "url": url
    }
    shops.append(shop)
pprint(shops)
# df = pd.DataFrame(shops)
# df.to_csv('scraped_data.csv')

# # Save to JSON
# df.to_json('scraped_data.json')
