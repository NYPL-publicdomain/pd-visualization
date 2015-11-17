# -*- coding: utf-8 -*-

# Description: normalizes data for use in all other scripts
# Example usage:
#   python normalize_data.py ../data/src/pd_items.json ../data/

import json
from pprint import pprint
import re
import sys

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputdir for data>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

# config
imageURLPattern = '^http://images\.nypl\.org/index\.php\?id=([^&]+)&t=g$'
# files
files = {
    "captures": []
}

# Captures
noCaptureCount = 0
invalidCaptureCount = 0

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)
    # pprint(item)

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
    files["captures"].append(captureId)

# Report on captures
print str(noCaptureCount) + " items with no captures"
print str(invalidCaptureCount) + " items with invalid captures"

# Write out data
for f in files:
    fname = OUTPUT_DIR + f + ".json"
    data = files[f]
    with open(fname, 'w') as outfile:
        json.dump(data, outfile)
    print "Wrote " + str(len(data)) + " lines to " + fname
