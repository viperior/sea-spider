import glob
import json

def find_errors():
    ignore_list = ['data/url_id_map.json']
    glob_pattern = 'data/*.json'
    item_count = 0
    ok_count = 0
    problem_count = 0

    for item in glob.glob(glob_pattern):
        with open(item, 'r') as infile:
            json_data = json.load(infile)

        if 'id' in json_data.keys():
            item_count += 1
            response_code = int(json_data['response_code'])
            url = json_data['url']

            if response_code == 200:
                ok_count += 1
            else:
                problem_count += 1

            print(response_code, ' ', url)
                
    print('Statistics:\nTotal items: ', item_count, '\nHealthy signals: ', \
        ok_count, '\nProblems: ', problem_count)
