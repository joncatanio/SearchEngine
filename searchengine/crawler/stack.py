import sys
from searchengine.crawler.config import key, cse_id
from googleapiclient.discovery import build

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def update_stack(query, num_pages):
    my_api_key = key
    my_cse_id = cse_id
    urls = [url.split("\n")[0] for url in get_stack()]

    i = 0
    try:
        while i < num_pages:
            results = google_search(query, my_api_key, my_cse_id, num=10, start=1+(i*10))
            for result in results:
                urls.append(result['link'])
            i += 1
    except:
        pass

    save_stack(set(urls))

def save_stack(arr):
    f = open('initial_stack.txt', 'w')
    for link in arr:
        f.write("{}\n".format(link))
    f.close()

def get_stack():
    f = open('initial_stack.txt', 'r')
    links = f.readlines()
    f.close()
    return links


if __name__ == "__main__":
    query = sys.argv[1] # site:csc.calpoly.edu/~
    num = int(sys.argv[2])
    num_pages = 1 if num is None else num
    update_stack(query, num_pages)
    
