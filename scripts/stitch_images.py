# -*- coding: utf-8 -*-

# Description: stitches together item captures into one image
# Example usage:
#   python stitch_images.py ../data/captures.json ../img/items/ ../img/items_100_10x10.jpg 100 10 10

from PIL import Image
import json
import math
import os
import sys

# input
if len(sys.argv) < 6:
    print "Usage: %s <inputfile item captures json> <inputdir of images> <outputfile for stitched image> <images per row> <image cell width> <image cell height>" % sys.argv[0]
    sys.exit(1)
INPUT_FILE = sys.argv[1]
INPUT_IMAGE_DIR = sys.argv[2]
OUTPUT_FILE = sys.argv[3]
ITEMS_PER_ROW = int(sys.argv[4])
ITEM_W = int(sys.argv[5])
ITEM_H =  int(sys.argv[6])

# config
imageExt = "jpg"

# init items
items = []
with open(INPUT_FILE) as data_file:
    items = json.load(data_file)
itemCount = len(items)
print "Loaded " + str(itemCount) + " items..."

# init
rows = int(math.ceil(itemCount / ITEMS_PER_ROW))
imageW = ITEM_W * ITEMS_PER_ROW
imageH = rows * ITEM_H
x = 0
y = 0
failCount = 0
skipCount = 0

# Create blank image
print "Creating blank image at (" + str(imageW) + ", " + str(imageH) + ")"
imageBase = Image.new("RGB", (imageW, imageH), "black")

for captureId in items:
    # Determine x/y
    if x >= imageW:
        x = 0
        y += ITEM_H
    # Try to paste image
    if captureId:
        fileName = INPUT_IMAGE_DIR + captureId + "." + imageExt
        try:
            im = Image.open(fileName)
            im.thumbnail((ITEM_W, ITEM_H), Image.NEAREST)
            imageBase.paste(im, (x, y))
            print "Pasted " + fileName
        except IOError:
            print "Cannot read file: " + fileName
            failCount += 1
        except:
            print "Unexpected error:", sys.exc_info()[0]
            failCount += 1
            raise
    else:
        skipCount += 1
    x += ITEM_W

# Save image
print "Saving stiched image..."

imageBase.save(OUTPUT_FILE)

print "Saved image: " + OUTPUT_FILE
print "Failed to add " + str(failCount) + " images."
print "Skipped " + str(skipCount) + " images."
