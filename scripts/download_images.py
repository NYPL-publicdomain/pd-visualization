# -*- coding: utf-8 -*-

# Example usage:
#   python download_images.py ../data/pd_mms_items.json ../img/items

import json
import os
from pprint import pprint
import sys
import urllib2

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile items json> <outputdir for images>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

# config
overwriteExisting = False
imageURLPattern = "http://images.nypl.org/index.php?id=%s&t=b"
imageExt = "jpg"

successCount = 0
skipCount = 0
failCount = 0

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)
    # pprint(item)
    # look for capture; if found, download the first one
    if 'captureIds' in item and len(item['captureIds']) > 0:
        captureId = item['captureIds'][0]
        if "," in captureId:
            captureId = captureId.split(",")[0]
        imageURL = imageURLPattern % captureId
        fileName = OUTPUT_DIR + "/" + captureId + "." + imageExt
        # save file if not found or overwrite is set to True
        if overwriteExisting or not os.path.isfile(fileName):
            with open(fileName, 'wb') as f:
                try:
                    f.write(urllib2.urlopen(imageURL).read())
                    f.close()
                    successCount += 1
                    print "Downloaded " + imageURL
                except URLError, e:
                    failCount += 1
                    print "Error: " + imageURL + " (" + e.reason + ")"
                except:
                    failCount += 1
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
        else:
            skipCount += 1
            # print "Skipped " + imageURL
    else:
        skipCount += 1
        print "No Captures: " + item['_id']

print "Downloaded " + str(successCount) + " images."
print "Skipped " + str(skipCount) + " images."
print "Failed to download " + str(failCount) + " images."
