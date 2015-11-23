# -*- coding: utf-8 -*-

# Description: generates a json file that contains the labels necessary for the UI
# Example usage:
#   python generate_labels.py ../data/ ../js/labels.json 100 10 50 20 3

import json
import math
import os
from pprint import pprint
import sys

if len(sys.argv) < 7:
    print "Usage: %s <inputdir of data> <outputfile labels json> <images per row> <image cell height> <group item threshold> <group threshold> <min group rows>" % sys.argv[0]
    sys.exit(1)
INPUT_DIR = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
ITEMS_PER_ROW = int(sys.argv[3])
ITEM_H = int(sys.argv[4])
GROUP_ITEM_THRESHOLD = int(sys.argv[5])
GROUP_THRESHOLD = int(sys.argv[6])
MIN_GROUP_ROWS = int(sys.argv[7])

labels = [
    {'id': 'centuries', 'label': 'Century Created', 'markers': []},
    {'id': 'genres', 'label': 'Genre', 'markers': []},
    {'id': 'collections', 'label': 'Collection', 'markers': []},
    {'id': 'colors', 'label': 'Color', 'markers': []}
]

minGroupHeight = ITEM_H * MIN_GROUP_ROWS

def getHeight(item_count):
    global ITEMS_PER_ROW
    global ITEM_H
    global minGroupHeight

    rows = int(math.ceil(1.0 * item_count / ITEMS_PER_ROW))
    height = max(rows * ITEM_H, minGroupHeight)

    return height

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
            if item['count'] < GROUP_ITEM_THRESHOLD and len(data) > GROUP_THRESHOLD:
                other['count'] += item['count']
            else:
                url = item['url'] if 'url' in item else ''
                height = getHeight(item['count'])
                markers.append({
                    'label': item['label'],
                    'url': (item['url'] if 'url' in item else ''),
                    'count': item['count'],
                    'value': item['value'],
                    'h': height
                })
                y += height
        # Add other
        if other['count']:
            other['h'] = getHeight(other['count'])
            markers.append(other)
        # Add unknown
        if unknown:
            markers.append({
                'label': unknown['label'],
                'url': (unknown['url'] if 'url' in unknown else ''),
                'count': unknown['count'],
                'value': unknown['value'],
                'h': getHeight(unknown['count'])
            })
    labels[i]['markers'] = markers

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(labels, outfile)
print "Wrote " + str(len(labels)) + " labels to " + OUTPUT_FILE
