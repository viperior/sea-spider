import bs4
from csv import reader
import find_errors
import glob
import json
import logging
import os
import re
import requests
import sys
import time

def crawl_csv_url_list():
    logging.info('Reading data from CSV')
    csv_file_path = get_config_value('csv_file_path')
    
    if len(glob.glob(csv_file_path)) > 0:
        with open(csv_file_path, 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader:
                crawl_recursively(row[0], depth=1)
    else:
        log_error_and_crash_with_message(
            'Could not find file: ' + csv_file_path
        )

def crawl_from_origin_url():
    url = get_config_value('origin_domain')
    origin_url = 'https://' + url 
    logging.info('Performing domain-wide scan on :' + origin_url)
    crawl_recursively(origin_url, depth=1)

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
        delay_between_crawls = get_config_value('delay_between_crawls')
        time.sleep(delay_between_crawls)
        crawl_result = {
            "id": url_id,
            "url": url,
            "response_code": r.status_code,
            "timestamp_float": time.time(),
            "text": r.text
        }

        with open(crawl_file_name_pattern, 'w') as outfile:
            json.dump(crawl_result, outfile, indent=4)

def create_empty_log_file(log_file_directory, log_file_filename):
    log_file_path = f"{log_file_directory}/{log_file_filename}"
    
    if not os.path.exists(log_file_directory):
        os.mkdir(log_file_directory)
    
    if not os.path.exists(log_file_path):
        open(log_file_path, 'a').close()

def extract_links_from_html(html):
    allow_outside = get_config_value('allow_outside_starting_domain')
    origin_domain = get_config_value('origin_domain')
    soup = bs4.BeautifulSoup(html, features='html.parser')
    pattern = '^https?://'

    if not allow_outside:
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

def log_error_and_crash_with_message(message):
    logging.error(message)
    raise ValueError(message)

def register_new_url_id(id, url):
    if len(glob.glob('data/url_id_map.json')) > 0:
        with open('data/url_id_map.json', 'r') as url_id_map_file:
            url_id_map = json.load(url_id_map_file)
    else:
        url_id_map = {}

    url_id_map[id] = {'url': url}

    with open('data/url_id_map.json', 'w') as url_id_map_file:
        json.dump(url_id_map, url_id_map_file, indent=4)

def validate_config_file():
    allow_outside_starting_domain = get_config_value('allow_outside_starting_domain')
    origin_domain = get_config_value('origin_domain')

    if allow_outside_starting_domain:
        logging.warning('Scan mode allows crawling outside origin domain')
    
    if (not allow_outside_starting_domain) and (origin_domain == False or \
        len(origin_domain) < 1):
        log_error_and_crash_with_message('Domain restriction active but no domain filter set')

def main():
    log_file_directory = 'data'
    log_file_filename = 'seaspider.log'
    log_file_path = 'data/seaspider.log'
    create_empty_log_file(log_file_directory, log_file_filename)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.WARNING,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file_path
    )

    validate_config_file()
    operation_mode = get_config_value('operation_mode')

    if operation_mode == 'domain_scan':
        crawl_from_origin_url()
    elif operation_mode == 'csv':
        crawl_csv_url_list()
    else:
        log_error_and_crash_with_message('Operation mode unrecognized: ' + \
            operation_mode + '\nPlease use \'domain_scan\' or \'csv\' as ' + \
            'the operation_mode value and try again.')
        pass
    find_errors.find_errors()

if __name__ == '__main__':
    main()
