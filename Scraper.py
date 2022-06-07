import requests, time, random
from bs4 import BeautifulSoup as bs

#Required INPUTS
SHOP_URL_Slug = "TMichaelStudio"
PAGES = 487


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = str(bs(requests.get(url).content, 'html.parser'))
    #print(soup)
    proxies = []
    data = soup.split("Updated at")
    #print(data)
    table = data[1].split("</textarea>")[0].split("\n")
    table = [i for i in table if i]
    print(table)
    table.pop(0)
    table.pop(0)

    for row in table:
        row = row.strip().split(":")
        ip = row[0]
        port = row[1]
        host = f"{ip}:{port}"
        proxies.append(host)

    return proxies

def get_session(proxies):
    # construct an HTTP session
    session = requests.Session()
    # choose one random proxy
    proxy = random.choice(proxies)
    session.proxies = {"http": proxy, "https": proxy}
    return session

def tryPagePull(pagenum, proxies):
    global SHOP_URL_Slug
    s = get_session(proxies)
    
    data = s.get('https://www.etsy.com/shop/' + SHOP_URL_Slug + '/sold?ref=pagination&page=' + str(pagenum + 1), timeout=1.5).content
    if data != None:
        return data
    else:
        tryPagePull(pagenum, proxies) #recures for the win

def cleanproxies(proxies):
    for i in range(len(proxies)):
            # construct an HTTP session
            session = requests.Session()
            # choose one random proxy
            proxy = proxies[i]
            session.proxies = {"http": proxy, "https": proxy}
            s = get_session(proxies)
            try:
                print("Request page with IP:", s.get("http://icanhazip.com", timeout=1.5).text.strip())
            except Exception as e:
                proxies.remove(proxy)
                print("Removed proxy:", proxy)

    print(len(proxies))
    return proxies

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

items = []
items_count = []
total_items = 0

proxies = get_free_proxies()
proxies = cleanproxies(proxies)

for i in range(PAGES):
    #page = str(requests.get('https://www.etsy.com/shop/' + SHOP_URL_Slug + '/sold?ref=pagination&page=' + str(i + 1),
    #                    headers=headers, allow_redirects=True).content)
    #print(page)
    page = tryPagePull(i, proxies)
    print(page)

    page = page.split("h3") #seperate by the item name header
    for item in page:
        if ' class="wt-text-caption v2-listing-card__title' in item:
            #print(item)
            aftertag = item.split('>')
            #print(aftertag)
            inbetween = aftertag[1].split('<')
            title = inbetween[0].replace(r'\n', '').strip()
            #print(title)

            if title not in items:
                items.append(title)
                items_count.append(1)
                total_items += 1

            else:
                items_count[items.index(title)] += 1
                total_items += 1

    print(str(round(i/PAGES*100, 2)) +  "% complete    " + str(round(((PAGES - i) * 11 + ((PAGES / 22  - i /22)* 160)) / 60,2)) + " minutes left   " + str(total_items) + " items found")
    
    time.sleep(random.randint(7,14))
    #break to avoid hitting the rate limit ban
    if i % 22 == 0 and i != 0:
        x = random.randint(120, 200)
        print("Sleeping for " + str(x) + " seconds")
        time.sleep(x) #take a timeout before ratelimit ban

#magical sorting
yx = zip(items_count, items)
yx = sorted(yx, key=lambda x: x[0], reverse=True)
items_count, items = zip(*yx)


with open("Totals.txt", "w") as f:
    for i in range(len(items)):
        f.write(items[i] + ": " + str(items_count[i]) + "\n")

    f.close()