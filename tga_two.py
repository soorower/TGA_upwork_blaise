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

df = pd.read_excel('tga_search_entries.xlsx')
names = df['Each Entry Link'].tolist()[:100]

for name in names:
    r = requests.get(
        name, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    # print(soup)

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
    print(public_artg_sum)
    print(product_info)
    print(f"{consumer_medicine}\n\n")
