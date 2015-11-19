# -*- coding: utf-8 -*-

# Description: retrieves the collection of each item
# Example usage:
#   python get_collections.py ../data/src/pd_items.json ../data/collections.json ../data/item_collections.json

import codecs
from collections import Counter
import json
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 3:
    print "Usage: %s <inputfile items json> <outputfile collections json> <outputfile item collections json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
OUTPUT_ITEMS_FILE = sys.argv[3]

# init
collections = []
item_collections = []

def addCollection(title, uuid):
    global collections
    global item_collections

    collection = next(iter([_c for _c in collections if _c['value']==uuid]), False)

    if collection:
        collections[collection['index']]['count'] += 1
    else:
        label = 'Unknown'
        url = ''
        if title:
            label = title
            url = 'http://digitalcollections.nypl.org/collections/' + uuid
        collection = {
            'index': len(collections),
            'value': uuid,
            'label': label,
            'url': url,
            'count': 1
        }
        collections.append(collection)

    item_collections.append(collection['index'])

with codecs.open(INPUT_FILE, encoding='utf-8') as infile:
    for line in infile:
        # Read line as json
        item = json.loads(line)

        uuid = ""
        if "collectionUUID" in item and item["collectionUUID"]:
            uuid = item["collectionUUID"].strip()

        # Retrieve collection title
        title = ""
        if "collectionTitle" in item and item["collectionTitle"]:
            title = item["collectionTitle"].encode("utf-8").strip()

        addCollection(title, uuid)

# Report on collections
collections = sorted(collections, key=lambda d: d['count'], reverse=True)
pprint(collections)

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(collections, outfile)
print "Wrote " + str(len(collections)) + " collections to " + OUTPUT_FILE

with open(OUTPUT_ITEMS_FILE, 'w') as outfile:
    json.dump(item_collections, outfile)
print "Wrote " + str(len(item_collections)) + " items to " + OUTPUT_ITEMS_FILE
