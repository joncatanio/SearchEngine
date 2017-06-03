## Setup for the searchengine package
In order to use the `searchengine` package the `PYTHONPATH` environment variable
needs to be updated.

#### Adding path to .bash_profile
- `export PYTHONPATH=${PYTHONPATH}:<absolute_path/to/SearchEngine/>`

#### Exporting a temporary path change type into the terminal
- `$ export PYTHONPATH=${PYTHONPATH}:<absolute_path/to/SearchEngine/>`


## Crawler Usage
Navigate to the `crawler` directory before following the directions below.

### Running the crawler
`python3 crawl.py`

### Updating the crawler's initial URL stack
Our crawler starts out with a url stack to increase the chances of reaching as many pages not reachable from the Cal Poly homepage. The script that will update the stack is called `stack.py`. 

#### Setup
`stack.py` uses a custom Google search engine in order to retrieve search results. In order to communicate with Google's API, an API key and a search engine id are required.

Create a file called `config.py` within the `crawler ` directory. Inside, paste:
```
key = '<api key goes here>'
cse_id = '<search engine id goes here>'
```
Replace the bracketed text with the credentials provided by [@alexgreene](https://github.com/alexgreene). Do not leave the brackets, but do leave the quotation marks.

To add links to the stack, run `python3 stack.py site:csc.calpoly.edu/~ 1` where `site:csc.calpoly.edu/~` would be replaced with your search term and `1` would be the number of pages of Google search results to pull urls from. 

*Note: We are limited to 100 total pages per day, with each page returning 10 results.*
