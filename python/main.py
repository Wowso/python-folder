import requests
from flask import Flask, render_template, request

base_url = "http://hn.algolia.com/api/v1"

# This URL gets the newest stories.
new = f"{base_url}/search_by_date?tags=story"

# This URL gets the most popular stories
popular = f"{base_url}/search?tags=story"


# This function makes the URL to get the detail of a storie by id.
# Heres the documentation: https://hn.algolia.com/api
def make_detail_url(id):
  return f"{base_url}/items/{id}"

Db = {}
app = Flask("DayNine")

@app.route("/")
def default():
    order_by = request.args.get('order_by')
    print(order_by)
    if order_by is None:
        order_by = "popular"
        r = requests.get(url = popular)
        Db = r.json()
    else:
        r = requests.get(url = new)
        Db = r.json()
    return render_template("index.html",posts=Db["hits"], order_by=order_by)

@app.route("/?order_by=popular")
def popular():
    order_by = request.args.get('order_by')
    r = requests.get(url = popular)
    Db = r.json()
    return render_template("index.html",posts=Db["hits"], order_by=order_by)

@app.route("/<id>")
def detail(id):
    r = requests.get(url = make_detail_url(id))
    return render_template("detail.html",posts=r.json(),comments=r.json()["children"])

app.run(host="0.0.0.0",port=9000)