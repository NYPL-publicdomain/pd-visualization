# -*- coding: utf-8 -*-

# Description: stitches together item captures into one image
# Example usage:
#   python stitch_images.py ../data/ ../img/items/ ../img/ 100 10 10 default 50 20 3
#   python stitch_images.py ../data/ ../img/items/ ../img/ 100 10 10 centuries 50 20 3
#   python stitch_images.py ../data/ ../img/items/ ../img/ 100 10 10 collections 50 20 3
#   python stitch_images.py ../data/ ../img/items/ ../img/ 100 10 10 colors 50 20 3
#   python stitch_images.py ../data/ ../img/items/ ../img/ 100 10 10 genres 50 20 3

from PIL import Image
import json
import math
import os
import sys

# input
if len(sys.argv) < 10:
    print "Usage: %s <inputdir of data> <inputdir of images> <outputdir for image> <images per row> <image cell width> <image cell height> <data group>  <group item threshold> <group threshold> <min group rows>" % sys.argv[0]
    sys.exit(1)
INPUT_DATA_DIR = sys.argv[1]
INPUT_IMAGE_DIR = sys.argv[2]
OUTPUT_IMAGE_DIR = sys.argv[3]
ITEMS_PER_ROW = int(sys.argv[4])
ITEM_W = int(sys.argv[5])
ITEM_H =  int(sys.argv[6])
DATA_GROUP = sys.argv[7]
GROUP_ITEM_THRESHOLD = int(sys.argv[8])
GROUP_THRESHOLD = int(sys.argv[9])
MIN_GROUP_ROWS = int(sys.argv[10])

# config
imageExt = "jpg"

# init captures
captures = []
with open(INPUT_DATA_DIR + "captures.json") as data_file:
    captures = json.load(data_file)
itemCount = len(captures)
print "Loaded " + str(itemCount) + " captures..."

# init groups
groups = []
item_groups = []
group_filename = INPUT_DATA_DIR + DATA_GROUP + ".json"
items_group_filename = INPUT_DATA_DIR + "item_" + DATA_GROUP + ".json"
if os.path.isfile(group_filename) and os.path.isfile(items_group_filename):
    _groups = []
    with open(group_filename) as data_file:
        _groups = json.load(data_file)
    with open(items_group_filename) as data_file:
        item_groups = json.load(data_file)
    # Take out unknown group
    unknown = next(iter([g for g in _groups if not g['value']]), False)
    other = {
        'count': 0,
        'items': []
    }
    # Add items to appropriate groups
    for i,g in enumerate(_groups):
        if g['value']:
            item_ids = [item_i for item_i, group_i in enumerate(item_groups) if group_i == g['index']]
            # this group is too small; add to "other" group
            if g['count'] < GROUP_ITEM_THRESHOLD and len(_groups) > GROUP_THRESHOLD:
                other['items'].extend(item_ids)
                other['count'] += g['count']
            else:
                g['items'] = item_ids
                groups.append(g)
    # Add "other" group
    if other['count']:
        groups.append(other)

    # Add "uknown" group
    if unknown:
        unknown['items'] = [item_i for item_i, group_i in enumerate(item_groups) if group_i == unknown['index']]
        groups.append(unknown)
else:
    # Put everything in one big group
    groups.append({
        'items': range(itemCount),
        'count': itemCount
    })

# init
x = 0
y = 0
failCount = 0
skipCount = 0
count = 0

# calculate height
rows = int(math.ceil(1.0 * itemCount / ITEMS_PER_ROW))
imageW = ITEM_W * ITEMS_PER_ROW
imageH = rows * ITEM_H

if len(groups) > 1:
    rows = 0
    for g in groups:
        group_rows = int(math.ceil(1.0 * g['count'] / ITEMS_PER_ROW))
        if group_rows < MIN_GROUP_ROWS:
            group_rows = MIN_GROUP_ROWS
        rows += group_rows
    imageH = rows * ITEM_H

# Create blank image
print "Creating blank image at (" + str(imageW) + " x " + str(imageH) + ")"
imageBase = Image.new("RGB", (imageW, imageH), "black")

for g in groups:
    items = g['items']
    extra_rows = max(MIN_GROUP_ROWS - int(math.ceil(1.0 * g['count'] / ITEMS_PER_ROW)), 0)

    for itemId in items:
        captureId = captures[itemId]
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
                # print "Pasted " + fileName

                sys.stdout.write('\r')
                sys.stdout.write(str(round(1.0*count/itemCount*100,3))+'%')
                sys.stdout.flush()
            except IOError:
                # print "Cannot read file: " + fileName
                failCount += 1
            except:
                # print "Unexpected error:", sys.exc_info()[0]
                failCount += 1
                raise
        else:
            skipCount += 1
        x += ITEM_W
        count += 1

    # Add extra rows for small groups
    for extra_row in range(extra_rows):
        y += ITEM_H

    # Go to the next line for the next group
    x = 0
    y += ITEM_H

# Save image
print "Saving stiched image..."

outputfile = OUTPUT_IMAGE_DIR + DATA_GROUP + "_" + str(ITEMS_PER_ROW) + "_" + str(ITEM_W) + "_" + str(ITEM_H) + "." + imageExt
imageBase.save(outputfile)

print "Saved image: " + outputfile
print "Failed to add " + str(failCount) + " images."
print "Skipped " + str(skipCount) + " images."
