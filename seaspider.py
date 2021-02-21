import bs4
import re
import requests
import sys
import time
from tqdm import tqdm

def check_url(url):
    url_check_result = {}
    r = requests.get(url, headers={'User-Agent': 'Sea'})
    url_check_result['status_code'] = r.status_code
    print('\n', url_check_result['status_code'], ' ', url)
    return url_check_result

def crawl_target(target_url):
    crawl_result = {}
    r = requests.get(target_url, headers={'User-Agent': 'Sea'})
    crawl_result['status_code'] = r.status_code
    crawl_result['text'] = r.text
    return crawl_result

def main():
    """Crawl a given starting URL, collect all links from its HTML, and then
    recursively crawl those links, while avoiding duplicate crawls."""
    crawl_queue = {}

    if len(sys.argv) < 2:
        print('[ERROR] No target URL supplied. Please provide a URL for seaspider to crawl.')
    else:
        target_url = sys.argv[1]
        crawl_result = crawl_target(target_url)
        print(crawl_result['status_code'], ' ', target_url)
        soup = bs4.BeautifulSoup(crawl_result['text'], features='html.parser')
        pattern = '^https?://'

        # Apply domain restriction
        if len(sys.argv) >= 3:
            pattern += sys.argv[2]

        links = soup.findAll('a', attrs={'href': re.compile(pattern)})
        print(len(links), ' links detected')

        for link in links:
            url = link.get('href')
            
            if not url in crawl_queue.keys():
                crawl_queue[url] = {}

        for key in crawl_queue.keys():
            print(key)

        progress_bar_label = 'Crawling ' + str(len(crawl_queue)) + ' URLs'

        for key in tqdm(crawl_queue.keys(), desc=progress_bar_label):
            crawl_queue[key]['crawl_result'] = check_url(key)
            time.sleep(0.1)
            
main()
