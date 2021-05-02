import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup
import requests
startTime = time.time()
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'tga-search.clients.funnelback.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Safari/537.36'
}


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

# -----------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------


def scrape_each():
    df = pd.read_excel('tga_search_entries.xlsx')
    n = len(df['Brand Name'].tolist())
    print(f'Total links to scrape from = {n}')
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

# -----------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------


def scrape_whole():
    print('Searching for total number of entries...')
    r = requests.get('https://tga-search.clients.funnelback.com/s/search.html?from-advanced=true&collection=tga-artg&fmo=on&daat=0&query_or=*&meta_i=&meta_F=&meta_A=&meta_H=&meta_bts=%21Y&meta_I=&meta_B=&meta_D=&meta_d1day=&meta_d1month=&meta_d1year=&meta_d2day=&meta_d2month=&meta_d2year=', headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    number_of_entries = int(soup.find('p', attrs={'class': 'description'}).string.split(
        'Documents: ')[1].split(' fully')[0].replace(',', ''))
    print(f'Total number of entries found: {number_of_entries}')
    x = int(number_of_entries/10)+1

    starts = []
    ends = []

    def scrape_first_5k():
        start = 0
        starts.append(start)
        end = 5000
        ends.append(end)

    def scrape_rest():
        start = 5000
        starts.append(start)
        end = int(f'{number_of_entries}')
        ends.append(end)

    def scrape_all():
        start = 0
        starts.append(start)
        end = int(f'{number_of_entries}')
        ends.append(end)

    def let_me_pick():
        start = int(input('start from: '))
        starts.append(start)
        end = int(input('end at: '))
        ends.append(end)

    print(
        f'So, Total number of pages to scrape is: {int(number_of_entries/10)}')

    def submenu():
        print('\n')
        print('1. scrape first 5000 links')
        print(f'2. scrape rest {int(number_of_entries/10) - 5000} links')
        print(f'3. scrape all links({int(number_of_entries/10)}) links')
        print('4. Let me select, manually...')
        selection = int(input('Enter Choice: '))
        if selection == 1:
            scrape_first_5k()
        elif selection == 2:
            scrape_rest()
        elif selection == 3:
            scrape_all()
        elif selection == 4:
            let_me_pick()
        else:
            print("Invalid Choice. Inter 1-3")
            submenu()

    submenu()

    k = 1
    links = []
    for i in range(int(f'{x}')):
        links.append(
            f'https://tga-search.clients.funnelback.com/s/search.html?from-advanced=true&collection=tga-artg&fmo=on&daat=0&query_or=*&meta_i=&meta_F=&meta_A=&meta_H=&meta_bts=%21Y&meta_I=&meta_B=&meta_D=&meta_d1day=&meta_d1month=&meta_d1year=&meta_d2day=&meta_d2month=&meta_d2year=&start_rank={k}')
        k = k + 10
    print('Collecting HTML contents...Using multithreading...')

    links = links[int(f'{starts[-1]}'):int(f'{ends[-1]}')]

    data = []
    list = {}
    res_html = []

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            res_html.append(response)

    def main():
        with ThreadPoolExecutor(max_workers=10) as executor:
            with requests.Session() as session:
                print('Scraping Each Entry Started....Please Wait.')
                for link in links:
                    executor.map(fetch, [session], [link])
                executor.shutdown(wait=True)
        print('Scraping data from scraped <html> started....')
        counter = 1
        for r in res_html:
            soup = BeautifulSoup(r.content, 'lxml')
            print(counter)
            counter = counter + 1
            # print(soup)
            entry_links = soup.find(
                'div', attrs={'class': 'searchresults clearfloat'}).findAll('p')[1:-1]
            details = soup.find(
                'div', attrs={'class': 'searchresults clearfloat'}).findAll('ul')

            for entry_link, detail in zip(entry_links, details):
                n = str(entry_link.find('a')).split('href="')[
                    1].split('" title')[0].replace('amp;', '')
                s = f"https://tga-search.clients.funnelback.com{n}"
                lists = detail.findAll('li')
                artg_list = []
                product_name_list = []
                active_ingre_list = []
                sponsor_list = []
                product_info_list = []
                consumer_med_list = []
                manufacturer_list = []
                for list in lists:
                    ks = list.find('strong').string
                    if 'ARTG ID:' in ks:
                        artg_id = list.get_text().replace(list.find('strong').string, '')
                        artg_list.append(artg_id)

                    if 'Product name:' in ks:
                        product_name = list.get_text().replace(list.find('strong').string, '')
                        product_name_list.append(product_name)

                    if 'Active ingredients:' in ks:
                        active_ingre = list.get_text().replace(list.find('strong').string, '')
                        active_ingre_list.append(active_ingre)

                    if 'Sponsor:' in ks:
                        sponsor = list.get_text().replace(list.find('strong').string, '')
                        sponsor_list.append(sponsor)

                    if 'Product Information:' in ks:
                        product_info = list.find('a')['href']
                        product_info_list.append(product_info)

                    if 'Consumer Medicines Information:' in ks:
                        consumer_med = list.find('a')['href']
                        consumer_med_list.append(consumer_med)

                    if 'Manufacturer:' in ks:
                        manufacturer = list.get_text().replace(list.find('strong').string, '')
                        manufacturer_list.append(manufacturer)

                if len(artg_list) == 0:
                    artg_id = '-'
                else:
                    artg_id = artg_list[-1].strip()
                if len(product_name_list) == 0:
                    product_name = '-'
                else:
                    product_name = product_name_list[-1].strip()
                if len(active_ingre_list) == 0:
                    active_ingre = '-'
                else:
                    active_ingre = active_ingre_list[-1].strip()
                if len(sponsor_list) == 0:
                    sponsor = '-'
                else:
                    sponsor = sponsor_list[-1].strip()

                if len(product_info_list) == 0:
                    product_info = '-'
                else:
                    product_info = product_info_list[-1]
                if len(consumer_med_list) == 0:
                    consumer_med = '-'
                else:
                    consumer_med = consumer_med_list[-1]
                if len(manufacturer_list) == 0:
                    manufacturer = '-'
                else:
                    manufacturer = manufacturer_list[-1].strip()

            #     print(artg_id)
            #     print(product_name)
            #     print(active_ingre)
            #     print(sponsor)
            #     print(product_info)
            #     print(consumer_med)
            #     print(manufacturer)

                listx = {
                    'Entry Link': s,
                    'ARTG ID': artg_id,
                    'Product Name': product_name,
                    'Active Ingredients': active_ingre,
                    'Sponsor Name': sponsor,
                    'Product Information': product_info,
                    'Consumer Medicine Information': consumer_med,
                    'Manufacturer': manufacturer
                }
                data.append(listx)
        df1 = pd.DataFrame(data)
        df2 = df1.drop_duplicates(
            subset=['ARTG ID'], keep='first').reset_index(drop=True)
        df2.to_csv(
            f'tga_whole_site_{ends[-1]}.csv', encoding='utf-8', index=False)
    main()

# -----------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------


def mainmenu():
    print('\n')
    print('1. Scrape the whole site')
    print('2. Scrape site 1(each entry link)')
    print('3. Scrape site 2(each entry details)')
    print('4. exit program')
    selection = int(input('Enter Choice: '))
    if selection == 1:
        scrape_whole()
    elif selection == 2:
        scrape_all_links()
    elif selection == 3:
        scrape_each()
    elif selection == 4:
        exit()
    else:
        print("Invalid Choice. Inter 1-3")
        mainmenu()


mainmenu()

tiempo_total = time.time() - startTime
print(f"total time needed: {tiempo_total}")
