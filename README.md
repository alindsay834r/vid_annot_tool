# vid_annot_tool
python tool to annotate video frames


DESCRIPTION:
Python GUI tool to annotate video frames. Allows user to select video. Displays video one frame at a time. Allows user to choose frame increment (positive or negative) and user can then either step through video one frame at a time or play video. Allows user to click displayed frame to indicate where target is located, and stores location in list. Target location annotation is then added to displayed frame. Target location annotation position is interpolated for frames that don't have a defined annotation.  Allows user to store annotations list in *.csv file, which can be re-loaded.  Allows user to select which target annotations to display and what color.  Allows user to save video with annotations (only supports output *.mp4 format).


DEPENDENCIES:
python 3
pandas
opencv-python3
Tkinter
pillow

tool has only been tested on Linux with Python3
tool has only been test to load *.mp4 videos
tool only outputs *.mp4 videos and *.csv annotation files


EXECUTING PROGRAM:
update config.py as desired
run main.py


TYPICAL WORKFLOW:
0. UPDATE CONFIG FILE - update config.py; set paths to default input/output dirs; set default annotation settings
1. EXECUTE MAIN - execute main.py
2. LOAD VIDEO - to load video file click "Load Video" button, or type "v"; select video file; loads video and displays first frame in GUI; if annotations *.csv file with same file name exists on default path it will also be loaded automatically
3. note that once video file is loaded "Frame Increment" selections become available on "MAIN MENU" and "ANNOTS MENU" pops out
4. LOAD ANNOTATION CSV FILE - to load an annotations.csv file, click "Load Annots" button or type 'a'; select annotations file; loads annotations; note this function does not verify the annots file actually belongs to the video file
5. NAVIGATE THROUGH VIDEO FILE - use up/down arrow buttons, or up/down arrow keys to change frame increment value, or type value into entry bow; if invalid value entered, box will revert to last valid value; type "-" to negate increment value
6. use "1"/left arrow/right arrow/"end" buttons, or type "Home"/left arrow/right arrow/"End" keys to step through video frames at frame increment value
7. click "Play/Pause" button, or type "p" to play/pause the video
8. click "ANNOTS MENU" toggle button to pop out/in "ANNOTS MENU"
9. click "SAVE VID MENU" toggle button to pop out/in "SAVE VID MENU"
10. MANAGE ANNOTATIONS - to add new target to annotations list, select "NEW TARGET" from list under "ANNOTS MENU" and left click on target in displayed frame; answer pop-up box asking for new target label; "ANNOTS MENU" will automatically update; annotation will be added to annotations list and annotation will be added to displayed frame
11. to add an annotation for an existing target, select desired target from list under "ANNOTS MENU" and left click on target in displayed frame; annotation will be added to annotations list and annotation will be added to displayed frame
12. to delete an annotation, select desired target from list under "ANNOTS MENU" and right click on displayed frame, annotation will be deleted from annotations list and annotation will be updated on displayed frame
13. note that once an annotation is added to the annotations list, an annotation will be added for that label to every displayed frame; the upper left corner of the annotation box contains a marker: - denotes a frame that comes before the first annotation, * denotes an interpolated position, nothing denotes an annotation for that specific frame, + denotes a frame that comes after the last annotation
14. the option to display/not display annotations, and choose color of displayed annotations for each label is available on the "ANNOTS MENU"; defaults for specific labels can be set in the config file
15. SAVE ANNOTATION CSV FILE - to save annotations list to *.csv, pop out "ANNOTS MENU" and click "Save Annots" button
16. SAVE ANNOTATED MP4 VIDEO - to save an annotated video to *.mp4, pop out "SAVE VID MENU", type in output name, and start/stop frame values and click "Save" button; video will be save at resolution and frame rate of original video with currently selected annotations; GUI freezes while frames are saving, and status messages are printed to command line
17. note if GUI window is resized, displayed frame will automatically resize to fit


OUTPUT INFO:
annotations file fields: label, xpos, ypos, iframe


AUTHOR:
alindsay834r (alindsay834r@gmail.com, @alindsay834r)


VERSION HISTORY
0.1, 2021_02_08, initial release


LICENSE
This file is subject to the terms and conditions defined in
file 'LICENSE.txt', which is part of this source code package.