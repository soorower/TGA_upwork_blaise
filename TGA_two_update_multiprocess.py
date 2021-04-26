
from os import link
import aiohttp
import asyncio
from numpy.core.arrayprint import set_printoptions
import pandas as pd
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
from bs4 import BeautifulSoup
import requests
from time import sleep
from multiprocessing.pool import Pool
import multiprocessing

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'tga-search.clients.funnelback.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Safari/537.36'
}
# startTime = time.time()


df = pd.read_excel('tga_search_entries_two.xlsx')
links = df['Each Entry Link'].tolist()


def do_something(url):
    response = requests.get(url, headers=headers)
    print(response.content)
    return response.content


res = []


def main(number1, number2):
    startTime = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [link for link in links[number1:number2]]
        rest = [val for val in executor.map(do_something, secs)]
    res.extend(rest)
    tiempo_total = time.time() - startTime
    print(f"total time needed: {tiempo_total}")
    print(len(res))


if __name__ == '__main__':
    i = 0
    n = 1
    # try:
    for l in range(1):
        main(i, n)
        i = i + 50
        n = n + 50
    # except:
    #     pass
    df1 = pd.DataFrame(res)
    df = df1.reset_index(drop=True)
    df.to_excel('tga_each_html_1.xlsx', encoding='utf-8', index=False)
