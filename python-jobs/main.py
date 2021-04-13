import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect,send_file
from save import save_to_file

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

"""
https://stackoverflow.com/jobs?r=true&q=python
https://weworkremotely.com/remote-jobs/search?term=python
https://remoteok.io/remote-dev+python-jobs
"""

rule = ["div","number","title","link","company"]

rules = [
    {"div":"js-search-results",
    "post":"js-result",
    "number":"seo-header",
    "title":"stretched-link",
    "link":"stretched-link",
    "company":"fc-black-700",
    "pages":"s-pagination"
    },
    {
        "div":"jobs-container",
        "post":"feature",
        "title":"title"
    },
    {
        "table":"jobsboard",   #table id 
        "tr":"job",     #class name
        "td":"company_and_position", #class name
        "title":"title",    #itemprop name
        "link":"url",   #itemprop name
        "company":"name"    #itemprop name
    }
]
db = {}

def new_url(arg):
    new_urls = [f"https://stackoverflow.com/jobs?r=true&q={arg}",
    f"https://weworkremotely.com/remote-jobs/search?term={arg}",
    f"https://remoteok.io/remote-dev+{arg}-jobs"]
    return new_urls

def crawling(url, num):
    content = []
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text,"html.parser")

    if num == 0:    #first url stackoverflow
        number = int(soup.find("div",{"class":rules[num]['number']}).find("span").text.replace(" ","").replace("jobs",""))
        page_max = int(soup.find("div",{"class":rules[num]["pages"]}).find("a")['title'][-1])
        posts = soup.find_all("div",{"class":rules[num]["post"]})
    elif num == 1:  #second url weworkremotely
        page_max = None
        div = soup.find("div",{"class":rules[num]["div"]})
        posts = div.find_all("li",class_=lambda x: x not in "view-all")
    elif num == 2:  #third url remoteok
        page_max = None
        table = soup.find("table",{"id":rules[num]["table"]})
        trs = table.find_all("tr",{"class":rules[num]["tr"]})

    if page_max is not None:
        for page in range(page_max):

            if content is not None:
                html = requests.get(url+f"&pg={page+1}", headers=headers)
                soup = BeautifulSoup(html.text,"html.parser")
                posts = soup.find_all("div",{"class":rules[num]["post"]})

            for post in posts:
                title = post.find("a",{"class":rules[num]["title"]}).text
                link = "https://stackoverflow.com"+post.find("a",{"class":rules[num]["link"]})['href']
                company = post.find("h3",{"class":rules[num]["company"]}).find("span",{"class":""}).text.replace(" ","").replace("\r","").replace("\n","")
                content += [{"title":title,"company":company,"link":link}]
    elif num == 1:
        for post in posts:
            a = post.find("span",{"class":"title"}).parent
            title = a.find("span",{"class":"title"}).text
            company = a.find("span").text
            link = "https://weworkremotely.com"+a['href']
            content += [{"title":title,"company":company,"link":link}]
    elif num == 2:
        for tr in trs:
            td = tr.find("td",{"class":"company_and_position"})
            title = td.find("h2",itemprop=rules[num]["title"]).text
            company = td.find("h3",itemprop=rules[num]["company"]).text
            link = "https://remoteok.io/"+td.find("a",itemprop=rules[num]["link"])['href']
            content += [{"title":title,"company":company,"link":link}]

    return content

app = Flask("DayThirteen")

@app.route("/")
def home():
    
    return render_template("home.html")

@app.route("/read")
def read():
    jobs=[]
    arg = request.args.get("term")
    if arg:
        
        arg = arg.lower()
        urls = new_url(arg)
        
        fromDb = db.get(arg)
        if fromDb:
            jobs = fromDb
        else:
            for count in range(3):
                jobs += crawling(urls[count],count)
            db[arg] = jobs
    else:
        return redirect("/")
    return render_template("read.html",arg= arg, jobs= jobs, jobs_count= len(jobs),download=f"/{arg}.csv")

@app.route("/export")
def export():
    try:
        arg = request.args.get('term')
        if not arg:
            raise Exception()
        arg = arg.lower()
        jobs = db.get(arg)
        if not jobs:
            raise Exception()
        save_to_file(arg,jobs)
        return send_file(
            f"{arg}.csv",
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename=f"{arg}.csv")
    except:
        return redirect("/")

app.run(host="0.0.0.0", port=9000)