from flask import Flask, request, Response
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

@app.route('/search/<query>/', methods = ['GET'])
def search(query):
    start = datetime.now()

    try:
        search_results = json.dumps([])
        end = datetime.now()
        elapsed = end - start

        results = {
            'results':[
                { 
                    'title': 'Cal Poly, San Luis Obispo', 
                    'link': 'http://www.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly CSC Department',
                    'link': 'http://www.csc.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly, San Luis Obispo', 
                    'link': 'http://www.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly CSC Department',
                    'link': 'http://www.csc.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly, San Luis Obispo', 
                    'link': 'http://www.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly CSC Department',
                    'link': 'http://www.csc.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly, San Luis Obispo', 
                    'link': 'http://www.calpoly.edu'
                },
                { 
                    'title': 'Cal Poly CSC Department',
                    'link': 'http://www.csc.calpoly.edu'
                },
            ],
            'meta': {
                'num_results': len(search_results),
                'seconds_elapsed': elapsed.total_seconds()
            }
        }

        for index, result in enumerate(results['results']):
            page = requests.get(result['link']).text
            soup = BeautifulSoup(page, 'lxml')
            des = soup.find('meta', {'name':'Description'})
            if des is None:
                des = soup.find('meta', {'name':'description'})
            if des and len(des) >= 30:
                des = des['content']
            else:
                all_text = soup.find('body').get_text().lower()
                print all_text
                query_index = all_text.find(query.lower())
                des = " ".join(all_text[query_index - 120: query_index + 120].split(" ")[1:-1])

            results['results'][index]['des'] = des

        results = json.dumps(results)

        resp = Response(results, status=200, mimetype='application/json')
    except:
        resp = Response("ERROR", status=500, mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = "*"
    return resp


if __name__ == '__main__':
    app.debug = True
    app.run()
