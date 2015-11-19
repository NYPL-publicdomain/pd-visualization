# -*- coding: utf-8 -*-

# Description: outputs the counts of different item property values
# Example usage:
#   python report_data.py ../data/src/pd_items.json ../data/report/

from collections import Counter
import json
import sys

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputdir>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

# init
data = {
    "collectionTitle": [],
    "date": [],
    "genre": [],
    "resourceType": [],
    "subjectGeographic": [],
    "subjectName": [],
    "subjectTitle": [],
    "subjectTopical": []
}

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)

    for d in data:
        if d in item and isinstance(item[d], basestring):
            data[d].append(item[d])
        elif d in item and isinstance(item[d], (list, tuple)) and len(item[d]) > 0:
            entry = item[d][0]
            if isinstance(entry, basestring):
                data[d].append(entry)
            elif isinstance(entry, (int, long, float)):
                data[d].append(str(entry))
            elif 'text' in entry:
                data[d].append(entry['text'])
        else:
            data[d].append('Unknown')


# Write out data
for d in data:
    fname = OUTPUT_DIR + d + ".json"
    counts = Counter(data[d])
    counts = sorted(counts.items(), key=lambda i: i[1], reverse=True)
    with open(fname, 'w') as outfile:
        json.dump(counts, outfile)
    print "Wrote to file: " + fname
