from flask import Flask, request, Response
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from algorithms import TF_IDF
import searchengine.database.search_engine_db as db

app = Flask(__name__)

@app.route('/search/<query>/<pr_flag>/', methods = ['GET'])
def search(query, pr_flag):
    start = datetime.now()
    links = TF_IDF.findRelevantLinks(query, 10, pr_flag)

    results = []

    for link in links:
        title = None
        des = None
        
        page = requests.request('GET', link, timeout=0.25, verify=False)
        if page.encoding is not None:
            soup = BeautifulSoup(page.text, "html.parser")
            des = soup.find('meta', {'name':'Description'})
            if des is None:
                des = soup.find('meta', {'name':'description'})
            if des and des['content'] and len(des['content']) >= 30:
                des = des['content']
            else:
                body = soup.find('body')
                if body is not None:
                    all_text = body.get_text().lower()
                    query_index = all_text.find(query.lower())
                    des = " ".join(all_text[query_index - 120: query_index + 120].split(" ")[1:-1])
            title = soup.find('title')

        results.append({ 
            'title': title.text if title is not None else link, 
            'link': link,
            'des': des if des is not None else '- - -',
        })

    elapsed = datetime.now() - start
    content = json.dumps({
        'results': results,
        'meta': {
            'num_results': len(results),
            'seconds_elapsed': elapsed.total_seconds()
        }
    })

    resp = Response(content, status=200, mimetype='application/json')
        #resp = Response("ERROR", status=500, mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = "*"
    return resp


if __name__ == '__main__':
    app.debug = True
    db.init_db()
    app.run()
