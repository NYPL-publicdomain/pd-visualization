# -*- coding: utf-8 -*-

# Description: generates a json file that contains the item ids in order they appear in the UI
# Example usage:
#   python generate_coordinates.py ../data/ ../js/coords.json 100 10 10 50 20 3

from PIL import Image
import json
import math
import os
import sys

# input
if len(sys.argv) < 8:
    print "Usage: %s <inputdir of data> <outputfile json> <images per row> <image cell width> <image cell height> <group item threshold> <group threshold> <min group rows>" % sys.argv[0]
    sys.exit(1)
INPUT_DATA_DIR = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
ITEMS_PER_ROW = int(sys.argv[3])
ITEM_W = int(sys.argv[4])
ITEM_H =  int(sys.argv[5])
GROUP_ITEM_THRESHOLD = int(sys.argv[6])
GROUP_THRESHOLD = int(sys.argv[7])
MIN_GROUP_ROWS = int(sys.argv[8])

# init
coords = {
    'centuries': [],
    'genres': [],
    'collections': [],
    'colors': []
}

def getGroups(groupName):
    global INPUT_DATA_DIR
    global GROUP_ITEM_THRESHOLD
    global GROUP_THRESHOLD

    item_groups = []
    groups = []

    _groups = []
    with open(INPUT_DATA_DIR + groupName + '.json') as data_file:
        _groups = json.load(data_file)
    with open(INPUT_DATA_DIR + 'item_' + groupName + '.json') as data_file:
        item_groups = json.load(data_file)

    # Take out unknown group
    unknown = next(iter([g for g in _groups if not g['value']]), False)
    other = {
        'count': 0,
        'items': []
    }
    # Add items to appropriate groups
    for i,g in enumerate(_groups):
        if g['value']:
            item_ids = [item_i for item_i, group_i in enumerate(item_groups) if group_i == g['index']]
            # this group is too small; add to "other" group
            if g['count'] < GROUP_ITEM_THRESHOLD and len(_groups) > GROUP_THRESHOLD:
                other['items'].extend(item_ids)
                other['count'] += g['count']
            else:
                g['items'] = item_ids
                groups.append(g)
    # Add "other" group
    if other['count']:
        groups.append(other)

    # Add "uknown" group
    if unknown:
        unknown['items'] = [item_i for item_i, group_i in enumerate(item_groups) if group_i == unknown['index']]
        groups.append(unknown)

    return groups

for groupName in coords:
    item_coords = []
    groups = getGroups(groupName)

    for g in groups:
        for itemId in g['items']:
            item_coords.append(itemId)

        # determine extra blank rows
        rows = int(math.ceil(1.0 * g['count'] / ITEMS_PER_ROW))
        extra_rows = max(MIN_GROUP_ROWS - rows, 0)

        # determine extra blank items in last row
        extra_items_in_last_row = rows * ITEMS_PER_ROW - g['count']
        blanks = extra_rows * ITEMS_PER_ROW + extra_items_in_last_row

        # fill the blanks with placeholders
        for blank in range(blanks):
            item_coords.append(-1)

    coords[groupName] = item_coords

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(coords, outfile)
print "Wrote coords to " + OUTPUT_FILE
