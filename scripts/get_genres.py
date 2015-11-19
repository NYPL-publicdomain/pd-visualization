# -*- coding: utf-8 -*-

# Description: retrieves the genre of items; attempts to normalize genre text
# Example usage:
#   python get_genres.py ../data/src/pd_items.json ../data/genres.json ../data/item_genres.json

from collections import Counter
import json
from pprint import pprint
import re
import sys
import urllib

# input
if len(sys.argv) < 3:
    print "Usage: %s <inputfile items json> <outputfile genres json> <outputfile item genres json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
OUTPUT_ITEMS_FILE = sys.argv[3]

# if string contains [x]: replace with [y]
substrings = {
    'lithograph': 'lithographs',
    'lithogrpah': 'lithographs',
    'litograph': 'lithographs',
    'lithgraph': 'lithographs',
    'engraving': 'engravings',
    'engraing': 'engravings',
    'engraver': 'engravings',
    'print': 'prints',
    'etching': 'etchings',
    'drawing': 'drawings',
    'pencil': 'drawings',
    'watercolor': 'watercolors',
    'gouache': 'watercolors',
    'ink': 'drawings',
    'photograph': 'photographs',
    'book': 'books',
    'monograph': 'books',
    'atlas': 'atlases',
    'painting': 'paintings',
    'illustration': 'illustrations',
    'map': 'maps',
    'cartographic': 'maps',
    'pen': 'drawings',
    'manuscript': 'manuscripts',
    'document': 'documents',
    'scroll': 'scrolls',
    'scores': 'sheet music',
    'musical notation': 'sheet music'
}

# init
genres = []
item_genres = []

def addGenre(g):
    global genres
    global item_genres

    genre = next(iter([_g for _g in genres if _g['value']==g]), False)

    if genre:
        genres[genre['index']]['count'] += 1
    else:
        label = 'Unknown'
        url = ''
        if g:
            label = g.capitalize()
            url = 'http://digitalcollections.nypl.org/search/index?filters%5Bgenre%5D=' + urllib.quote(label)
        genre = {
            'index': len(genres),
            'value': g,
            'label': label,
            'url': url,
            'count': 1
        }
        genres.append(genre)

    item_genres.append(genre['index'])

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)

    # Retrieve genre
    genre = ""
    if "genre" in item and len(item["genre"]) > 0:
        for g in item["genre"]:
            g = str(g["text"].encode("utf_8"))
            # Make lowercase exclude everything after divider
            g = g.lower().split(" -- ")[0]
            # Remove non-ASCII chars
            g = re.sub(r'[^\x00-\x7F]+','', g)
            # Trim string
            g = g.strip()
            for s in substrings:
                if s in g:
                    g = substrings[s]
                    break
            genre = g
            break
    addGenre(genre)

# Report on collections
genres = sorted(genres, key=lambda d: d['count'], reverse=True)
pprint(genres)

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(genres, outfile)
print "Wrote " + str(len(genres)) + " genres to " + OUTPUT_FILE

with open(OUTPUT_ITEMS_FILE, 'w') as outfile:
    json.dump(item_genres, outfile)
print "Wrote " + str(len(item_genres)) + " items to " + OUTPUT_ITEMS_FILE
