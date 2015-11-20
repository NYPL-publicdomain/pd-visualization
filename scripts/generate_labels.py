# -*- coding: utf-8 -*-

# Description: generates a json file that contains the labels necessary for the UI
# Example usage:
#   python generate_labels.py ../data/ ../js/labels.json 100 10 50 20

import json
import math
import os
from pprint import pprint
import sys

if len(sys.argv) < 6:
    print "Usage: %s <inputdir of data> <outputfile labels json> <images per row> <image cell height> <marker threshold> <item threshold>" % sys.argv[0]
    sys.exit(1)
INPUT_DIR = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
ITEMS_PER_ROW = int(sys.argv[3])
ITEM_H = int(sys.argv[4])
MARKER_THRESHOLD = int(sys.argv[5])
ITEM_THRESHOLD = int(sys.argv[6])

labels = [
    {'id': 'centuries', 'label': 'Date Created', 'markers': []},
    {'id': 'genres', 'label': 'Genre', 'markers': []},
    {'id': 'collections', 'label': 'Collection', 'markers': []},
    {'id': 'colors', 'label': 'Color', 'markers': []}
]

def getHeight(item_count):
    global ITEMS_PER_ROW
    global ITEM_H

    rows = int(math.ceil(1.0 * item_count / ITEMS_PER_ROW))
    return rows * ITEM_H

for i, l in enumerate(labels):
    fileName = INPUT_DIR + l['id'] + '.json'

    if not os.path.isfile(fileName):
        print "Warning: " + fileName + " does not exist."
        continue

    markers = []
    other = {
        'label': 'Other',
        'count': 0,
        'value': '',
        'url': ''
    }

    with open(fileName) as data_file:
        data = json.load(data_file)
        # Remove unknown values
        unknown = next(iter([d for d in data if not d["value"]]), False)
        data = [d for d in data if d["value"]]
        y = 0
        for item in data:
            if item['count'] < MARKER_THRESHOLD and len(data) > ITEM_THRESHOLD:
                other['count'] += item['count']
            else:
                url = item['url'] if 'url' in item else ''
                markers.append({
                    'label': item['label'],
                    'url': (item['url'] if 'url' in item else ''),
                    'count': item['count'],
                    'value': item['value'],
                    'y': y
                })
                y += getHeight(item['count'])
        # Add other
        if other['count']:
            other['y'] = y
            markers.append(other)
            y += getHeight(other['count'])
        # Add unknown
        if unknown:
            markers.append({
                'label': unknown['label'],
                'url': (unknown['url'] if 'url' in unknown else ''),
                'count': unknown['count'],
                'value': unknown['value'],
                'y': y
            })
    labels[i]['markers'] = markers

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(labels, outfile)
print "Wrote " + str(len(labels)) + " labels to " + OUTPUT_FILE
