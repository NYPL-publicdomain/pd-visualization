# -*- coding: utf-8 -*-

# Description: retrieves the dominant color of item images
# Example usage:
#   python get_color_data.py ../data/captures.json ../img/items/ ../data/item_hsl.json 3

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
    print "Usage: %s <inputfile items json> <dir for images> <outputfile item colors json> <num of color groups>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
INPUT_IMAGE_DIR = sys.argv[2]
OUTPUT_FILE = sys.argv[3]
COLOR_GROUP_COUNT = int(sys.argv[4])

# config
imageExt = "jpg"
resizeTo = 20
black_luminance_threshold = 0.2
white_luminance_threshold = 0.8

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))
WeightedColor = namedtuple('WeightedColor', ('color', 'weight'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))

def colorz(filename, n=3):
    global resizeTo

    try:
        img = Image.open(filename)
        w, h = img.size
        if w > resizeTo or h > resizeTo:
            img.thumbnail((resizeTo, resizeTo))
            w, h = img.size
        points = get_points(img)
        clusters = kmeans(points, n, 1)
        rgbs = [map(int, c.center.coords) for c in clusters]
        weights = [1.0*len(c.points)/(w*h) for c in clusters]
        hexs = map(rtoh, rgbs)
        colors = [Color(h) for h in hexs]
        weighted_colors = [WeightedColor(c, weights[i]) for i,c in enumerate(colors)]
        return weighted_colors
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

def chooseColor(weighted_colors):
    global black_luminance_threshold
    global white_luminance_threshold

    # sort by saturation
    weighted_colors = sorted(weighted_colors, key=lambda c: c.color.saturation, reverse=True)

    # separate colors by luminance
    prioritized_colors = [c for c in weighted_colors if c.color.luminance > black_luminance_threshold and c.color.luminance < white_luminance_threshold]
    deprioritized_colors = [c for c in weighted_colors if c.color.luminance <= black_luminance_threshold or c.color.luminance >= white_luminance_threshold]

    # combine the two color lists
    weighted_colors = prioritized_colors + deprioritized_colors

    # return the first one
    return weighted_colors[0]

# init
item_colors = []

# init items
items = []
with open(INPUT_FILE) as data_file:
    items = json.load(data_file)
itemCount = len(items)
print "Loaded " + str(itemCount) + " items..."

# analyze colors
for i, captureId in enumerate(items):
    if captureId:
        fileName = INPUT_IMAGE_DIR + captureId + "." + imageExt
        # fileName = "../img/items/415904.jpg"
        weighted_colors = colorz(fileName, COLOR_GROUP_COUNT)
        hsl = []
        if len(weighted_colors) > 0:
            c = chooseColor(weighted_colors)
            hsl = [c.color.hue, c.color.saturation, c.color.luminance]
        item_colors.append([hsl, c.weight])

    sys.stdout.write('\r')
    sys.stdout.write(str(round(1.0*i/itemCount*100,3))+'%')
    sys.stdout.flush()

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(item_colors, outfile)
print "Wrote " + str(len(item_colors)) + " colors to " + OUTPUT_FILE
