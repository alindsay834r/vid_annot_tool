# 
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
# History (when, who, what):
# 20210208, alindsay834r, initial release
#
# lib_gui.py
# Given a window, builds GUI and updates GUI inside.
#

import os
from pathlib import Path
import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd

import annot_gui.lib_annot as la
import config

class AnnotGUI():
	def __init__(self, window):
		# set window variable
		self.window = window
		self.window.title('no video loaded')
		# init gui settings
		self.maingui2_flag = -1
		self.savvgui_flag = -1
		self.annotgui_flag = -1
		# init VideoCapture and display object variables
		self.ivfpath = None
		self.cap = None
		self.iframe = None
		self.nframe = None
		self.scale = 1
		self.ppv_flag = -1
		self.incv_flag = -1
		self.decv_flag = -1
		self.goto0_flag = -1
		self.gotoEnd_flag = -1
		self.valid_ent_inc_val = 1
		self.interval_ms = 1
		# init annotations  variables
		self.annotations_list = list()
		self.label_list = list()
		self.annot_menu_label_sel = list()
		self.sframe_label_sel = None
		self.rb_label_sel_var = tk.StringVar(self.window,'NEW TARGET')
		self.disp_annot_flag = 1
		# init save vid variables
		self.cap2 = None
		self.ovid = None
		# create side bar for menus, initilialize with main menu 1
		self.rbar = tk.Frame(self.window)
		self.rbar.pack(expand=False, fill=tk.BOTH, side=tk.RIGHT, anchor=tk.N)
		self.mainmenugui1()
		# create canvas for video images
		self.canvas = tk.Canvas(self.window)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		# add canvas mouse click callbacks elements
		self.canvas.bind('<Button-1>',self.add_annotation_callback)
		self.canvas.bind('<Button-3>',self.delete_annotation_callback)
		# update image on canvas (this function runs continuously)
		self.updatev()
		# mainloop
		self.window.mainloop()

	# close everything out when main window is destroyed
	def __del__(self):
		# Release the input video source when the window object is destroyed
		if self.cap is not None:
			if self.cap.isOpened():
				self.cap.release()
		# mainloop
		self.window.mainloop()

	# add main menu 1 to GUI - always present
	def mainmenugui1(self):
		# create main menu frame inside right bar
		self.rmenu1w = 15
		self.rmenu1 = tk.Frame(self.rbar, width=self.rmenu1w)
		self.rmenu1.pack(expand=False, side=tk.LEFT, anchor=tk.N)
		# add main menu title
		label_mainmenu1 = tk.Label(self.rmenu1,text='MAIN MENU',font='bold',width=self.rmenu1w)
		label_mainmenu1.pack(anchor=tk.CENTER, expand=False)
		# add load video button and key binding
		btn_loadv = tk.Button(self.rmenu1, text="Load Video (v)", width=self.rmenu1w, command=self.loadv)
		btn_loadv.pack(anchor=tk.CENTER, expand=False)
		self.window.bind('v',self.loadv)
		# add key bindings
		self.window.bind('<Escape>',lambda x: self.window.destroy())
		self.window.bind('q',lambda x: self.window.destroy())

	# add main menu 1 to GUI - appears after video is loaded
	def mainmenugui2(self):
		# only execute if menu is not already open
		if self.maingui2_flag is -1:
			self.maingui2_flag = 1
			# add frame increment title
			label_frame_inc = tk.Label(self.rmenu1,text='Frame Increment',width=self.rmenu1w)
			label_frame_inc.pack(anchor=tk.CENTER, expand=False)
			# create frame increment up/value/down frame (line on the GUI)
			frame_inc = tk.Frame(self.rmenu1, width=self.rmenu1w)
			frame_inc.pack(anchor=tk.CENTER, expand=False)
			# add frame decrement value button and key binding
			btn_dec_val = tk.Button(frame_inc, text=u"\u2193", width=1, command=self.dec_inc_val)
			btn_dec_val.pack(side=tk.LEFT, expand=False)
			self.window.bind('<Down>',self.dec_inc_val)
			# add frame increment value entry box
			self.ent_inc_val = tk.Entry(frame_inc,width=round(self.rmenu1w/2))
			self.ent_inc_val.pack(side=tk.LEFT, expand=False)
			self.ent_inc_val.insert(0,'1')
			# add frame increment value button and key binding
			btn_inc_val = tk.Button(frame_inc, text=u"\u2191", width=1, command=self.inc_inc_val)
			btn_inc_val.pack(side=tk.LEFT, expand=False)
			self.window.bind('<Up>',self.inc_inc_val)
			# add key binding to negate current frame increment value
			self.window.bind('-',self.neg_inc_val)
			# create start/back/fwd/end skip video frames frame (line on the GUI)
			frame_inc2 = tk.Frame(self.rmenu1, width=self.rmenu1w)
			frame_inc2.pack(anchor=tk.CENTER, expand=False)
			# add skip to first video frame button and key binding
			btn_goto0 = tk.Button(frame_inc2, text=u"1", width=1, command=self.goto0)
			btn_goto0.pack(side=tk.LEFT, expand=False)
			self.window.bind('<Home>',self.goto0)
			# add step back video frame button and key binding
			btn_inc_in = tk.Button(frame_inc2, text=u"\u2190", width=1, command=self.decv)
			btn_inc_in.pack(side=tk.LEFT, expand=False)
			self.window.bind('<Left>',self.decv)
			# add step forward video frame button and key bindings
			btn_inc_out = tk.Button(frame_inc2, text=u"\u2192", width=1, command=self.incv)
			btn_inc_out.pack(side=tk.LEFT, expand=False)
			self.window.bind('<Return>',self.incv)
			self.window.bind('<KP_Enter>',self.incv)
			self.window.bind('<Right>',self.incv)
			# add skip to last video frame button and key binding
			btn_gotoEnd = tk.Button(frame_inc2, text=u"End", width=1, command=self.gotoEnd)
			btn_gotoEnd.pack(side=tk.LEFT, expand=False)
			self.window.bind('<End>',self.gotoEnd)
			# add play/pause video button and key binding
			btn_ppv = tk.Button(self.rmenu1, text="Play/Pause (p)", width=self.rmenu1w, command=self.ppv)
			btn_ppv.pack(anchor=tk.CENTER, expand=False)
			self.window.bind('p',self.ppv)
			# add annots menu toggle frame
			frame_annot_label = tk.Frame(self.rmenu1, width=self.rmenu1w)
			frame_annot_label.pack(anchor=tk.CENTER, expand=False)
			# add annots menu label
			label_annot = tk.Label(frame_annot_label,text='ANNOTS MENU',width=self.rmenu1w-1)
			label_annot.pack(side=tk.LEFT, expand=False)
			# add annots menu toggle button
			self.btn_annot_toggle = tk.Button(frame_annot_label, text=">", width=1, command=self.annotmenugui)
			self.btn_annot_toggle.pack(side=tk.LEFT, expand=False)
			# add save vid menu toggle frame
			frame_savv_label = tk.Frame(self.rmenu1, width=self.rmenu1w)
			frame_savv_label.pack(anchor=tk.CENTER, expand=False)
			# add save vid menu label
			label_savv = tk.Label(frame_savv_label,text='SAVE VID MENU',width=self.rmenu1w-1)
			label_savv.pack(side=tk.LEFT, expand=False)
			# add save vid menu toggle button
			self.btn_savv_toggle = tk.Button(frame_savv_label, text=">", width=1, command=self.savvgui)
			self.btn_savv_toggle.pack(side=tk.LEFT, expand=False)

	# prompt user for path, load video
	def loadv(self,event=None):
		# get input video path
		new_ivfpath = filedialog.askopenfilename(initialdir = config.default_ivfdir)
		# verify path exists
		if len(new_ivfpath)>0:
			self.ivfpath = new_ivfpath
			print('Loading '+self.ivfpath)
			# if video currently open, close it
			if self.cap is not None:
				if self.cap.isOpened():
					self.cap.release()
			# create VideoCapture object
			self.cap = cv2.VideoCapture(self.ivfpath)
			# if video failed to open, clear video variables and return
			# this part is not fully error trapped
			if (self.cap.isOpened()==False):
				print ('Error opening '+self.ivfpath)
				self.canvas.delete('all')
				self.cap = None
				self.ivfpath = None
				self.iafpath = None
				self.annotations_list = list()
				self.annot_menu_label_sel = list()
				self.iframe = None
				self.nframe = None
				return
			# initialize frame id
			self.iframe = -1
			self.nframe = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
			# get frame rate of input video
			self.fps = self.cap.get(cv2.CAP_PROP_FPS)
			# get resolutions of input video
			frame_width = int(self.cap.get(3))
			frame_height = int(self.cap.get(4))
			self.vsize = (frame_width, frame_height)
			# set window title to name of file
			self.window.title(os.path.basename(self.ivfpath)+ \
				', frame {} of {}'.format(self.iframe+2,self.nframe))
			# if annotation file exists on default path, load it
			self.iafpath = config.default_iafdir+Path(self.ivfpath).stem+'.csv'
			if os.path.isfile(self.iafpath):
				self.annotations_list = la.load_annotations_csv(self.iafpath)
			# otherwise init to empty list
			else:
				self.annotations_list = list()
			# if annot menu is open, close it (to clear out)
			if self.annotgui_flag is 1:
				self.close_annotmenu()
				self.annot_menu_label_sel = list()
			# if save vid menu is open, close it
			if self.savvgui_flag is 1:
				self.close_savvmenu()
			# add the rest of main ui
			self.mainmenugui2()
			# open annot menu
			self.annotmenugui()

	# load annotations CSV file
	# note this function does not verify the annots file actually belongs to the video file
	def loada(self,event=None):
		# user verify if overwriting existing file
		if (len(self.annotations_list)>0):
			ask_ow_annots = messagebox.askokcancel('Overwriting Annotation!', \
				'Are you sure you want to overwrite the annotations currently in memory?')
			if ask_ow_annots is False:
				return
		# get input annotation file path
		iafpath = filedialog.askopenfilename(initialdir = config.default_iafdir)
		# verify path exists
		if len(iafpath)>0:
			self.annotations_list = la.load_annotations_csv(iafpath)
			# if annot menu is open, close it (to clear out)
			if self.annotgui_flag is 1:
				self.close_annotmenu()
				self.annot_menu_label_sel = list()
			# open annot menu
			self.annotmenugui()

	# save annotations to CSV file
	def sava(self,event=None):
		if (len(self.annotations_list)>0) and (self.iafpath is not None):
			initfilename = Path(self.iafpath).stem+'.csv'
			oafpath = filedialog.asksaveasfilename(initialdir=config.default_odir, \
				initialfile=initfilename,filetypes=[('csv file','*.csv')],confirmoverwrite=True)
			if len(oafpath)==0:
				print('cancelled save')
				return
			la.save_annotations_csv(self.annotations_list,oafpath)

	# toggle play/pause video flag
	def ppv(self,event=None):
		self.ppv_flag = -self.ppv_flag

	# toggle increment video flag
	def incv(self,event=None):
		self.incv_flag = -self.incv_flag

	# toggle deccrement video flag
	def decv(self,event=None):
		self.decv_flag = -self.decv_flag

	# skip to first frame of video
	def	goto0(self,event=None):
		self.goto0_flag = -self.goto0_flag

	# skip to last frame of video
	def	gotoEnd(self,event=None):
		self.gotoEnd_flag = -self.gotoEnd_flag

	# negate increment value
	def neg_inc_val(self,event=None):
		# try to get integer value from entry box
		try:
			inc_val = int(self.ent_inc_val.get())
			self.valid_ent_inc_val = int(self.ent_inc_val.get())
		# if increment input is not an integer, set it to last valid value
		except ValueError: 
			self.ent_inc_val.delete(0,tk.END)
			self.ent_inc_val.insert(0,str(self.valid_ent_inc_val))
			inc_val = int(self.ent_inc_val.get())
		# update value in entry box
		self.ent_inc_val.delete(0,tk.END)
		self.ent_inc_val.insert(0,str(-inc_val))

	# increase increment value
	def inc_inc_val(self,event=None):
		inc_val = int(self.ent_inc_val.get())
		if inc_val<-1000:
			inc_val=-1000
		elif inc_val>=-1000 and inc_val<-100:
			inc_val=-100
		elif inc_val>=-100 and inc_val<-25:
			inc_val=-25
		elif inc_val>=-25 and inc_val<-10:
			inc_val=-10
		elif inc_val>=-10 and inc_val<-5:
			inc_val=-5
		elif inc_val>=-5 and inc_val<5:
			inc_val=inc_val+1
		elif inc_val>=5 and inc_val<10:
			inc_val=10
		elif inc_val>=10 and inc_val<25:
			inc_val=25
		elif inc_val>=25 and inc_val<100:
			inc_val=100
		elif inc_val>=100 and inc_val<1000:
			inc_val=1000
		else:
			inc_val=inc_val+1
		# update value in entry box
		self.ent_inc_val.delete(0,tk.END)
		self.ent_inc_val.insert(0,str(inc_val))

	# decrease increment value
	def dec_inc_val(self,event=None):
		inc_val = int(self.ent_inc_val.get())
		if inc_val>1000:
			inc_val=1000
		elif inc_val<=1000 and inc_val>100:
			inc_val=100
		elif inc_val<=100 and inc_val>25:
			inc_val=25
		elif inc_val<=25 and inc_val>10:
			inc_val=10
		elif inc_val<=10 and inc_val>5:
			inc_val=5
		elif inc_val<=5 and inc_val>-5:
			inc_val=inc_val-1
		elif inc_val<=-5 and inc_val>-10:
			inc_val=-10
		elif inc_val<=-10 and inc_val>-25:
			inc_val=-25
		elif inc_val<=-25 and inc_val>-100:
			inc_val=-100
		elif inc_val<=-100 and inc_val>-1000:
			inc_val=-1000
		else:
			inc_val=inc_val-1
		# update value in entry box
		self.ent_inc_val.delete(0,tk.END)
		self.ent_inc_val.insert(0,str(inc_val))

	# update image
	def updatev(self):
		if self.cap is not None:
			if self.cap.isOpened():
				# read next frame
				ret, self.frame = self.cap.read()
				if ret:
					# increment iframe
					self.iframe=self.iframe+1
					# add annotations to frame
					self.frame = la.draw_annotations(self.disp_annot_flag, \
													self.frame, \
													self.iframe, \
													self.nframe, \
													self.annotations_list, \
													self.label_list, \
													self.annot_menu_label_sel, \
													config.annot_box_size)
					# convert to RGB
					self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
					# convert to PIL format
					self.frame = Image.fromarray(self.frame)
					# resize image to fit fully inside canvas
					fw = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
					fh = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
					cw = self.canvas.winfo_width()
					ch = self.canvas.winfo_height()
					self.scale = min(cw/fw,ch/fh)
					self.frame = self.frame.resize((int(fw*self.scale),int(fh*self.scale)), Image.ANTIALIAS)
					# convert to ImageTk format
					self.frame = ImageTk.PhotoImage(self.frame) 
					# update displayed image
					self.canvas.create_image(0, 0, image=self.frame, anchor = tk.NW)
					# cap.read() automatically increments forward 1 frame, 
					# compute any additional frame increment
					try:
						inc_val = int(self.ent_inc_val.get())
						self.valid_ent_inc_val = int(self.ent_inc_val.get())
					# if increment input is not an integer, set it to last valid value
					except ValueError: 
						self.ent_inc_val.delete(0,tk.END)
						self.ent_inc_val.insert(0,str(self.valid_ent_inc_val))
						inc_val = int(self.ent_inc_val.get())
					fskip = inc_val*(-self.decv_flag)-1
					# if flagged to jump to beginning of video
					if self.goto0_flag==1:
						self.iframe = 0
						fskip = -1
					# if flagged to jump to end of video
					if self.gotoEnd_flag==1:
						self.iframe = self.nframe-1
						fskip = -1
					# if not incrementing or decrementing and if video is paused, 
					# set fskip to -1 (repeat previous frame)
					elif (self.incv_flag is -1) and (self.decv_flag is -1) and (self.ppv_flag is -1):
						fskip = -1
					# if at end of video or beyond, point to end of video
					elif (self.iframe+fskip)>(self.nframe-2):
						self.iframe = self.nframe-1
						fskip = -1
					# if at beginning of video or before, point to first frame of video
					elif (self.iframe+fskip)<0:
						self.iframe = 0
						fskip = -1
					# if skipping a frame, point cap to desired frame
					if fskip!=0:
						# update frame id
						self.iframe = self.iframe+fskip
						# update frame position in cap
						self.cap.set(1,self.iframe+1)
					# update window title to name of file + frame id
					self.window.title(os.path.basename(self.ivfpath)+ \
						', frame {} of {}'.format(self.iframe+2,self.nframe))
		# always set video increment/decrement flag to false at end of update
		self.incv_flag = -1
		self.decv_flag = -1
		self.goto0_flag = -1
		self.gotoEnd_flag = -1
		# Repeat every 'interval' ms
		self.window.after(self.interval_ms, self.updatev)

	# add click positions to the annotations list
	def add_annotation_callback(self,event):
		# if video loaded, add annotation
		if self.cap is not None:
			# get target label
			label = self.rb_label_sel_var.get()
			# if 'NEW TARGET' selected, get target label from user
			new_label_flag = False
			if label=='NEW TARGET':
				new_label_flag = True
				label = simpledialog.askstring('Label','Enter new target label:')
				# if cancel, return without adding the annotation
				if (label is None) or (label==''):
					return
			# if annotation already exists for this label+frame, delete it
			if len(self.annotations_list)>0:
				for i in self.annotations_list:
					if (i[0]==label) and (i[3]==(self.iframe+1)):
						self.annotations_list.remove(i)
			# store new annotation in list
			unscaled_pos_x = round(event.x/self.scale)
			unscaled_pos_y = round(event.y/self.scale)
			self.annotations_list.append([label,unscaled_pos_x,unscaled_pos_y,self.iframe+1])	
			# sort annotations list on label+frame id 
			# (necessary for interpolation when adding annotations to image)
			self.annotations_list = sorted(self.annotations_list, key=lambda x: (x[0],x[3]))

			if new_label_flag is True:
				# add label to annot sel list so it can be plotted
				rb_disp_var = tk.BooleanVar(self.window,'1')			
				opmenu_color_var = tk.StringVar(self.window,'Red')
				self.annot_menu_label_sel.append([label,rb_disp_var,opmenu_color_var])
				# set label as annot edit select
				self.rb_label_sel_var.set(label)
				# if menu open, update option menu
				if self.annotgui_flag is 1:
					self.update_rb_tgt_sel()

	# add click positions to the annotations list
	def delete_annotation_callback(self,event):
		# if video loaded, delete annotation
		if self.cap is not None:
			# get target label
			label = self.rb_label_sel_var.get()
			# if annotation exists for this frame, delete it
			if len(self.annotations_list)>0:
				for i in self.annotations_list:
					if (i[0]==label) and (i[3]==(self.iframe+1)):
						self.annotations_list.remove(i)
						# if removed the only entry for the selected target, 
						# set annot edit select to NEW TARGET and refresh gui
						label_gone_flag = True
						for j in self.annotations_list:
							if (j[0]==label):
								label_gone_flag = False
						if label_gone_flag is True:
							# set label as annot edit select
							self.rb_label_sel_var.set('NEW TARGET')
							# if menu open, update option menu
							if self.annotgui_flag is 1:
								self.update_rb_tgt_sel()

	# build save vid menu GUI
	def savvgui(self,event=None):
		if self.ivfpath is not None:
			# toggle display flag
			self.savvgui_flag = -self.savvgui_flag
			# if savv menu is not open, open it
			if self.savvgui_flag is 1:
				self.btn_savv_toggle['text']='<'
				# create right sidebar
				rmenu2w = 15
				self.rmenu2 = tk.Frame(self.rbar, width=rmenu2w)
				self.rmenu2.pack(expand=False, side=tk.LEFT, anchor=tk.N)
				# add save menu label
				label_savvmenu = tk.Label(self.rmenu2,text='SAVE VID MENU',font='bold',width=rmenu2w)
				label_savvmenu.pack(anchor=tk.CENTER, expand=False)	
				# add enter name label
				label_savvname = tk.Label(self.rmenu2,text='Output File Label',width=rmenu2w)
				label_savvname.pack(anchor=tk.CENTER, expand=False)
				# add entry box for save name
				self.ent_savvname = tk.Entry(self.rmenu2,width=rmenu2w)
				self.ent_savvname.pack(anchor=tk.CENTER, expand=False)
				self.ent_savvname.insert(0,'annot')
				# add start/stop frame selection label
				label_ssframe = tk.Label(self.rmenu2,text='Start/Stop Frame',width=rmenu2w)
				label_ssframe.pack(anchor=tk.CENTER, expand=False)
				# add frame for start/stop frame entry boxes (line in the GUI)
				frame_ssframe = tk.Frame(self.rmenu2, width=rmenu2w)
				frame_ssframe.pack(anchor=tk.CENTER, expand=False)
				# add start frame entry box, default to first frame
				self.ent_start_val = tk.Entry(frame_ssframe,width=round(rmenu2w/2))
				self.ent_start_val.pack(side=tk.LEFT, expand=False)
				self.ent_start_val.insert(0,'1')
				# add stop frame entry box, default to last frame
				self.ent_stop_val = tk.Entry(frame_ssframe,width=round(rmenu2w/2))
				self.ent_stop_val.pack(side=tk.LEFT, expand=False)
				self.ent_stop_val.insert(0,self.nframe)
				# add save vid button
				btn_savev = tk.Button(self.rmenu2, text="Save Vid mp4", width=rmenu2w, command=self.savv)
				btn_savev.pack(anchor=tk.CENTER, expand=False)
			# if savv menu is open, close it
			elif self.savvgui_flag is -1:
				self.close_savvmenu()

	# Save annotated movie
	def savv(self):
		initfilename = Path(self.ivfpath).stem+'_'+self.ent_savvname.get()+'.mp4'
		ovfpath = filedialog.asksaveasfilename(initialdir=config.default_odir, \
			initialfile=initfilename,filetypes=[('mp4 file','*.mp4')],confirmoverwrite=True)
		if len(ovfpath)==0:
			return
		print('Saving '+ ovfpath)
		# create output VideoCapture object
		fourcc = cv2.VideoWriter_fourcc(*'mp4v')
		self.ovid = cv2.VideoWriter(ovfpath,fourcc, self.fps, self.vsize)
		# create input VideoCapture object
		self.cap2 = cv2.VideoCapture(self.ivfpath)
		# get number frames
		l_nframe = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
		# make copy of annoitations list so it doesn't get changed mid save
		l_disp_annot_flag = self.disp_annot_flag
		l_annotations_list = self.annotations_list
		l_label_list = self.label_list
		# validate start/stop frames
		try:
			istart = int(self.ent_start_val.get())
			istop = int(self.ent_stop_val.get())
		except ValueError: 
			print('start/stop frame invalid')
			return
		if istop<istart:
			print('start frame exceeds stop frame')
			return
		if istart<1:
			print('start/stop frame invalid')
			return
		if istop>l_nframe:
			print('stop frame exceeds EOF')
			return
		# set self.cap2 to start frame
		l_iframe = istart
		self.cap2.set(1,l_iframe)
		# loop through frames, drawing annotations and saving
		while self.cap2.isOpened() and l_iframe<=istop:
			# read next frame
			ret, l_frame = self.cap2.read()
			# if frame read successfully display it
			if ret==True:
				# add annotations to frame
				l_frame_annot = la.draw_annotations(l_disp_annot_flag, \
													l_frame, \
													l_iframe, \
													l_nframe, \
													l_annotations_list, \
													l_label_list, \
													self.annot_menu_label_sel, \
													config.annot_box_size)
				self.ovid.write(l_frame_annot)
			# increment frame id
			l_iframe = l_iframe+1
			# update saving status string
			if l_iframe%100==0:
				print('Saving Frame {} ...'.format(l_iframe))
		# release input video source when done saving
		self.cap2.release()
		# release output VideoWriter object
		self.ovid.release()
		# update displayed status
		print('Save Complete')

	# close save vid menu GUI
	def close_savvmenu(self):
		# Release the video source when the window object is destroyed
		if self.cap2 is not None:
			if self.cap2.isOpened():
				self.cap2.release()
		# Release the video source when the window object is destroyed
		if self.ovid is not None:
			if self.ovid.isOpened():
				self.ovid.release()
		# set display flag to off
		self.savvgui_flag = -1
		# destroy menu
		self.btn_savv_toggle['text']='>'
		self.rmenu2.destroy()

	# build annots menu GUI
	def annotmenugui(self,event=None):
		if self.ivfpath is not None:
			# toggle display flag
			self.annotgui_flag = -self.annotgui_flag
			# if savv menu is not open, open it and toggle flag
			if self.annotgui_flag is 1:
				self.btn_annot_toggle['text']='<'
				# create annots menu frame inside right sidebar
				rmenu3w = 15
				self.rmenu3 = tk.Frame(self.rbar, width=rmenu3w)
				self.rmenu3.pack(expand=False, side=tk.LEFT, anchor=tk.N)
				# add menu label
				label_cannotmenu = tk.Label(self.rmenu3,text='ANNOTS MENU',font='bold',width=rmenu3w)
				label_cannotmenu.pack(anchor=tk.CENTER, expand=False)
				# add load video button and key binding
				btn_loada = tk.Button(self.rmenu3, text="Load Annots (a)", width=self.rmenu1w, command=self.loada)
				btn_loada.pack(anchor=tk.CENTER, expand=False)
				self.window.bind('a',self.loada)
				# add save annotations button
				btn_sava = tk.Button(self.rmenu3, text="Save Annot csv", width=rmenu3w, command=self.sava)
				btn_sava.pack(anchor=tk.CENTER, expand=False)
				# add scrollable label list with selectable options
				# needs to be last or when called it reorders the menu elements
				self.update_rb_tgt_sel()
			elif self.annotgui_flag is -1:
				self.close_annotmenu()

	# update scrollable target label list
	def update_rb_tgt_sel(self):
		# convert annotations_list to a pandas dataframe
		annotations_df =  pd.DataFrame(self.annotations_list,columns=['label','x','y','iFrame'])
		# get list of unique labels
		label_list = list(set(annotations_df['label']))
		label_list.sort()
		# add NEW TARGET option to list
		label_list.insert(0,'NEW TARGET')
		# store previous label selections, and destroy scrollable window if it already exists
		if self.sframe_label_sel is not None:
			# store annot_menu_label_sel
			prev_annot_menu_label_sel = self.annot_menu_label_sel
			# destroy scrollable region
			self.sframe_label_sel.destroy()
		else:
			prev_annot_menu_label_sel = list()
		# create scrolling region
		self.sframe_label_sel = self.ScrollableFrame(self.rmenu3)
		# init label sel list to empty list
		self.annot_menu_label_sel = list()
		# add labels to scrollable list
		for label in label_list:
			# set none-specified default selections
			displayflag = True
			colortxt = 'Red'
			# look in config file for specified default selections
			if len(config.default_label_sel)>0:
				default_label_sel_df =  pd.DataFrame(config.default_label_sel,columns=['label','rb_disp','color'])
				imatch = default_label_sel_df.index[default_label_sel_df['label']==label].tolist()
				if len(imatch)>0:
					# get display flag and color of label
					displayflag = config.default_label_sel[imatch[0]][1]
					colortxt = config.default_label_sel[imatch[0]][2]
			# look for previous label selections for current target
			if len(prev_annot_menu_label_sel)>0:
				# find current label in label_sel
				label_sel_df =  pd.DataFrame(prev_annot_menu_label_sel,columns=['label','rb_disp','color'])
				imatch = label_sel_df.index[label_sel_df['label']==label].tolist()
				if len(imatch)>0:
					# get display flag and color of label
					displayflag = (prev_annot_menu_label_sel[imatch[0]][1]).get()
					colortxt = (prev_annot_menu_label_sel[imatch[0]][2]).get()
			# create frame for current label line
			frame = tk.Frame(self.sframe_label_sel.scrollable_frame)
			# note self.rb_label_sel_var holds the current selected label,
			# it is initialized in __init__
			# create label selection radio button for current label
			rb_label_sel = tk.Radiobutton(frame,text=label,indicatoron=0,width=18,height=2,padx=2,variable=self.rb_label_sel_var,value=label)
			rb_label_sel.pack(side=tk.LEFT, expand=False)
			# if new target, add white space label to line names up
			if label is 'NEW TARGET':
				tk.Label(frame,text='', width=13).pack(side=tk.LEFT, expand=False)
			# otherwise, add disp radio button, and color select dropdown
			else:
				# create disp annot radio variable, default to on
				rb_disp_var = tk.BooleanVar(self.window,displayflag)
				# add disp annot radio button, attached to the variable
				rb_disp = tk.Checkbutton(frame,variable=rb_disp_var,indicatoron=True)
				rb_disp.pack(side=tk.LEFT, expand=False)
				# define color options list
				color_options = ['Red','Orange','Yellow','Green','Cyan','Blue','Purple','Magenta','Black','White']
				# create annot color variable, set to colortxt
				opmenu_color_var = tk.StringVar(self.window)
				opmenu_color_var.set(colortxt)
				# add color select drop down menu, attached to the variable
				opmenu_color = tk.OptionMenu(frame, opmenu_color_var, *color_options)
				opmenu_color.config(width=5)
				opmenu_color.pack(side=tk.LEFT, expand=False)
				# store label annot selections in list
				self.annot_menu_label_sel.append([label,rb_disp_var,opmenu_color_var])
			frame.pack()
		# pack the scrollable frame
		self.sframe_label_sel.pack()

	# close annots menu GUI
	def close_annotmenu(self):
		self.btn_annot_toggle['text']='>'
		self.annotgui_flag = -1
		self.rmenu3.destroy()

	# define scrollable frame class
	class ScrollableFrame(tk.Frame):
		def __init__(self, container, *args, **kwargs):
			super().__init__(container, *args, **kwargs)
			# add canvas to container
			canvas = tk.Canvas(self,width=270,height=170) 
 			# add scrollbar to container and attach to canvas
			#scrollbarh = tk.Scrollbar(self,orient=tk.HORIZONTAL,command=canvas.xview)
			scrollbarv = tk.Scrollbar(self,orient=tk.VERTICAL,command=canvas.yview)
			# add scrollable container to canvas
			self.scrollable_frame = tk.Frame(canvas)
			# update region size when scrollable frame contents changes
			self.scrollable_frame.bind(
				'<Configure>',
				lambda e: canvas.configure(
					scrollregion=canvas.bbox('all')
				)
			)
			# create scrollable region inside canvas
			canvas.create_window((0,0),window=self.scrollable_frame,anchor=tk.NW)
			# move scrollbar with scrollable region
			#canvas.configure(xscrollcommand=scrollbarh.set)
			canvas.configure(yscrollcommand=scrollbarv.set)
			# position canvas and scrollbar
			canvas.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
			#scrollbarh.pack(side=tk.BOTTOM,fill='x')
			scrollbarv.pack(side=tk.RIGHT,fill='y')
