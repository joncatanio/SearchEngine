import os
import wget
from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import string
import PyPDF2
import sys
import searchengine.database.search_engine_db as db
import searchengine.crawler.stack as stack
import signal

class timeout:
    def __init__(self, seconds=20, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# ignore image files and non csc.calpoly.edu urls and
# the visited links
def check_tag(tag, visited):
	return (("mailto" not in tag) and (".jpg" not in tag) and (".jpeg" not in tag) and
		(".png" not in tag) and (".gif" not in tag) and (".exe" not in tag) and ("csc.calpoly.edu" in tag) and
		(tag not in visited))

# ignore image files and non csc.calpoly.edu urls but
# don't worry about visited links
def check_tag_without_visited(tag):
	return (("mailto" not in tag) and (".jpg" not in tag) and (".jpeg" not in tag) and
		(".png" not in tag) and (".gif" not in tag) and (".exe" not in tag) and ("csc.calpoly.edu" in tag))

# Input = [word1, word2, ...]
# Updates database returns nothing
def index_one_file(baselink, term_list):
   # List of tuples (word, position)
	word_list = []

	for index, word in enumerate(term_list):
		if len(word) == 0:
			continue

		word_list.append((word, index))

	db.addWords(baselink, word_list)

# extracts text from pdf file
def read_pdf_file(url):
	pdf_file_obj = open(url, 'rb')
	pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
	num_pages = pdf_reader.numPages
	total_text = ""

	for page_num in range(num_pages):
		page_obj = pdf_reader.getPage(0)
		total_text += page_obj.extractText() + " "

	return total_text

def crawl():
	urls = [url.split("\n")[0] for url in stack.get_stack()] # stack of urls to scrape

	# The first url we're crawling needs to be marked as already visited.
	# Otherwise if the page contained a link to itself, we'd crawl it twice.
	visited = ["https://csc.calpoly.edu/"]

	exclude = set(string.punctuation)
	url_map = {}

	html_text = ""

	max_links = 0

	while len(urls) > 0:
		max_links += 1
		print("   Link: \033[36m\'" + str(urls[0]) + "\'\033[0m")

		# set the text to parse by beautiful soup to that of
		# a pdf if found, or just the page itself
		if ".pdf" in urls[0]:
			try:
				print("\033[32m", end=" ")
				file_name = wget.download(urls[0])
				html_text = read_pdf_file(urls[0].split("/")[-1])
				os.remove(urls[0].split("/")[-1])
				print("\033[0m")
			except Exception as e:
				print("\033[33m" + str(e) + "\033[0m")
				urls.pop(0)
				continue
		else:
			try:
				html_text = urlopen(urls[0], timeout=20).read()
			except Exception as e:
				print("\033[33m" + str(e) + "\033[0m")
				urls.pop(0)
				continue

		# make sure the page parsing takes 20 seconds max, else
		# skip the page
		try:
			with timeout(seconds=20):
				soup = BeautifulSoup(html_text, "html.parser")

				# kill all script and style elements
				for script in soup(["script", "style"]):
				    script.extract()    # rip it out

				# get text
				text = soup.get_text()

				# break into lines and remove leading and trailing space on each
				lines = (line.strip() for line in text.splitlines())
				# break multi-headlines into a line each
				chunks = (phrase.strip().lower() for line in lines for phrase in line.split("  "))
				# drop blank lines
				text = '\n'.join(chunk for chunk in chunks if chunk)
				# join the text so it is a single string
				text = ''.join(ch for ch in text if ch not in exclude)
				# remove some special characters found to be prevalent
				text = text.replace('\n', ' ').replace(u'\xa0', u' ')

				# remove characters that are not alphanumeric or . or _ or -
				for ch in text:
					if not ch.isalnum() or ch != '.' or ch != '_' or ch != '-':
						text.replace(ch, '')

				term_list = text.split(' ')

		      	# Update database
				index_one_file(urls[0], term_list)

				url_top = urls[0]

				links_to_add = []
				url_map[url_top] = []

				urls.pop(0)

				print("Visited:", max_links, "-- URL Stack:", len(urls))

				for tag in soup.findAll('a', href=True):
					tag['href'] = urljoin("https://csc.calpoly.edu/", tag['href'])

					# check if the url is valid not worrying about visited,
					# this is to get the mapping from a link to get
					if check_tag_without_visited(tag['href']):
						links_to_add.append(tag['href'])
					
				if links_to_add:
					db.addLinks(url_top, links_to_add)

				for tag in soup.findAll('a', href=True):
					tag['href'] = urljoin("https://csc.calpoly.edu/", tag['href'])

					# check if the url is valid and has not been visited
					if check_tag(tag['href'], visited):
						urls.append(tag['href'])
						visited.append(tag['href'])
		except Exception as e:
			print("\033[33m" + str(e) + "\033[0m")
			urls.pop(0)
			continue

	return visited

def main():
	db.init_db()
	db.start_crawl_transaction()
	crawl()
	print('\n-- Crawl Complete --')
	print('Finishing Database Transaction')
	db.finish_crawl_transaction()

if __name__ == "__main__":
	main()
