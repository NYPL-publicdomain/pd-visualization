# -*- coding: utf-8 -*-

# Description: generates a json file that contains the data necessary for the UI
# Example usage:
#   python generate_metadata.py ../data/src/pd_items.json ../js/items/ 5

import json
import math
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 3:
    print "Usage: %s <inputfile items json> <outputfile item captures json> <number of files>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
FILE_COUNT = int(sys.argv[3])

# config
imageURLPattern = '^http://images\.nypl\.org/index\.php\?id=([^&]+)&t=g$'

# init
items = []

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)

    # Retrieve UUID
    uuid = ""
    if "UUID" in item and item["UUID"]:
        uuid = item["UUID"].strip()

    # Retrieve title
    title = ""
    if "title" in item and item["title"]:
        title = item["title"].encode("utf-8").strip()

    # Retrieve capture id of item's first capture
    captureId = ""
    if "captures" in item and len(item["captures"]) > 0:
        capture = item["captures"][0]
        match = re.search(imageURLPattern, capture)
        if match:
            captureId = match.group(1).strip()

    items.append([uuid, title, captureId])

# Write out data
groupSize = int(math.ceil(1.0 * len(items) / FILE_COUNT))
start = 0
end = groupSize
for i in range(FILE_COUNT):
    fileName = OUTPUT_DIR + 'items_'+str(i)+'_'+str(FILE_COUNT)+'.json'
    if i >= FILE_COUNT-1:
        group = items[start:]
    else:
        group = items[start:end]
        start = end
        end += groupSize
    with open(fileName, 'w') as outfile:
        json.dump(group, outfile)
    print "Wrote " + str(len(group)) + " lines to " + fileName
