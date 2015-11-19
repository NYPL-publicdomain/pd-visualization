# -*- coding: utf-8 -*-

# Description: retrieves the date (year) of items
# Example usage:
#   python get_dates.py ../data/src/pd_items.json ../data/dates.json

from collections import Counter
import json
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputfile item dates json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

# config
yearPattern = '[^0-9]*([12][0-9]{3}).*'

# init
dates = []

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
    item = json.loads(line)

    # Retrieve date
    date = ""
    if "date" in item and len(item["date"]) > 0:
        for d in item["date"]:
            year = getYearFromString(d)
            if year:
                date = year
                break
        # if not date:
        #     print "No date found for: "
        #     pprint(item["date"])
    dates.append(date)

# Report on dates
date_counts = Counter(dates)
pprint(date_counts)

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(dates, outfile)
print "Wrote " + str(len(dates)) + " lines to " + OUTPUT_FILE
