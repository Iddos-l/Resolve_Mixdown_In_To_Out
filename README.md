
# MIXDOWN2
`Render out in out portion of the timeline and insert to timeline`

This script uses the DaVinci Resolve API to render a specific preset,
import the rendered file back into DaVinci, and insert it into the timeline.
The preset to be rendered is specified as "MIXDOWN".

If in and out points are set by the user, only the selected range will be rendered.
If no in and out points are set, the whole timeline will be rendered.

The render output will be set to the media destination of the first clip in Video track 1.
The rendered file will be imported back into DaVinci and placed in the
"Mixdown" folder under a "Media" bin.

The file will then be inserted into a new video track in the timeline.

### Requirements
* python3
* DaVinci Resolve 18 and above

### Usage
Save a preset render name: "MIXDOWN".
Selcet the region of the timeline to render with in out points.
Run the script.

### Known Issues
Make sure there are more than one video track in the timeline and that the "Auto Track Selector" is enabled above track video 1. If these conditions are not met, the script may not work as expected.
