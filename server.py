from flask import Flask, request, Response
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

import sys
sys.path.insert(0, './algorithms')

import TF_IDF

app = Flask(__name__)

@app.route('/search/<query>/', methods = ['GET'])
def search(query):
    start = datetime.now()

    try:
        links = TF_IDF.findRelevantLinks(query, 10)
        elapsed = datetime.now() - start

        results = []

        for link in links:
            page = requests.get(link).text
            soup = BeautifulSoup(page, 'lxml')
            des = soup.find('meta', {'name':'Description'})
            if des is None:
                des = soup.find('meta', {'name':'description'})

            if des and len(des) >= 30:
                des = des['content']
            else:
                all_text = soup.find('body').get_text().lower()
                query_index = all_text.find(query.lower())
                des = " ".join(all_text[query_index - 120: query_index + 120].split(" ")[1:-1])

            results.append({ 
                'title': soup.find('title').text, 
                'link': link,
                'des': des,
            })

        content = json.dumps({
            'results': results,
            'meta': {
                'num_results': len(results),
                'seconds_elapsed': elapsed.total_seconds()
            }
        })

        resp = Response(content, status=200, mimetype='application/json')
    except:
        resp = Response("ERROR", status=500, mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = "*"
    return resp


if __name__ == '__main__':
    app.debug = True
    app.run()