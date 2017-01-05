from Tkinter import *

import sys
sys.path.append('..')
from autoscrollbar import *

class Tab(Frame):

	def __init__(self, parent, noColumns, resize):
		Frame.__init__(self, parent)
		self.parent = parent		
		self.rows = []
		self.noColumns = noColumns
		self.resize = resize
		if resize:
			self.xval = 6
		else:
			self.xval = 2
		self.setScrollBars()
		self.setTheScrollbar = False

	def setScrollBars(self):
		vscrollbar = AutoScrollbar(self)
		vscrollbar.grid(row=0, column=1, sticky=N+S)

		self.canvas = Canvas(self,
						yscrollcommand=vscrollbar.set)
		self.canvas.grid(row=0, column=0, sticky=N+S+E+W)

		vscrollbar.config(command=self.canvas.yview)

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.canvas.grid_columnconfigure(0, weight=1)
		self.canvas.grid_rowconfigure(0, weight=1)

		self.frame = Frame(self.canvas)
		for i in range(self.noColumns):
			self.frame.columnconfigure(i, weight=1)

	def resizeFrame(self, e):
		self.canvas.itemconfig(self.frameid, width=e.width)
		self.canvas.config(scrollregion=self.canvas.bbox("all"))

	def processLabels(self, name):
		for row in self.rows:
			for word in row:
				for i in range(99):
					try:
						word.grid(column=row.index(word), row=self.rows.index(row), sticky=W, padx=self.xval, pady=1)
						break
					except:
						print "Failed word.grid() " + name
						return
		self.setScrollbars2()

	def setScrollbars2(self):
		self.frameid = self.canvas.create_window(0, 0, anchor=NW, window=self.frame)		
		if self.resize:
			self.canvas.itemconfig(self.frameid, width=self.canvas.winfo_width())	
		if self.resize and self.setTheScrollbar == False:	
			self.bind("<Configure>", self.resizeFrame)			
			self.setTheScrollbar = True
		self.canvas.config(scrollregion=self.canvas.bbox("all"))

	def addRow(self, *args):
		row = []
		for t in args:
			row.append(Label(self.frame, text=t))
		self.rows.append(row)
		return row