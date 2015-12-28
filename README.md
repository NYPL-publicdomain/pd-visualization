# NYPL Public Domain Release 2016 Visualization

To generate the images and data that powers the UI:

1. Download a [data dump](https://github.com/NYPL-publicdomain/digital-collections-pd-data-and-tools) of NYPL items
2. Run the following scripts to extract necessary item categories
  - [get_captures.py](scripts/get_captures.py) retrieves capture ids to retrieve the images
  - [get_dates.py](scripts/get_dates.py) retrieves the creation dates from the items
  - [get_genres.py](scripts/get_genres.py) retrieves the genres from the items
  - [get_collections.py](scripts/get_collections.py) retrieves the collections from the items
3. Run [download_images.py](scripts/download_images.py) to download all the images of the first captures of the items
4. Run [get_colors.py](scripts/get_colors.py) to get the colors from the images
5. Run [stitch_images.py](scripts/stitch_images.py) to stitch together the images for each item category
6. The following scripts do some pre-processing for the UI:
  - [generate_metadata.py](scripts/generate_metadata.py) - loads all the metadata (title, description, uuid, etc) for the item thumbnail preview
  - [generate_labels.py](scripts/generate_labels.py) - generates the labels and counts for the righthand column in the UI
  - [generate_coordinates.py](scripts/generate_coordinates.py) - generates the pixel coordinates of each item for each collection for easy look-up on hover
