#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script uses the DaVinci Resolve API to render a specific preset,
# import the rendered file back into DaVinci, and insert it into the timeline.
# The preset to be rendered is specified as "MIXDOWN".
#
# If in and out points are set by the user, only the selected range will be rendered.
# If no in and out points are set, the whole timeline will be rendered.
#
# The render output will be set to the media destination of the first clip in Video track 1.
# The rendered file will be imported back into DaVinci and placed in the
# "Mixdown" folder under a "Media" bin.
#
# The file will then be inserted into a new Video track in the timeline.

import os
import time
import uuid
import ntpath
from pathlib import Path
import DaVinciResolveScript as bmd

def getFolder(parentFolder, childFolder, mp):
    '''
    This function searches for a specific child folder within a parent folder
    in the DaVinci Resolve media pool.
    If the child folder exists within the parent folder,
    the function returns the child folder object.
    If the child folder does not exist, the function
    creates it and returns the newly created child folder object.
    Parameters:
        - parentFolder (Folder): The parent folder to search within.
        - childFolder (str): The name of the child folder to search for or create.
        - mp (MediaPool): The DaVinci Resolve MediaPool object.

    Returns:
        Folder: The child folder object, either existing or newly created.
    '''
    if childFolder in [folder.GetName() for folder in parentFolder.GetSubFolderList()]:
        for folder in parentFolder.GetSubFolderList():
            if folder.GetName() == childFolder:
                return folder
    else:
        return mp.AddSubFolder(parentFolder , childFolder)

# Getting Resolve objects
resolve = bmd.scriptapp('Resolve')
mediaStorage = resolve.GetMediaStorage()
projectManager = resolve.GetProjectManager()
proj = projectManager.GetCurrentProject()
mediaPool = proj.GetMediaPool()
tl = proj.GetCurrentTimeline()
startFrame = tl.GetCurrentVideoItem().GetStart()
videoTrackCount = tl.GetTrackCount('video')
video1Clips = tl.GetItemListInTrack('video', 1)
tc = tl.GetCurrentTimecode().replace(':', '.')
firstClip = ''

# Get the first clip of video track 1 at the inPoint.
for f in video1Clips:
    if f.GetStart() == startFrame:
        firstClip = f
        break

# Getting the firstClip source path and creating 'Mixdown' dir if nedded.
base, ext = os.path.splitext(firstClip.GetName())
suffix = uuid.uuid1().hex[:6]
mixdownName = f'{tl.GetName()}_Mixdown_{tc}_{suffix}'
parrentFolder = Path(os.path.dirname(firstClip.GetMediaPoolItem().GetClipProperty()['File Path']))
destFolder = Path(str(parrentFolder) + '/Mixdown')
Path(destFolder).mkdir(parents=True, exist_ok=True)

# Loading output preset and setting up parameters.
proj.LoadRenderPreset('MIXDOWN')
proj.SetRenderSettings({
    "CustomName": str(mixdownName),
    "TargetDir": str(destFolder)})

# Render
proj.AddRenderJob()
jobId = proj.GetRenderJobList()[-1]['JobId']
proj.StartRendering(jobId)

while proj.IsRenderingInProgress():
    time.sleep(1)

# Import the new render output to a specific bin.
os.chdir(destFolder)
dest = os.getcwd()

# Go to Media/Mixdown/Timline bin or create one
masterFolder = mediaPool.GetRootFolder()
mediaFolder = getFolder(masterFolder, 'Media', mediaPool)
mediaPool.SetCurrentFolder(mediaFolder)
mixdownFolder = getFolder(mediaFolder, 'Mixdown', mediaPool)
mediaPool.SetCurrentFolder(mixdownFolder)
timelineFolder = getFolder(mixdownFolder, tl.GetName(), mediaPool)
mediaPool.SetCurrentFolder(timelineFolder)

# Import the file
files = mediaStorage.GetFiles(dest)
for f in files.values():
    fullName = ntpath.basename(f)
    name, ex = os.path.splitext(fullName)
    if name == mixdownName:
        mediaStorage.AddItemsToMediaPool(f)
        break

# Insert clip to timeline
resolve.OpenPage('edit')
for item in timelineFolder.GetClipList():
    if item.GetName() == fullName:
        item.SetClipColor('Green')
        endClip = item.GetClipProperty('End')
        mediaPool.AppendToTimeline([{'mediaPoolItem':item, 'startFrame': 0,
                                     'endFrame': endClip, 'mediaType': 1,
                                     'trackIndex': videoTrackCount+1,
                                     'recordFrame': startFrame}])

projectManager.SaveProject()
