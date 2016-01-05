# -*- coding: utf-8 -*-

# Description: generates a mosaic image based on a list of UUIDs
# Example usage:
#   python make_mosaic.py ../data/src/pd_items.json ../img/mosaic_800x480.jpg w 800 480 0.2 0.66 10

import json
import math
import os
from PIL import Image
from pprint import pprint
import re
import sys
import urllib2

# input
if len(sys.argv) < 8:
    print "Usage: %s <inputfile items json> <output file> <derivative size> <target w> <target h> <cell h start multiplier> <cell h multiplier> <min cell h>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
DERIV_CODE = sys.argv[3]
IMAGE_W = int(sys.argv[4])
IMAGE_H = int(sys.argv[5])
CELL_H_MULTIPLIER_START = float(sys.argv[6])
CELL_H_MULTIPLIER = float(sys.argv[7])
MIN_CELL_H = int(sys.argv[8])

# config
imageURLPatternFind = '^http://images\.nypl\.org/index\.php\?id=([^&]+)&t=g$'
imageURLPattern = "http://images.nypl.org/index.php?id=%s&t=" + DERIV_CODE
tmpFolder = "../tmp/"
imageExt = "jpg"
overwriteExisting = False

# a list of item/collection UUIDs
uuids = [
    '812e5770-c60c-012f-7167-58d385a7bc34',
    # 'e5462600-c5d9-012f-a6a3-58d385a7bc34',
    '9ea5d5b0-1117-0132-7932-58d385a7b928',
    '56605f50-c6cc-012f-3e5a-58d385a7bc34',
    'ab394b60-d4bc-0131-8bd5-58d385a7bbd0',
    '8031e230-c612-012f-3daf-58d385a7bc34',
    # 'd533f0b0-c5ca-012f-d4a0-58d385a7bc34',
    # '6c7dc4f0-c5f5-012f-ff48-58d385a7bc34',
    # '34007fd0-c6d2-012f-5566-58d385a7bc34',
    '0c73c6d0-c62b-012f-f421-58d385a7bc34',
    '2c2da8e0-c6da-012f-0f26-58d385a7bc34',
    # '35301010-c58d-012f-1196-58d385a7bc34',
    # 'e020e560-c62d-012f-a0f9-58d385a7bc34',
    'f1c763b0-c5dd-012f-5b39-58d385a7bc34',
    # '41394870-c6b7-012f-942c-3c075448cc4b'
    '28d304b0-c612-012f-cd39-58d385a7bc34'
]
excludeCaptures = [
    '1229586',
    '1229587',
    '1229595',
    '1229594',
    '1229616',
    '1161039',
    '5206296',
    '1229601',
    '419504',
    '1229590',
    '1229610',
    '1229611',
    '1229583',
    '1229582',
    '419559',
    '1229614',
    '1229565',
    '1229596',
    '1229569',
    '1229593',
    '1229580',
    '5214877',
    '419556',
    '1229604',
    '1229584',
    '1229608',
    '1229568'
]

# init
captureIds = []
images = []
imageCount = 0
randomBase = 3

# calculations
cellH = CELL_H_MULTIPLIER_START * IMAGE_W
x = 0
y = 0
h = cellH
while y < IMAGE_H:
    if x > IMAGE_W:
        y += h
        x = 0
        h *= CELL_H_MULTIPLIER
        h = max(h, MIN_CELL_H)
    x += h
    imageCount += 1
imageCount = int(imageCount * 1.5) # add some padding

print "Requiring %s valid images" % imageCount
print "Looking for images..."

for line in open(INPUT_FILE,'r').readlines():
    # Read line as json
    item = json.loads(line)
    captureId = ""

    # no captures
    if not "captures" in item or len(item["captures"]) <= 0:
        continue

    # item not in list of UUIDs
    # if not ("collectionUUID" in item and item["collectionUUID"] in uuids) and not ("UUID" in item and item["UUID"] in uuids):
    if not ("collectionUUID" in item and item["collectionUUID"] in uuids):
        continue

    capture = item["captures"][0]
    match = re.search(imageURLPatternFind, capture)
    if match:
        captureId = match.group(1).strip()
    if not captureId:
        continue

    captureIds.append(captureId)

captureCount = len(captureIds)
print "Found %s valid images" % captureCount
if captureCount < imageCount:
    print "Too few images found"
    sys.exit(1)

# For creating pseudo-random numbers
def halton(index, base):
    result = 0.0
    f = 1.0 / base
    i = 1.0 * index
    while(i > 0):
        result += f * (i % base)
        i = math.floor(i / base)
        f = f / base
    return result

# Sample images pseudo-randomly
for i in range(imageCount):
    h = halton(i, randomBase)
    captureId = captureIds[int(h * captureCount)]
    if captureId in excludeCaptures:
        continue

    # See if file exists or overwrite is set to True
    fileName = tmpFolder + captureId + "." + imageExt
    if overwriteExisting or not os.path.isfile(fileName):

        # Download image
        imageURL = imageURLPattern % captureId
        with open(fileName, 'wb') as f:
            try:
                f.write(urllib2.urlopen(imageURL).read())
                f.close()
                print str(i+1) + ". Downloaded " + imageURL + " (" + str(round(1.0 * i / imageCount * 100, 3)) + "%)"
                images.append(fileName)
            except urllib2.URLError, e:
                print str(i+1) + ". URL error: " + imageURL , e.args
            except:
                print str(i+1) + ". Unexpected error: " + imageURL , sys.exc_info()[0]
                raise

    else:
        images.append(fileName)

print "Retrieved %s images" % len(images)

# Create blank image
print "Creating blank image at (" + str(IMAGE_W) + " x " + str(IMAGE_H) + ")"
imageBase = Image.new("RGB", (IMAGE_W, IMAGE_H), "black")

x = 0
y = 0
h = int(cellH)
for fileName in images:

    if y > IMAGE_H:
        break

    try:
        im = Image.open(fileName)
        imW, imH = im.size
        ratio = 1.0 * imW / imH

        if x > IMAGE_W:
            y += h
            x = 0
            h *= CELL_H_MULTIPLIER
            h = int(max(h, MIN_CELL_H))

        w = int(h * ratio)
        im.thumbnail((w, h), Image.ANTIALIAS)
        imageBase.paste(im, (x, y))

        x += w

    except IOError:
        print "Cannot read file: " + fileName
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

# Save image
print "Saving stiched image..."
imageBase.save(OUTPUT_FILE)
print "Saved image: " + OUTPUT_FILE
