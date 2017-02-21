#!/usr/bin/env python3
from flask import *
import sqlite3
import requests
import json

app = Flask(__name__)

votes = {}

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
    voteTrue INTEGER DEFAULT 0,
    voteFalse INTEGER DEFAULT 0,
    UNIQUE (title)
    );""")

    db.execute("""
    CREATE TABLE IF NOT EXISTS ip(
    ip TEXT PRIMARY KEY
    )
    """)

    db.close()

def getNews(source):
    url="https://newsapi.org/v1/articles?source=" + source  + "&sortBy=top&apiKey=" + config["API_KEY"]
    response = requests.get(url)
    newsData = json.loads(response.text)
    return newsData

def setNewsToDb(news):
    db = sqlite3.connect("news.db")
    cursor = db.cursor()
    for article in news["articles"]:
        cursor.execute("INSERT OR IGNORE INTO news (title, author, description, url, urlToImage, publishedAt) VALUES (?, ?, ?, ?, ?, ?)", [article["title"], article["author"], article["description"], article["url"], article["urlToImage"], article["publishedAt"]] )
        #Get the id's of newly created entries
        for row in cursor.execute("SELECT id FROM news WHERE url ='" + article["url"] + "'"):
            try:
                cursor.execute("ALTER TABLE ip ADD COLUMN n" + str(row[0]) + " INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                print("Column already exists")

    db.commit()
    db.close()

def loadNewsFromDb():
    db = sqlite3.connect("news.db")
    cursor = db.cursor()
    data = []
    for row in cursor.execute("SELECT * FROM news ORDER BY voteTrue + voteFalse DESC"):
        data.append({"id": row[0], "title": row[1], "author": row[2], "description": row[3], "url": row[4], "urlToImage": row[5], "publishedAt": row[6], "voteTrue": row[7], "voteFalse": row[8]})
    db.close()
    return data

@app.route("/vote/", methods=["POST"])
def vote():
    db = sqlite3.connect("news.db")
    cursor = db.cursor()

    id = request.json["id"]
    column = "vote" + request.json["opinion"]

    ip = request.environ["REMOTE_ADDR"]

    cursor.execute("INSERT OR IGNORE INTO ip (ip) VALUES (?)", [ip])

    cursor.execute("SELECT n" + str(id) + " FROM ip WHERE ip='" + ip + "'")
    alreadyVoted = cursor.fetchone()[0]
    if not alreadyVoted:
        cursor.execute("UPDATE news SET " + column + " = " + column + " + 1 WHERE id = " + str(id))
        cursor.execute("UPDATE ip SET n" + str(id) + " = 1 WHERE ip = '" + ip + "'")

    db.commit()

    db.close()
    return "NULL"

@app.route("/")
def main():
    return render_template('index.html', news=loadNewsFromDb())

if __name__ == "__main__":
    initDb()
    setNewsToDb(getNews("google-news"))
    app.run(debug=True, host="0.0.0.0")
