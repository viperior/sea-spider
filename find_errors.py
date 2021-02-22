import dominate
from dominate.tags import *
from dominate.util import raw
import glob
import json

def display_statistics(stats):
    output = 'Statistics:'

    for i in range(len(stats)):
        output += '\n' + stats[i]['label'] + ': ' + str(stats[i]['value'])

    print(output)

def find_errors():
    ignore_list = ['data/url_id_map.json']
    glob_pattern = 'data/*.json'
    item_count = 0
    ok_count = 0
    problem_count = 0
    response_codes = {}

    for item in glob.glob(glob_pattern):
        if item in ignore_list:
            pass
        
        with open(item, 'r') as infile:
            url_id = item.replace('.json', '').replace('data\\', '')
            json_data = json.load(infile)

        if 'id' in json_data.keys():
            item_count += 1
            response_code = int(json_data['response_code'])
            url = json_data['url']

            if response_code == 200:
                ok_count += 1
            else:
                problem_count += 1

            response_codes[int(url_id)] = {
                'response_code': response_code,
                'url': url
            }

            print(response_code, ' ', url)
    
    stats = {
        0: {
            'label': 'Total items',
            'value': item_count
        },
        1: {
            'label': 'Healthy signals',
            'value': ok_count
        },
        2: {
            'label': 'Problems',
            'value': problem_count
        },
        3: {
            'label': 'Health score',
            'value': str(round((ok_count / item_count) * 100.0)) + '%'
        }
    }
    display_statistics(stats)
    generate_error_report(stats, response_codes)

def generate_error_report(stats, response_codes):
    doc = dominate.document(title='Crawl Statistics')

    with doc.head:
        meta(charset='utf-8')
        meta(description='Crawl Statistics')
        link(rel='stylesheet', href='css/styles.css')

    with doc:
        h1('Crawl Statistics')
        
        with table():
            with thead():
                with tr():
                    th('Metric')
                    th('Value')
            with tbody():
                for i in range(len(stats)):
                    with tr():
                        td(stats[i]['label'])
                        td(stats[i]['value'])

        with div(cls='emoji-cloud'):
            for key in response_codes.keys():
                response_code = int(response_codes[key]['response_code'])
                url = response_codes[key]['url']
                
                if response_code == 200:
                    emoji = '&#10004;'
                else:
                    emoji = '&#128293;'
                
                span(raw(emoji), title=url)

        with table():
            with thead():
                with tr():
                    th('Response code')
                    th('URL')
            with tbody():
                for key in response_codes.keys():
                    with tr():
                        td(response_codes[key]['response_code'])
                        td(response_codes[key]['url'])

    with open('docs/crawl-stats-report.html', 'w') as f:
        f.write(doc.render())

find_errors()
