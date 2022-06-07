import requests, time, random


#Required INPUTS
SHOP_URL_Slug = "TMichaelStudio"
PAGES = 487


headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

items = []
items_count = []
total_items = 0

for i in range(PAGES):
    page = str(requests.get('https://www.etsy.com/shop/' + SHOP_URL_Slug + '/sold?ref=pagination&page=' + str(i + 1),
                        headers=headers, allow_redirects=True).content)
    #print(page)
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

    print(str(round(i/PAGES*100, 2)) +  "% complete    " + str(round(((PAGES - i) * 110 + ((PAGES / 22  - i /22)* 160)) / 60,2)) + " minutes left   " + str(total_items) + " items found")
    
    time.sleep(random.randint(70,140))
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