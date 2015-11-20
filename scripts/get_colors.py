# -*- coding: utf-8 -*-

# Description: retrieves the dominant color of items
# Example usage:
#   python get_colors.py ../data/captures.json ../img/items/ ../data/colors.json ../data/item_colors.json

from collections import namedtuple
from colour import Color
import json
from math import sqrt
from PIL import Image
from pprint import pprint
import random
import sys

# input
if len(sys.argv) < 4:
    print "Usage: %s <inputfile items json> <dir for images> <outputfile colors json> <outputfile item colors json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
INPUT_IMAGE_DIR = sys.argv[2]
OUTPUT_FILE = sys.argv[3]
OUTPUT_ITEMS_FILE = sys.argv[4]

# config
imageExt = "jpg"

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))

def colorz(filename, n=3):
    try:
        img = Image.open(filename)
        w, h = img.size
        if w > 200 or h > 200:
            img.thumbnail((200, 200))
            w, h = img.size
        points = get_points(img)
        clusters = kmeans(points, n, 1)
        rgbs = [map(int, c.center.coords) for c in clusters]
        return map(rtoh, rgbs)
    except IOError:
        return []
    except:
        return []

def euclidean(p1, p2):
    return sqrt(sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))

def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while 1:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

# init
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
black_luminance_threshold = 0.16
white_luminance_threshold = 0.84
item_colors = []

# init items
items = []
with open(INPUT_FILE) as data_file:
    items = json.load(data_file)
itemCount = len(items)
print "Loaded " + str(itemCount) + " items..."

def getNearestColor(c, color_list):
    global black_luminance_threshold
    global white_luminance_threshold

    # Create a copy
    color_list = color_list[:]

    # Check for black
    if c.luminance < black_luminance_threshold:
        return next(iter([_c for _c in color_list if _c['label']=='Black']))

    # Check for white
    elif c.luminance > white_luminance_threshold:
        return next(iter([_c for _c in color_list if _c['label']=='White']))

    # Remove black and white from list
    color_list = [_c for _c in color_list if _c['value'] and _c['label']!='Black' and _c['label']!='White']

    # Find the color with the smallest distance in hue
    min_color_i = 0
    min_color = Color(color_list[min_color_i]['value'])
    min_distance = abs(c.hue - min_color.hue)
    for _c in color_list:
        _color = Color(_c['value'])
        _distance = abs(c.hue - _color.hue)
        if _distance < min_distance:
            min_color_i = _c['index']
            min_color = _color
            min_distance = _distance

    return color_list[min_color_i]


# analyze colors
for i, captureId in enumerate(items):
    if captureId:
        fileName = INPUT_IMAGE_DIR + "415905" + "." + imageExt
        imgColors = colorz(fileName, 3)
        nearest_color = next(iter([_c for _c in colors if _c['label']=='Unknown']))
        if len(imgColors) > 0:
            c = Color(imgColors[0])
            nearest_color = getNearestColor(c, colors)
        colors[nearest_color['index']]['count'] += 1
        item_colors.append(nearest_color['index'])

    sys.stdout.write('\r')
    sys.stdout.write(str(round(1.0*i/itemCount*100,5))+'%')
    sys.stdout.flush()

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(colors, outfile)
print "Wrote " + str(len(colors)) + " colors to " + OUTPUT_FILE

with open(OUTPUT_ITEMS_FILE, 'w') as outfile:
    json.dump(item_colors, outfile)
print "Wrote " + str(len(item_colors)) + " items to " + OUTPUT_ITEMS_FILE
