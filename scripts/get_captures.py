# -*- coding: utf-8 -*-

# Description: retrieves the capture ids of items
# Example usage:
#   python get_captures.py ../data/src/pd_items.json ../data/captures.json

import json
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputfile item captures json>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

# config
imageURLPattern = '^http://images\.nypl\.org/index\.php\?id=([^&]+)&t=g$'

# init
captureIds = []

# Captures
noCaptureCount = 0
invalidCaptureCount = 0

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)

    # Retrieve capture ids of item's first capture
    captureId = ""
    if "captures" in item and len(item["captures"]) > 0:
        capture = item["captures"][0]
        match = re.search(imageURLPattern, capture)
        if match:
            captureId = match.group(1).strip()
        if not captureId:
            print "Invalid Image URL: " + capture
            invalidCaptureCount += 1
    else:
        noCaptureCount += 1

    captureIds.append(captureId)

# Report on captures
print str(noCaptureCount) + " items with no captures"
print str(invalidCaptureCount) + " items with invalid captures"

# Write out data
with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(captureIds, outfile)
print "Wrote " + str(len(captureIds)) + " lines to " + OUTPUT_FILE
