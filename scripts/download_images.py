# -*- coding: utf-8 -*-

# Description: downloads the smallest cropped image captures from a list of items
# Example usage:
#   python download_images.py ../data/captures.json ../img/items/ b
# Derivative types:
#   t: 150
#   b: 100 (cropped)
#   f: 192
#   r: 300
#   w: 760
#   q: 1600
#   v: 2560
#   g: Original

import json
import os
from PIL import Image
import sys
import urllib2

# input
if len(sys.argv) < 2:
    print "Usage: %s <inputfile item captures json> <outputdir for images> <derivative code>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
DERIVATIVE_CODE = sys.argv[3]

# config
overwriteExisting = False
imageURLPattern = "http://images.nypl.org/index.php?id=%s&t=" + DERIVATIVE_CODE
imageExt = "jpg"

items = []
count = 0
successCount = 0
skipCount = 0
failCount = 0

def isValidImage(fileName):
    isValid = True
    try:
        im=Image.open(fileName)
        # do stuff
    except IOError:
        # filename not an image file
        isValid = False
    except:
        isValid = False
    return isValid

with open(INPUT_FILE) as data_file:
    items = json.load(data_file)
itemCount = len(items)
print "Downloading " + str(itemCount) + " captures..."

for captureId in items:
    imageURL = imageURLPattern % captureId
    fileName = OUTPUT_DIR + captureId + "." + imageExt
    # save file if not found or overwrite is set to True
    if overwriteExisting or not os.path.isfile(fileName) or not isValidImage(fileName):
        with open(fileName, 'wb') as f:
            try:
                f.write(urllib2.urlopen(imageURL).read())
                f.close()
                successCount += 1
                print str(count) + ". Downloaded " + imageURL + " (" + str(round(1.0 * count / itemCount * 100, 3)) + "%)"
            except urllib2.URLError, e:
                failCount += 1
                print str(count) + ". URL error: " + imageURL , e.args
            except:
                failCount += 1
                print str(count) + ". Unexpected error: " + imageURL , sys.exc_info()[0]
                raise
    else:
        skipCount += 1
        # print str(count) + ". Skipped " + imageURL
    count += 1

print "Downloaded " + str(successCount) + " images."
print "Skipped " + str(skipCount) + " images."
print "Failed to download " + str(failCount) + " images."
