import bs4
import find_errors
import glob
import json
import logging
import re
import requests
import sys
import time

def crawl_recursively(url, depth=1):
    url = url.split('#', 1)[0]
    max_crawl_depth = get_config_value('max_crawl_depth')
    
    if depth <= max_crawl_depth:
        crawl_target(url)
        url_id = get_url_id(url)

        with open('data/' + str(url_id) + '.json') as crawl_file:
            crawl_json = json.load(crawl_file)

        crawl_html = crawl_json['text']
        links = extract_links_from_html(crawl_html)

        for link in links:
            crawl_recursively(link, depth + 1)

def crawl_target(url):
    logging.debug('Considering crawl target: ' + url)
    url_id = get_url_id(url)
    crawl_file_name_pattern = 'data/' + str(url_id) + '.json'
    crawl_file_exists = len(glob.glob(crawl_file_name_pattern)) > 0

    if not crawl_file_exists:
        print('Crawling: ', url)
        r = requests.get(url, headers={'User-Agent': 'Sea'})
        crawl_result = {
            "id": url_id,
            "url": url,
            "response_code": r.status_code,
            "timestamp_float": time.time(),
            "text": r.text
        }

        with open(crawl_file_name_pattern, 'w') as outfile:
            json.dump(crawl_result, outfile, indent=4)

def extract_links_from_html(html):
    allow_outside_starting_domain = get_config_value('allow_outside_starting_domain')
    origin_domain = get_config_value('origin_domain')
    soup = bs4.BeautifulSoup(html, features='html.parser')
    pattern = '^https?://'

    if not allow_outside_starting_domain:
        pattern += origin_domain

    links = soup.findAll('a', attrs={'href': re.compile(pattern)})
    links_list = []

    for link in links:
        url = link.get('href')
        links_list.append(url)

    return links_list

def get_max_url_id():
    if len(glob.glob('data/url_id_map.json')) > 0:
        with open('data/url_id_map.json') as url_id_map_file:
            url_id_map = json.load(url_id_map_file)

        max_id = 0

        for url_id in url_id_map.keys():
            if int(url_id) > max_id:
                max_id = int(url_id)

        return max_id
    else:
        return 0

def get_url_id(url):
    if len(glob.glob('data/url_id_map.json')) > 0:
        with open('data/url_id_map.json', 'r') as url_id_map_file:
            url_id_map = json.load(url_id_map_file)

        for url_id in url_id_map.keys():
            if url_id_map[url_id]['url'] == url:
                return url_id
        
    new_url_id = get_max_url_id() + 1
    register_new_url_id(new_url_id, url)
    return new_url_id

def get_config_value(key):
    with open('config.json', 'r') as config_file:
        config_json = json.load(config_file)

    return config_json[key]

def register_new_url_id(id, url):
    if len(glob.glob('data/url_id_map.json')) > 0:
        with open('data/url_id_map.json', 'r') as url_id_map_file:
            url_id_map = json.load(url_id_map_file)
    else:
        url_id_map = {}

    url_id_map[id] = {'url': url}

    with open('data/url_id_map.json', 'w') as url_id_map_file:
        json.dump(url_id_map, url_id_map_file, indent=4)

def main():
    logging.basicConfig(filename='data/example.log', level=logging.DEBUG)
    origin_url = 'https://' + get_config_value('origin_domain')
    crawl_recursively(origin_url)
    find_errors.find_errors()

main()
