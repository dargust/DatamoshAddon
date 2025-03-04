# Blender Datamosh Addon

This Blender addon allows users to perform datamoshing on video clips rendered from Blender's Video Sequence Editor (VSE). It automatically identifies transition points between clips and applies the datamoshing effect to the rendered video.

## Features

- Automatically detects transition points between video clips in the VSE.
- Processes the rendered MP4 video to create a datamoshed version.
- Simple user interface with a button to trigger the datamoshing process.

## Installation

1. Download or clone the repository.
2. Open Blender and navigate to `Edit > Preferences > Add-ons`.
3. Click on `Install...` and select the `blender-datamosh-addon` directory.
4. Enable the addon by checking the box next to its name in the Add-ons list.

## Usage

1. Render your video using Blender's Video Sequence Editor.
2. Open the Video Sequence Editor and locate the panel for the Datamosh addon.
3. Click the "Datamosh" button to process the rendered video.
4. The addon will automatically grab the transition points and apply the datamoshing effect.

## Standalone Usage

1. Change the input file and frame data in the parse_raw_avi.py file
2. Run the parse_raw_avi.py as a standalone python script

## Dependencies

- Blender 2.8 or higher
- Python 3.7 or higher