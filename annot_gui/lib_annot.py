# 
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
# Author: alinsday834r (alinsday834r@gmail.com, @alinsday834r)
# Date: 2021_02_07
# Version: 1.0
#
# lib_annot.py
# Functions for managing and drawing annotations.
#

import os
from tkinter import messagebox
import cv2
import numpy as np
import pandas as pd
import csv

# save annotations list to csv
def save_annotations_csv(annotations_list,afpath,verify_ow_flag):
	print('Saving '+afpath)
	# user verify if overwriting existing file
	if (verify_ow_flag is True) and (os.path.isfile(afpath)):
		ask_ow_file = messagebox.askokcancel('File Already Exists','Overwrite existing file?')
		if ask_ow_file is False:
			print('cancelled save')
			return
		else:
			print('overwriting existing file')
	# open annotation file
	fp = open(afpath,'w')
	# write annotations to file
	with fp:
		writer = csv.writer(fp)
		writer.writerows(annotations_list)
	# close annotation file
	fp.close
	return

# load annotations list from csv
def load_annotations_csv(afpath):
	print('Loading '+afpath)
	# open annotation file
	fp = open(afpath,'r')
	# write annotations to file
	with fp:
		reader = csv.reader(fp)
		annotations_list = list(reader)
	# close annotation file
	fp.close
	# values are read in as strings; convert time and positions to ints
	annotations_list= [([i[0]]+[int(float(j)) for j in i[1:]]) for i in annotations_list]
	return annotations_list

# define function to draw annotations on image
def draw_annotations(disp_annot_flag,frame,iFrame,nFrames,annotations_list,label,label_sel):
	# write annotations on frame
	if disp_annot_flag is 1:
		# write frame number on frame
		fInfo_text = 'frame {} of {}'.format(iFrame+1,nFrames)
		frame = cv2.putText(frame,fInfo_text,(5,frame.shape[0]-10), \
							cv2.FONT_HERSHEY_SIMPLEX,.8,(0,0,255),1)
		# if there are entries in list
		if len(annotations_list)>0:
			# convert annotations_list to a pandas dataframe
			annotations_df =  pd.DataFrame(annotations_list,columns=['label','x','y','iFrame'])
			# get list of unique labels
			unique_labels = set(annotations_df['label'])
			# loop through labels
			ilabel=-1
			for label in unique_labels:
				ilabel=ilabel+1
				if len(label_sel)>0:
					# find current label in label_sel
					label_sel_df =  pd.DataFrame(label_sel,columns=['label','rb_disp','color'])
					imatch = label_sel_df.index[label_sel_df['label']==label].tolist()
					# get display flag and color of label
					thedisplayflag = (label_sel[imatch[0]][1]).get()
					thecolortxt = (label_sel[imatch[0]][2]).get()
				else:
					thedisplayflag=True
					thecolortxt = 'Red'
				# set color of annotation box
				if thecolortxt == 'Red':
					color = (0,0,255) # red
				elif thecolortxt == 'Orange':
					color = (0,128,255) # orange
				elif thecolortxt == 'Yellow':
					color = (0,255,255) # yellow
				elif thecolortxt == 'Green':
					color = (0,255,0) # green
				elif thecolortxt == 'Cyan':
					color = (255,255,0) # cyan
				elif thecolortxt == 'Blue':
					color = (255,0,0) # blue
				elif thecolortxt == 'Purple':
					color = (255,51,153) # blue
				elif thecolortxt == 'Magenta':
					color = (255,0,255) # magenta
				elif thecolortxt == 'Black':
					color = (0,0,0) # black
				elif thecolortxt == 'White':
					color = (255,255,255) # white
				else:
					color = (0,0,255) # red
				# if annotations display selections are true for label, display annotations 
				if thedisplayflag is True:
					# extract frame index and positions as ndarrays
					ip = (annotations_df.loc[(annotations_df.label==label), 'iFrame']).values
					xp = (annotations_df.loc[(annotations_df.label==label), 'x']).values
					yp = (annotations_df.loc[(annotations_df.label==label), 'y']).values
					# assume that list is sorted by label, then by frame index
					if iFrame < ip[0]:
						center_point=(xp[0],yp[0])
						interp_marker = '-' # indicates current frame is before first annotation
					elif iFrame > ip[-1]:
						center_point=(xp[-1],yp[-1])
						interp_marker = '+' # indicates current frame is after last annotation
					else:
						try:
							i = list(ip).index(iFrame)
							center_point = (xp[i],yp[i])
							interp_marker = '' # indicates current frame is in annotation list
						except ValueError:
							center_point = (round(np.interp(iFrame,ip,xp)), \
											round(np.interp(iFrame,ip,yp)))
							interp_marker = '*' # indicates current frame is interpolated position
					# set annotation box size
					hwbox = 50
					# compute annotation box corner positions
					start_point = (max(center_point[0]-hwbox,0),max(center_point[1]-hwbox,0))
					end_point = (max(center_point[0]+hwbox,0),max(center_point[1]+hwbox,0))
					# add annotation box to frame
					frame = cv2.rectangle(frame, start_point, end_point, color, thickness=2)
					# add annotation label to frame
					frame = cv2.putText(frame,label,(start_point[0],max(start_point[1]-5,0)), \
										cv2.FONT_HERSHEY_SIMPLEX,.5,color,1)
					# add annotation inter marker to frame
					frame = cv2.putText(frame,interp_marker,(start_point[0]+5,start_point[1]+10), \
										cv2.FONT_HERSHEY_SIMPLEX,.5,color,1)
				
	return frame
