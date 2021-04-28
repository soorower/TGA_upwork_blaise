import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup
import requests

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


def scrape_all_links():
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
        for linka, brand_name in zip(list_links, names):
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
                for i in range(1):
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
    df = df1.reset_index(drop=True)
    df.to_excel('tga_search_entries.xlsx', encoding='utf-8', index=False)


def scrape_each():
    df = pd.read_excel('tga_search_entries.xlsx')
    n = len(df['Brand Name'].tolist())
    print(f'there are total {n} links..')
    print('\n')
    print('''if you give 0 as input, it will start to scrape from first link''')
    start = input('Start scraping from(0): ')
    print('\n')
    print('if you give 5000 as input, it will end scraping 5000 links')
    end = input('Stop Scarping at(5000-10000 at a time recommended): ')

    links = df['Each Entry Link'].tolist()[int(f'{start}'):int(f'{end}')]
    names = df['Brand Name'].tolist()[int(f'{start}'):int(f'{end}')]
    # links = df['Each Entry Link'].tolist()[:500]
    # names = df['Brand Name'].tolist()[:500]
    data = []
    list = {}
    res_html = []

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            res_html.append(response)

    def main():
        with ThreadPoolExecutor(max_workers=12) as executor:
            with requests.Session() as session:
                print('Scraping Each Entry Started....Please Wait.')
                i = 1
                for link in links:
                    print(i)
                    i = i + 1
                    executor.map(fetch, [session], [link])
                executor.shutdown(wait=True)

    main()
    print('Scraping data from scraped <html> started....')
    counter = 1
    for r, name, url in zip(res_html, names, links):
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
    df1 = pd.DataFrame(data)
    df2 = df1.reset_index(drop=True)
    df2.to_csv('tga_final.csv', encoding='utf-8', index=False)

    time.sleep(2)

    df = pd.read_csv('tga_final.csv')

    brands = df['Brand Name'].tolist()
    each_entries = df['Each Entry Link'].tolist()

    artg_ids = df['ARTG ID'].tolist()
    product_names = df['Product Name'].tolist()

    ingres = df['Active Ingredients'].tolist()
    sponsors = df['Sponsor Name'].tolist()

    artg_entry_fors = df['ARTG entry for'].tolist()
    public_artg_sums = df['Public ARTG Summary'].tolist()

    product_infos = df['Product Information'].tolist()
    consumer_medicines = df['Consumer Medicine Information'].tolist()

    data1 = []
    list1 = {}
    counter = 1
    for brand, each_entry in zip(brands, each_entries):
        print(counter)
        counter = counter + 1
        each_entry1 = each_entry.split('i%3D')[1].split('&auth')[0]
        # print(each_entry)
        for artg, product_name, ingre, sponsor, artg_entry_for, public_artg_sum, product_info, consumer_medicine in zip(artg_ids, product_names, ingres, sponsors, artg_entry_fors, public_artg_sums, product_infos, consumer_medicines):
            if artg[8:] == each_entry1:
                list1 = {
                    'Brand Name': brand,
                    'Each Entry Link': each_entry,
                    'ARTG ID': artg[8:],
                    'Product Name': product_name,
                    'Active Ingredients': ingre,
                    'Sponsor Name': sponsor,
                    'ARTG entry for': artg_entry_for,
                    'Public ARTG Summary': public_artg_sum,
                    'Product Information': product_info,
                    'Consumer Medicine Information': consumer_medicine

                }
                data1.append(list1)

    # print(len(data1))

    df2 = pd.DataFrame(data1)
    df = df2.drop_duplicates(
        subset=['ARTG ID'], keep='first').reset_index(drop=True)
    df.to_csv(f'tga_final_{end}.csv', encoding='utf-8', index=False)


def mainmenu():
    print('\n')
    print('1. Scrape entry links for all brands')
    print('2. Collect info from each entry link')
    print('3. Quit')
    selection = int(input('Enter Choice: '))
    if selection == 1:
        scrape_all_links()
    elif selection == 2:
        scrape_each()
    elif selection == 3:
        exit()
    else:
        print("Invalid Choice. Inter 1-3")
        mainmenu()


mainmenu()

tiempo_total = time.time() - startTime
print(f"total time needed: {tiempo_total}")
