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

def crawl_from_origin(origin_url, domain_restriction=''):
    """Crawl a given starting URL, collect all links from its HTML, and then
    recursively crawl those links, while avoiding duplicate crawls."""
    crawl_queue = {}
    crawl_result = crawl_target(origin_url)
    print(crawl_result['status_code'], ' ', origin_url, ' ORIGIN')
    soup = bs4.BeautifulSoup(crawl_result['text'], features='html.parser')
    pattern = '^https?://' + domain_restriction
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

def crawl_target(target_url):
    crawl_result = {}
    r = requests.get(target_url, headers={'User-Agent': 'Sea'})
    crawl_result['status_code'] = r.status_code
    crawl_result['text'] = r.text
    return crawl_result

def main():
    if len(sys.argv) < 2:
        print('[ERROR] No target URL supplied. Please provide a URL for seaspider to crawl.')
    else:
        origin_url = sys.argv[1]
        
        if len(sys.argv) >= 3:
            domain_restriction = sys.argv[2]
            crawl_from_origin(origin_url, domain_restriction)
        else:
            domain_restriction_warning = 'You are about to crawl with domain'\
                'restriction. Are you sure? (y/n) '
            user_input = input(domain_restriction_warning)
            
            if user_input == 'y':
                crawl_from_origin(origin_url)
                
    print('Ending session...')
            
main()
