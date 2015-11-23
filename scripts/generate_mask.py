# -*- coding: utf-8 -*-

# Description: creates a mask/sprite for use in UI
# Example usage:
#   python generate_mask.py ../img/mask_100_50_10_10.png 100 50 10 10 10

import math
from PIL import Image
import sys

# input
if len(sys.argv) < 6:
    print "Usage: %s <outputfile> <items per row> <items per col> <item width> <item height> <steps>" % sys.argv[0]
    sys.exit(1)
OUTPUT_FILE = sys.argv[1]
ITEMS_PER_ROW = int(sys.argv[2])
ITEMS_PER_COL = int(sys.argv[3])
ITEM_W = int(sys.argv[4])
ITEM_H = int(sys.argv[5])
STEPS = int(sys.argv[6])

stepW = ITEMS_PER_ROW * ITEM_W
imageW = stepW * STEPS
imageH = ITEMS_PER_COL * ITEM_H
stepsPerStep = int(1.0 * ITEMS_PER_ROW * ITEMS_PER_COL / STEPS)
stepVelocity = 1.0 + 1.0 / STEPS
indexH = 0

# Create blank image
print "Creating blank image at (" + str(imageW) + " x " + str(imageH) + ")"
imageBase = Image.new("RGB", (imageW, imageH), "black")

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

sssteps = STEPS
for step in range(STEPS):
    for sstep in range(stepsPerStep):
        hx = halton(indexH, 3)
        hy = halton(indexH, 5)
        indexH += 1
        x = math.floor(hx * ITEMS_PER_ROW) * ITEM_W
        y = math.floor(hy * ITEMS_PER_COL) * ITEM_H
        x0 = stepW * (STEPS-1)
        for ssstep in range(sssteps):
            # draw box at x+x0,y
            img = Image.new("RGB", (ITEM_W, ITEM_H), "white")
            imageBase.paste(img, (int(x+x0), int(y)))
            x0 -= stepW
    sssteps -= 1
    stepsPerStep = int(stepVelocity * stepsPerStep)

# Save image
print "Saving stiched image..."
imageBase.save(OUTPUT_FILE)
