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
    voteFalse INTEGER
    )""")

def getNews():
    url="https://newsapi.org/v1/articles?source=the-washington-post&sortBy=top&apiKey=" + config["API_KEY"]
    response = requests.get(url)
    newsData = json.loads(response.text)
    return newsData

@app.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    initDb()
    print(getNews())
    app.run(debug=True, host="0.0.0.0")
