import requests, time, random, os

#SERVER implementation
#can run async all time to handle multiple requests
#designed to import jobs from txt file upload
#job can be viewed in uploaded job file for webview

#Start it with crontab settings


def scrapepage(url, indicie):

    try:
        #doublecheck the url is clean
        if 'https://www.etsy.com/shop/' in url and '/sold' in url and '?ref=pagination&page=' not in url:
            print("URL is clean")
        else:
            print("URL is not clean")
            return False, 'URL Error'

        #look im a real web brower
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

        #vars to tallie products in
        items = []
        items_count = []
        total_items = 0

        #select page from etsy magic pagination. Thats some real disney magic right there
        pagimagion = "?ref=pagination&page=" + str(indicie)

        #finnaly actually get the page
        page = str(requests.get(url + pagimagion, headers=headers, allow_redirects=True).content)

        #cleanup page for parsing
        page = page.split("h3") #seperate by the item name header
        for item in page:
            if ' class="wt-text-caption v2-listing-card__title' in item: #check if in right place
                aftertag = item.split('>')#trim everything before the title
                inbetween = aftertag[1].split('<')#trim everything after the title
                title = inbetween[0].replace(r'\n', '').strip()#get stripped title minues weird whitespace

                #new item found so append
                if title not in items:
                    items.append(title)
                    items_count.append(1)
                    total_items += 1

                else:#item already exists so just add to count
                    items_count[items.index(title)] += 1
                    total_items += 1

        return True, [items, items_count, total_items] #return success and data
    except: #if any error occurs  #requests is often angry
        print("Error")
        return False, 'Error- Job Failed'

def exportJobData(jobloc,url, start, end, status, progress, data): #export job data to txt file for web view
    try:
        with open(jobloc, "w") as f:
            f.write("URL;" + url + "\n") #u understand \n right?
            f.write("Start Page;" + str(start) + "\n")
            f.write("End Page;" + str(end) + "\n")
            f.write("Status;" + status + "\n")
            f.write("Progress;" + str(progress) + "\n")
            for i in data:
                f.write(i + "\n")
            f.close()
            return True
    except:
        print("Unable to export job data to web") #oh lawd not again
        return False

def Server(jobsdir): #main server function (a loop)
    while(True):#see

        #check for jobs
        jobs = []
        for i in os.listdir(jobsdir):
            if i.endswith(".txt"):
                jobs.append(i)
                os.chmod(jobsdir+i, 0o755) #php is a facist scumbag #just let me write to it

        #process each job
        for job in jobs:

            #open the job data file and parse contents
            with open(jobsdir + job, "r") as f:
                lines = f.readlines()
                lines = [x.strip() for x in lines]
                lines = [x for x in lines if x]
                f.close()

            #set all retived data into variables
            notnew = False
            for line in lines:
                line = line.split(";")
                if line[0] == "URL":
                    url = line[1]
                elif line[0] == "Start Page":
                    start = int(line[1])
                elif line[0] == "End Page":
                    end = int(line[1])
                elif line[0] == "Status":
                    status = line[1]
                    if status == "Complete" or status == "Failed":
                        notnew = True

            #found a new job
            #start it
            if notnew == False:
                #start job and update status
                print("Job started")
                status = "Running"

                #items to tallie
                items = []
                items_count = []
                total_items = 0

                #how did it go? If bad don't try to export data
                sucess = True

                #loop for x pages
                for i in range(start, end + 1):
                    print("Scraping page " + str(i))

                    #scrape page
                    status, data = scrapepage(url, i)

                    #if sucessful scrape
                    if status == True:

                        #add data to tallies
                        new_items = data[0]
                        new_items_count = data[1]
                        total_items += data[2]

                        for i in range(len(new_items)):
                            if new_items[i] not in items:
                                items.append(new_items[i])
                                items_count.append(new_items_count[i])
                            else:
                                items_count[items.index(new_items[i])] += new_items_count[i]

                        #update progress percentage and export an update to webview
                        progress = str(round((i - start + 1) / (end - start + 1) * 100, 2)) + "% Page: " + str(i)
                        exportJobData(jobsdir+job,url, start, end, "Running", progress, [""])

                        #wait in between requests
                        if i < end:
                            time.sleep(random.randint(35,60))

                    #if unsucessful scrape end it all and say so in job file
                    elif status == False:
                        print("Job failed")
                        exportJobData(jobsdir+job, url, start, end, "Failed", data, [""])
                        sucess = False
                        break
                    else:
                        print("Error")
                        exportJobData(jobsdir+job, url, start, end, "Failed", data, [""])
                        sucess = False
                        break

                #when done
                if sucess == True: #all went well so export data
                    print("Job complete")

                    #sort items
                    yx = zip(items_count, items)
                    yx = sorted(yx, key=lambda x: x[0], reverse=True)
                    items_count, items = zip(*yx)

                    #export data
                    export_level_data = []
                    for i in range(len(items)):
                        export_level_data.append(items[i] + ", " + str(items_count[i]))
                    exportJobData(jobsdir+job, url, start, end, "Complete", "100%", export_level_data)
                    continue

            #when looping through jobs ignore already processed jobs
            if status == "Complete" or status == "Failed":
                continue

        #wait for new jobs
        time.sleep(20)


#start server and look a the dir where jobs are uploaded
Server('/var/www/html/scraper-jobs/uploads/')