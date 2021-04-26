import json
import os
import cloudscraper
from bs4 import BeautifulSoup as bs
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import sys
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
from time import sleep
import random

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
df = pd.read_csv('BrandNames.csv')
names = df['Names'].tolist()
list_links = []
for name in names:
    query = name.replace('+', '%2B').replace(' ', '+').replace('(', '%28').replace(')', '%29').replace('/', '%2F').replace('&', '%26').replace("'", "%27").replace(',', '%2C').replace(
        ':', '%3A').replace(';', '%3B').replace('=', '%3D').replace('?', '%3F').replace('@', '%40').replace('*', '%2A').replace('!', '%20').replace('#', '%23').replace('$', '%24')
    query_link = f"https://tga-search.clients.funnelback.com/s/search.html?query={query}&collection=tga-artg"
    list_links.append(query_link)


data = []
list = {}
counter = 1
try:
    for linka, brand_name in zip(list_links[:100], names[:100]):
        print(counter)
        counter = counter + 1
        # print(f'Brand: {brand_name}')
        next_page_links = []
        link_contain = []

        def linkscrape(link):
            try:
                r = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(r.content, 'html.parser')
            except:
                pass
            link_box = soup.find(
                'div', attrs={'class': 'searchresults clearfloat'}).findAll('p')[1:]

            for link in link_box:
                try:
                    n = str(link.find('a')).split('href="')[
                        1].split('" title')[0].replace('amp;', '')
                except:
                    pass
                s = f"https://tga-search.clients.funnelback.com{n}"
                link_contain.append(s)

            if soup.find('map', attrs={'name': 'Previous and Next links if any'}).findAll('a'):
                for next in soup.find('map', attrs={'name': 'Previous and Next links if any'}).findAll('a'):
                    if 'Next 10' in next.string:
                        next_page = f"https://tga-search.clients.funnelback.com/s/{next['href']}"
                        next_page_links.append(next_page)
    #             print(next_page)
            link_contain.pop(-1)

        try:
            linkscrape(linka)
        except:
            pass

        k = 11
        try:
            for i in range(2):
                if next_page_links[-1].find(str(k))+1:
                    linkscrape(next_page_links[-1])
                k = k + 10
        except:
            pass

        print(f"Links Found: {len(link_contain)}\n")
        for linkish in link_contain:
            list = {
                'Brand Name': brand_name,
                'Each Entry Link': linkish
            }
            data.append(list)
except:
    pass
df1 = pd.DataFrame(data)
df = df1.drop_duplicates(
    subset=['Each Entry Link'], keep='first').reset_index(drop=True)
df.to_excel('tga_search_entries_two.xlsx', encoding='utf-8', index=False)

tiempo_total = time.time() - startTime
print(f"total time needed: {tiempo_total}")
