from os import link
import aiohttp
import asyncio
from numpy.core.arrayprint import set_printoptions
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup
import requests
from time import sleep

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'tga-search.clients.funnelback.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Safari/537.36'
}
startTime = time.time()


df = pd.read_excel('tga_search_entries_two.xlsx')
links = df['Each Entry Link'].tolist()[:100]
names = df['Brand Name'].tolist()[:100]
data = []
list = {}
res = []


def fetch(session, url):
    with session.get(url, headers=headers) as response:
        res.append(response)


def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        with requests.Session() as session:
            for link in links:
                executor.map(fetch, [session], [link])
            executor.shutdown(wait=True)


main()
counter = 1
for r, name, url in zip(res, names, links):
    soup = BeautifulSoup(r.content, 'lxml')
    # print(soup)
    print(counter)
    counter = counter + 1

    artg_id = soup.find('h2', attrs={'class': 'search-heading'}).string

    tables = soup.find('table', attrs={'class': 'artg-record'})

    public_artg_sums = []
    product_infos = []
    consumer_medicines = []
    for tab in tables.findAll('tr'):
        if 'Product name' in tab.find('th').string:
            product_name = tab.find('td').string
        if 'Active ingredients' in tab.find('th').string:
            active_ingre = tab.find('td').string
        if 'Sponsor name' in tab.find('th').string:
            sponsor_name = tab.find('td').string
        if 'ARTG entry for' in tab.find('th').string:
            artg_en = tab.find('td').string
            artg_en_for = " ".join(artg_en.split())
        try:
            if 'Public ARTG summary' in tab.find('th').string:
                public_artg_sum = tab.find('td').find('a')['href']
                public_artg_sums.append(public_artg_sum)
        except:
            public_artg_sum.append('-')
        try:
            if 'Product Information' in tab.find('th').string:
                product_info = tab.find('td').find('a')['href']
                product_infos.append(product_info)
        except:
            product_infos.append('-')
        try:
            if 'Consumer Medicines Information' in tab.find('th').string:
                consumer_medicine = tab.find('td').find('a')['href']
                consumer_medicines.append(consumer_medicine)
        except:
            consumer_medicines.append('-')

    if len(public_artg_sums) == 0:
        public_artg_sum = '-'
    if len(product_infos) == 0:
        product_info = '-'
    if len(consumer_medicines) == 0:
        consumer_medicine = '-'

    # print(artg_id)
    # print(product_name)
    # print(active_ingre)
    # print(sponsor_name)
    # print(artg_en_for)
    # print(public_artg_sum)
    # print(product_info)
    # print(f"{consumer_medicine}\n\n")
    list = {
        'Brand Name': name,
        'Each Entry Link': url,
        'ARTG ID': artg_id,
        'Product Name': product_name,
        'Active Ingredients': active_ingre,
        'Sponsor Name': sponsor_name,
        'ARTG entry for': artg_en_for,
        'Public ARTG Summary': public_artg_sum,
        'Product Information': product_info,
        'Consumer Medicine Information': consumer_medicine
    }
    data.append(list)
    # print(data)


df1 = pd.DataFrame(data)
df = df1.drop_duplicates(
    subset=['ARTG ID'], keep='first').reset_index(drop=True)
df.to_csv('tga_artg_final_100.csv', encoding='utf-8', index=False)

tiempo_total = time.time() - startTime
print(f"total time needed: {tiempo_total}")

#
