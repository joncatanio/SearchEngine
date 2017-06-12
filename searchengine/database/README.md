# Database Source Files
The description and method stubs for each module is defined below. Examples can be found at the end of the file. If there is confusion on setting up the database click [here](setup/README.md).

### search_engine_db.py
This is the sole module to import when using the database endpoints. This file simply imports all of the functions from the other modules and has an initialization method to start the database connection.

#### Methods
`init_db()` - This method **must** be called before using any of the database endpoints. It establishes a connection to the database.

### db_connection.py
Holds a stateful connection to the DB accessible to all other python modules
through `db.connection.connection`. This allows all files to maintain a
connection, avoiding connecting to the database with every API call.

### query_tables.py
Endpoints for querying all the database tables.

#### Methods
`getLinks(words)` - This method returns the list of links that contain any of the given words.
- `words` - list of strings representing words contained in a search query

`getNumLinks(word = None)` - This method returns the number of links that contain the given word, or the total number of links in the database if no word is given.
- `word` - string representing the word to search for

`getFreq(word, link)` - This method returns the frequency of a given word for a given link.
- `word` - string representing the word to search for
- `link` - string representing the link to search for

`getMaxFreq(link)` - This method returns the maximum frequency achieved by any word for a given link.
- `link` - string representing the link to search for

`getInlinks(links=None)` - This method returns a dictionary in the form `{'link': ['inlinks', ...], ...}`. If the this method is called without the parameter it will return a dictionary containing all links from the `Links` table and makes the gurantee that all links will be included and at least an empty list will be returned as a value from any given key.
- `links` - list of links to find the inlinks for, each link is a key into the returned dictionary, all links will be present in the dictionary as an empty or populated list

`getNumOutlinks(links=None)` - This method returns a dictionary in the form `{'link': integer, ...}`. If the this method is called without the parameter it will return a dictionary containing all links from the `Links` table and makes the gurantee that all links will be included and at least a 0 will be returned as a value from any given key.
- `links` - list of links to find the number of outlinks for, each link is a key into the returned dictionary, all links will be present in the dictionary as a `0` or integer

### update_tables.py
Endpoints for updating all the database tables. The endpoints provided in this file are really for the web crawler and indexer.

#### Methods
`start_crawl_transaction()` - This method must be called before starting the web crawler. It begins a MySQL transaction that will modify the database while allowing users to query a static database.

`finish_crawl_transaction()` -Once crawling has finished this method must be called for updated data to be committed to the database.

`_addBaselink(baselink)` - This is a private method that simply verifies that `baselink` exists in the `Links` table, if not it adds it.
- `baselink` - string representing the current link of the crawled page

`addWords(baselink, words)` - Updates the Words and WordMeta tables.
- `baselink` - string representing the current link of the crawled page
- `words` - a list of tuples in the form `(word, position_in_text)` where word in a string and position_in_text is an integer

`addLinks(baselink, links)` - Updates the Links and Hyperlinks tables.
- `baselink` - string representing the current link of the crawled page
- `links` - a list of strings representing the links linked from baselink

`updatePageRank(links)` - Updates the Links tables with new PageRank values.
- `links` - a dictionary `{link: pageRank, ...}` of links to update

## Warnings
Sometimes the crawler hiccups and the database connection is lost, `start_crawl_transaction` and `finish_crawl_transaction` are currently just used to start and commit transactions, one may need to explicitly call `db.db_connection.connection.commit()` if they are running into too large of transactions. See the `crawler.py` code for examples.

## Examples
```python
import searchengine.database.search_engine_db as db

db.init_db()
db.start_crawl_transaction()
# Crawler goes to page 'csc.calpoly.edu' and finds the sentence 'computer science'
db.addWords('csc.calpoly.edu', [('computer', 1), ('science', 2)])
db.addLinks('csc.calpoly.edu', ['https://www.calpoly.edu', 'https://csc.calpoly.edu/faculty/'])
db.finish_crawl_transaction()
```
