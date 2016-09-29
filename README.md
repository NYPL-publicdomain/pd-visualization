# NYPL Public Domain Release 2016 Visualization

On January 6th, 2016, The New York Public Library made 187,000 digital items in the public domain available for high resolution download. This is a visualization and interface that helps users explore what was contained in that release.

View the visualization here: [http://publicdomain.nypl.org/pd-visualization/](http://publicdomain.nypl.org/pd-visualization/)

## Building the Visualization

To generate the images and data that powers the UI, a number of python scripts have been made to crunch the data

1. Download and unzip a [data dump](https://s3.amazonaws.com/labs.nypl.org/publicdomain/pd_mms_items.ndjson.gz) of NYPL items
2. Run the following scripts to extract necessary item categories
  - [get_captures.py](scripts/get_captures.py) retrieves capture ids to retrieve the images
  - [get_dates.py](scripts/get_dates.py) retrieves the creation dates from the items
  - [get_genres.py](scripts/get_genres.py) retrieves the genres from the items
  - [get_collections.py](scripts/get_collections.py) retrieves the collections from the items
3. Run [download_images.py](scripts/download_images.py) to download all the images of the first captures of the items
4. Run [get_color_data.py](scripts/get_color_data.py) and [get_colors.py](scripts/get_colors.py) to get the colors from the images
5. Run [stitch_images.py](scripts/stitch_images.py) to stitch together the images for each item category
6. The following scripts do some pre-processing for the UI:
  - [generate_metadata.py](scripts/generate_metadata.py) - loads all the metadata (title, description, uuid, etc) for the item thumbnail preview
  - [generate_labels.py](scripts/generate_labels.py) - generates the labels and counts for the righthand column in the UI
  - [generate_coordinates.py](scripts/generate_coordinates.py) - generates the pixel coordinates of each item for each collection for easy look-up on hover

---
### About the NYPL Public Domain Release

On January 6, 2016, The New York Public Library enhanced access to public domain items in Digital Collections so that everyone has the freedom to enjoy and reuse these materials in almost limitless ways. For all such items the Library now makes it possible to download the highest resolution images available directly from the [Digital Collections](http://digitalcollections.nypl.org) website.

That means more than 187,000 items free to use without restriction! But we know that 180K of anything is a lot to get your head around — so as a way to introduce you to these collections and inspire new works, NYPL Labs developed a suite of [projects and tools](http://nypl.org/publicdomain) to help you explore the vast collections and dive deep into specific ones.

Go forth, reuse, and let us know what you made with the #nyplremix hashtag! For more information:

- [NYPL Labs Remix Residency](http://www.nypl.org/help/about-nypl/fellowships-institutes/remix)
- [Data & Tools](https://github.com/NYPL-publicdomain/data-and-utilities)
- [Public Domain Collections](http://publicdomain.nypl.org)
- [Project Credits](https://github.com/NYPL-publicdomain/nypl-publicdomain.github.io#credits-for-the-january-2016-nypl-public-domain-release)
