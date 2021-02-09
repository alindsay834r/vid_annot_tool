# 
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
# History (when, who, what):
# 20210208, alindsay834r, initial release
#
# config.py
# vid_annot_tool configuration parameters
#

# default input video file path
default_ivfdir = './'
# default input annotations path
default_iafdir = './'
# default output path
default_odir = './'

# annotation box size
annot_box_size = 50

# label specific settings
#[label, display on/off, annot color]
# color options = ['Red','Orange','Yellow','Green','Cyan','Blue','Purple','Magenta','Black','White']
# if a label is not listed, it will default to display-on/red
#EXAMPLE
#default_label_sel = [['navyshirt',True,'Blue'], 
#					 ['greenshirt',False,'Green']]
default_label_sel = []