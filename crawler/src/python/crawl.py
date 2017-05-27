import os
import wget
from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import string
import PyPDF2

def check_tag(tag, visited):
	return (("mailto" not in tag) and (".jpg" not in tag) and (".jpeg" not in tag) and (".png" not in tag) and (".gif" not in tag) and ("csc.calpoly.edu" in tag) and (tag not in visited))

def check_tag_without_visited(tag):
	return (("mailto" not in tag) and (".jpg" not in tag) and (".jpeg" not in tag) and (".png" not in tag) and (".gif" not in tag) and ("csc.calpoly.edu" in tag))

#input = [word1, word2, ...]
#output = {word1: [pos1, pos2], word2: [pos2, pos434], ...}
def index_one_file(term_list):
	file_index = {}
	
	for index, word in enumerate(term_list):
		if len(word) == 0:
			continue

		if word in file_index.keys():
			file_index[word].append(index)
		else:
			file_index[word] = [index]
	
	return file_index

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
	url = "https://csc.calpoly.edu/"

	urls = [url] # stack of urls to scrape
	visited = [url] # historic record of urls
	exclude = set(string.punctuation)
	url_map = {}

	html_text = ""

	while len(urls) > 0:
		print(urls[0])

		if ".pdf" in urls[0]:
			try:
				file_name = wget.download(urls[0])
				html_text = read_pdf_file(urls[0].split("/")[-1])
				os.remove(urls[0].split("/")[-1])
			except Exception as e:
				print(str(e))
				urls.pop(0)
				continue
		else:
			try:
				html_text = urlopen(urls[0]).read()
			except Exception as e:
				print(str(e))
				urls.pop(0)
				continue

		soup = BeautifulSoup(html_text, "lxml")

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

		text = ''.join(ch for ch in text if ch not in exclude)

		text = text.replace('\n', ' ').replace('\r', '').replace(u'\xa0', u' ')

		term_list = text.split(' ')

		url_top = urls[0]

		url_map[url_top] = []

		urls.pop(0)

		print("num urls:", len(urls))

		for tag in soup.findAll('a', href=True):
			tag['href'] = urljoin(url, tag['href'])

			if check_tag_without_visited(tag['href']):
				url_map[url_top].append(tag['href'])

		for tag in soup.findAll('a', href=True):
			tag['href'] = urljoin(url, tag['href'])
			
			if check_tag(tag['href'], visited):
				urls.append(tag['href'])
				visited.append(tag['href'])

	print(visited)

def main():
	crawl()

if __name__ == "__main__":
	main()
