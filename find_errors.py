import dominate
from dominate.tags import *
from dominate.util import raw
import glob
import json
from time import gmtime, strftime

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

            if response_code == 200 and not 'http:' in url:
                ok_count += 1
                emoji = get_emoji_html('checkmark')
                status = 'ok'
            else:
                problem_count += 1
                emoji = get_emoji_html('red_x')
                status = 'problem'

            response_codes[int(url_id)] = {
                'status': status,
                'emoji': emoji,
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
        nav_items = [
            ['All reports', '../docs/'],
            ['Last report', '../docs/latest.html']
        ]
        
        with nav():
            with ul():
                for nav_item in nav_items:
                    with li():
                        a(nav_item[0], href=nav_item[1])

        div('Report timestamp: ' + get_current_timestamp_utc())
        
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
                url = response_codes[key]['url']
                emoji = response_codes[key]['emoji']
                title_text = str(response_codes[key]['response_code']) + \
                    ' ' + url
                a(raw(emoji), title=title_text, href=url)

        with table():
            with thead():
                with tr():
                    th('Status')
                    th('Response code')
                    th('URL')
            with tbody():
                for key in response_codes.keys():
                    if response_codes[key]['status'] == 'ok':
                        table_row_class = 'ok'
                    else:
                        table_row_class = 'problem'

                    with tr(cls=table_row_class):
                        td(raw(response_codes[key]['emoji']))
                        td(response_codes[key]['response_code'])
                        
                        with td():
                            url = response_codes[key]['url']
                            a(url, href=url)

    output_file_path = 'docs/crawl-stats-report.' + \
        get_current_timestamp_utc() + '.html'

    with open(output_file_path, 'w') as f:
        f.write(doc.render())

    with open('docs/latest.html', 'w') as f:
        f.write(doc.render())

def get_current_timestamp_utc():
    return strftime("%Y%m%dT%H%M%SZ", gmtime())

def get_emoji_html(emoji_name):
    prefix = '&#'
    postfix = ';'
    
    if emoji_name == 'checkmark':
        code = '9989'
    elif emoji_name == 'fire':
        code = '128293'
    elif emoji_name == 'rainbow':
        code = '127752'
    elif emoji_name == 'red_x':
        code = '10060'
    else:
        code = '10060'

    emoji_html = prefix + code + postfix
    return emoji_html
