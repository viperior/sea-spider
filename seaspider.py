import bs4
from csv import reader
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
        logging.info('Python requests call completed: ' + str(r.status_code) + ' ' + url)
        time.sleep(0.2)
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
    logging.basicConfig(filename='data/seaspider.log', level=logging.ERROR)
    operation_mode = get_config_value('operation_mode')
    allow_outside_starting_domain = get_config_value('allow_outside_starting_domain')
    origin_domain = get_config_value('origin_domain')

    if allow_outside_starting_domain:
        logging.warn('Scan mode allows crawling outside origin domain')
    
    if (not allow_outside_starting_domain) \
        and (origin_domain == False or len(origin_domain) < 1):
        error_message = 'Domain restriction active but no domain filter set'
        logging.error(error_message)
        raise ValueError(error_message)

    if operation_mode == 'domain-scan':
        logging.info('Performing a domain-wide crawl')
        origin_url = 'https://' + origin_domain
        logging.info('Performing domain-wide scan on :' + origin_domain)
        crawl_recursively(origin_url, depth=1)
        find_errors.find_errors()
    elif operation_mode == 'csv':
        logging.info('Reading data from CSV')
        # open file in read mode
        csv_file_path = 'data/in.csv'
        
        if len(glob.glob(csv_file_path)) > 0:
            with open(csv_file_path, 'r') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = reader(read_obj)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    crawl_recursively(row[0], depth=1)

                find_errors.find_errors()
        else:
            logging.error('Could not find file: ' + csv_file_path)
    else:
        logging.error('Operation mode unrecognized: ' + operation_mode)

main()
