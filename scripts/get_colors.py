# -*- coding: utf-8 -*-

# Description: retrieves the color-group of items
# Example usage:
#   python get_colors.py ../data/item_hsl.json ../data/colors.json ../data/item_colors.json

from colour import Color
import copy
import json
import math
from pprint import pprint
import sys

# input
if len(sys.argv) < 3:
    print "Usage: %s <inputfile color data json> <outputfile colors json> <outputfile item colors json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
OUTPUT_ITEMS_FILE = sys.argv[3]

# config
colors = [
    {'index': 0, 'value': '#ff0000', 'label': 'Red', 'count': 0},
    {'index': 1, 'value': '#ffa500', 'label': 'Orange', 'count': 0},
    {'index': 2, 'value': '#ffff00', 'label': 'Yellow', 'count': 0},
    {'index': 3, 'value': '#008000', 'label': 'Green', 'count': 0},
    {'index': 4, 'value': '#0000ff', 'label': 'Blue', 'count': 0},
    {'index': 5, 'value': '#800080', 'label': 'Violet', 'count': 0},
    {'index': 6, 'value': '#ffffff', 'label': 'White', 'count': 0},
    {'index': 7, 'value': '#000000', 'label': 'Black', 'count': 0},
    {'index': 8, 'value': '', 'label': 'Unknown', 'count': 0}
]
black_luminance_threshold = 0.2
white_luminance_threshold = 0.84

# init
item_colors = []

# init items
items = []
with open(INPUT_FILE) as data_file:
    items = json.load(data_file)
itemCount = len(items)
print "Loaded " + str(itemCount) + " items..."

def getNearestColor(c, the_list):
    global black_luminance_threshold
    global white_luminance_threshold

    hue = c[0]
    saturation = c[1]
    luminance = c[2]

    # Create a copy
    color_list = copy.deepcopy(the_list)

    # Check for black
    if luminance < black_luminance_threshold:
        return next(iter([_c for _c in color_list if _c['label']=='Black']))

    # Check for white
    elif luminance > white_luminance_threshold and saturation < (1.0-white_luminance_threshold):
        return next(iter([_c for _c in color_list if _c['label']=='White']))

    # Remove black and white from list
    color_list = [_c for _c in color_list if _c['value'] and _c['label']!='Black' and _c['label']!='White']

    # Find the color with the smallest distance in hue
    min_color_i = 0
    min_color = Color(color_list[min_color_i]['value'])
    min_distance = abs(hue - min_color.hue)
    for _c in color_list:
        _color = Color(_c['value'])
        _distance = abs(hue - _color.hue)
        if _distance < min_distance:
            min_color_i = _c['index']
            min_color = _color
            min_distance = _distance

    return color_list[min_color_i]

# analyze colors
for i, weighted_hsl in enumerate(items):
    hsl = []
    weight = 0
    nearest_color = next(iter([_c for _c in colors if _c['label']=='Unknown']))
    if len(weighted_hsl) > 0 and len(weighted_hsl[0]) > 0:
        hsl = weighted_hsl[0]
        weight = weighted_hsl[1]
        nearest_color = getNearestColor(hsl, colors)

    colors[nearest_color['index']]['count'] += 1
    item_colors.append([nearest_color['index'], weight])

    sys.stdout.write('\r')
    sys.stdout.write(str(round(1.0*i/itemCount*100,3))+'%')
    sys.stdout.flush()

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(colors, outfile)
print "Wrote " + str(len(colors)) + " colors to " + OUTPUT_FILE

with open(OUTPUT_ITEMS_FILE, 'w') as outfile:
    json.dump(item_colors, outfile)
print "Wrote " + str(len(item_colors)) + " items to " + OUTPUT_ITEMS_FILE
