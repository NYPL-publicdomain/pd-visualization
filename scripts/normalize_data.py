# -*- coding: utf-8 -*-

# Description: normalizes data for use in all other scripts
# Example usage:
#   python normalize_data.py ../data/src/pd_items.json ../data/items.json

from collections import Counter
import json
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputfile items json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

# config
imageURLPattern = '^http://images\.nypl\.org/index\.php\?id=([^&]+)&t=g$'
yearPattern = '[^0-9]*([12][0-9]{3}).*'

# init
items = []

# Captures
noCaptureCount = 0
invalidCaptureCount = 0

# Get a year from string
def getYearFromString(d):
    # Make everything a string
    if isinstance(d, (int, long, float)):
        d = str(d)
    # Case: 170 becomes 1700
    if len(d) < 4:
        d = d.ljust(4, '0')
    # Look for first year in standard format (e.g. 1900)
    match = re.search(yearPattern, d)
    if match:
        return int(match.group(1))
    # Case: 17-- becomes 1700, 179? becomes 1790
    d = d.replace('-', '0')
    d = d.replace('?', '0')
    match = re.search(yearPattern, d)
    if match:
        return int(match.group(1))
    # Case: 17th century becomes 1600
    match = re.search('[^0-9]*([12][0-9])th.*', d)
    if match:
        century = int(match.group(1))
        century -= 1
        return century * 100
    # Case: 865, 950 (super old)
    match = re.search('[^0-9]*([89][0-9]{2}).*', d)
    if match:
        return int(match.group(1))
    return False

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    _item = json.loads(line)
    item = {}
    # pprint(item)

    # Retrieve capture ids of item's first capture
    captureId = ""
    if "captures" in _item and len(_item["captures"]) > 0:
        capture = _item["captures"][0]
        match = re.search(imageURLPattern, capture)
        if match:
            captureId = match.group(1).strip()
        if not captureId:
            print "Invalid Image URL: " + capture
            invalidCaptureCount += 1
    else:
        noCaptureCount += 1
    item['captureId'] = captureId

    # Retrieve date
    date = ""
    if "date" in _item and len(_item["date"]) > 0:
        for d in _item["date"]:
            year = getYearFromString(d)
            if year:
                date = year
                break
        # if not date:
        #     print "No date found for: "
        #     pprint(_item["date"])
    item['date'] = date
    items.append(item)

# Report on captures
print str(noCaptureCount) + " items with no captures"
print str(invalidCaptureCount) + " items with invalid captures"

# Report on dates
dates = Counter([i["date"] for i in items])
pprint(dates)

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(items, outfile)
print "Wrote " + str(len(items)) + " lines to " + OUTPUT_FILE
