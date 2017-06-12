# Cal Poly Search Engine For CSC Domain
Authors: Jon Catanio, Tyler Dahl, Alex Greene, Lohit Vankineni, & Shubham Kahal

## Setup for the searchengine package
In order to use the `searchengine` package the `PYTHONPATH` environment variable
needs to be updated.

#### Adding path to .bash_profile
- `export PYTHONPATH=${PYTHONPATH}:<absolute_path/to/SearchEngine/>`

#### Exporting a temporary path change type into the terminal
- `$ export PYTHONPATH=${PYTHONPATH}:<absolute_path/to/SearchEngine/>`

#### Package Requirements
Please see the `requirements.txt` file in the root directory. You should be able to run the command `pip3 install -r requirements.txt` to install them pretty easily.

## Setting up the Database
Please refer to the README located [here](searchengine/database/setup/README.md) to learn how to set up the MySQL database.
A testing database that has pre-crawled information with PageRanks assigned can be found [here](searchengine/test/test_db.gz).

## Running the Server
- In the `searchengine` directory there is a Python3 file titled `server.py` simply run `python3 server.py` and a Flask server will be running on localhost port 5000.
- Navigate to the `frontend` directory and open the `index.html` file in your web browser of choice (we know Chrome and Safari work if you have trouble with this).
- Enter search queries and wait shortly for results. (There will be no results if the database is not populated).

## Crawler Usage
Navigate to the `crawler` directory before following the directions below.

### Running the crawler
`python3 crawl.py`

### Updating the crawler's initial URL stack
Our crawler starts out with a url stack to increase the chances of reaching as many pages not reachable from the Cal Poly homepage. The script that will update the stack is called `stack.py`. 

#### Setup
`stack.py` uses a custom Google search engine in order to retrieve search results. In order to communicate with Google's API, an API key and a search engine id are required.

Run `pip install google-api-python-client`

Create a file called `config.py` within the `crawler ` directory. Inside, paste:
```
key = '<api key goes here>'
cse_id = '<search engine id goes here>'
```
Replace the bracketed text with the credentials provided by [@alexgreene](https://github.com/alexgreene). Do not leave the brackets, but do leave the quotation marks.

To add links to the stack, run `python3 stack.py site:csc.calpoly.edu/~ 1` where `site:csc.calpoly.edu/~` would be replaced with your search term and `1` would be the number of pages of Google search results to pull urls from. 

*Note: We are limited to 100 total pages per day, with each page returning 10 results.*

## PageRank
To assign a PageRank to each link simply navigate to the `searchengine/algorithms` directory and run `python3 PageRank.py`, this will begin assigning ranks to each link.

*Note: The database needs to be setup and populated before running the PageRank file*

## Other Information
For other information please visit some of the other directories in the package, most have their own README files associated with them.

The website can be found [here](http://frank.ored.calpoly.edu/~kahal466/) which includes information that was found in our final report.

The live demo can be found on our [AWS EC2 instance](http://ec2-54-183-201-81.us-west-1.compute.amazonaws.com/). This will only be up for a short period of time as we do not want to pay for it to stay up. If you would like to see the live version please contact me at joncatanio [at] gmail [dot] com. The live version is using a precrawled database and will be out of date as new pages get added to the `csc.calpoly.edu` domain since we are not constantly crawling on that instance.

If you are experiencing some slowness in getting results that is simply due to us using [beautiful soup](https://www.crummy.com/software/BeautifulSoup/) to fetch relevant link titles and descriptions after the database API returns links. We realize this was not the best design decision and could have been remedied by storing that data in the `Links` table after each crawl. Other than that it operates as expected and the results should be very relevant! :)
