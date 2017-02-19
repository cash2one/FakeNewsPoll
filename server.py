#!/usr/bin/env python3
from flask import *
import sqlite3
import requests
import json

app = Flask(__name__)

with open("config.json") as data_file:
    config = json.load(data_file)

def initDb():
    db = sqlite3.connect("news.db")
    db.execute("""CREATE TABLE IF NOT EXISTS news(
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT,
    author TEXT,
    description TEXT,
    url TEXT,
    urlToImage TEXT,
    publishedAt TEXT,
    voteTrue INTEGER,
    voteFalse INTEGER,
    UNIQUE (title)
    )""")
    db.close()

def getNews(source):
    url="https://newsapi.org/v1/articles?source=" + source  + "&sortBy=top&apiKey=" + config["API_KEY"]
    response = requests.get(url)
    newsData = json.loads(response.text)
    return newsData

def loadNewsToDb(news):
    db = sqlite3.connect("news.db")
    cursor = db.cursor()
    for article in news["articles"]:
        cursor.execute("INSERT OR IGNORE INTO news (title, author, description, url, urlToImage, publishedAt) VALUES (?, ?, ?, ?, ?, ?)", [article["title"], article["author"], article["description"], article["url"], article["urlToImage"], article["publishedAt"]] )
    db.commit()
    db.close()

@app.route("/")
def main():
    return render_template('index.html', news=getNews("the-washington-post"))

if __name__ == "__main__":
    initDb()
    print(getNews("the-washington-post"))
    loadNewsToDb(getNews("the-washington-post"))
    app.run(debug=True, host="0.0.0.0")
