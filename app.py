from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbbookcard

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
    'https://search.shopping.naver.com/book/search?bookTabType=BEST_SELLER&catId=50005542&pageIndex=1&pageSize=40&query=%EB%B2%A0%EC%8A%A4%ED%8A%B8%EC%85%80%EB%9F%AC&sort=REL',
    headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')
trs = soup.find('ul', class_="list_book")
i = 0
for tr in trs:
    find_name = tr.find('span', class_="bookListItem_text__bglOw")
    a_tag = find_name.text
    a_img = tr.find('img')['src']
    if a_tag is not None:
        i += 1
        name = a_tag[2:]
        img = a_img

        db.bestbook.update_one({'rank': i}, {'$set': {'name': name}}, upsert=True);
        db.bestbook.update_one({'rank': i}, {'$set': {'img': img}});
    if i == 6:
        break;


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/review', methods=['POST'])
def book_review():
    title_receive = request.form['title_give']
    time_receive = request.form['time_give']
    content_receive = request.form['content_give']

    doc = {
        'title': title_receive,
        'time': time_receive,
        'content': content_receive,
    }

    db.bookreview.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


@app.route('/review', methods=['GET'])
def read_reviews():
    reviews = list(db.bookreview.find({}, {'_id': False}))
    return jsonify({'all_reviews': reviews})

@app.route('/best', methods=['GET'])
def read_book():
    books = list(db.bestbook.find({}, {'_id': False}))
    return jsonify({'all_books': books})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

