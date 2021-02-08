# 
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
# Author: alinsday834r (alinsday834r@gmail.com, @alinsday834r)
# Date: 2021_02_07
# Version: 1.0
#
# main.py
# Main executable.  Creates primary GUI window and passes 
# it to AnnotGUI to create all other elements.
#

import tkinter as tk
import annot_gui.lib_gui as lg

# create the root widget (graphical window)
window=tk.Tk()

# populate the root widget with the Annotation Tool
lg.AnnotGUI(window)







