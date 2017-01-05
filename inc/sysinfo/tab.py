from autoscrollbar import *
from Tkinter import *
from ttk import Separator

class Tab(Frame):

	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent		
		self.headers = []
		self.bodies = []
		self.initUI()

	def setScrollBars(self):
		vscrollbar = AutoScrollbar(self)
		vscrollbar.grid(row=0, column=1, sticky=N+S)

		self.canvas = Canvas(self,
		                yscrollcommand=vscrollbar.set)
		self.canvas.grid(row=0, column=0, sticky=N+S+E+W)

		vscrollbar.config(command=self.canvas.yview)

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.frame = Frame(self.canvas)
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=2)

	def setScrollBars2(self):
		self.canvas.create_window(0, 0, anchor=NW, window=self.frame)
		self.frame.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))

	def initUI(self):
		self.grid()
		self.setScrollBars()

	def processLabels(self):
		for i in range(len(self.headers)):
			if not self.headers[i] == "---separator---":
				self.headers[i].grid(column=0, row=i, sticky=W, padx=6, pady=1)
				self.bodies[i].grid(column=1, row=i, sticky=W, padx=6, pady=1)
			else:
				s = Separator(self.frame, orient=HORIZONTAL)
				s.grid(column=0, row=i, sticky=W+E, padx=6, pady=2, columnspan=2)
		self.setScrollBars2()

	def addRow(self, header, body):
		header = header + ": "
		self.headers.append(Label(self.frame, text=header))
		
		bodyVar = StringVar()
		bodyVar.set(body)
		self.bodies.append(Label(self.frame, textvariable=bodyVar))
		return bodyVar

	def addSeparator(self):
		self.headers.append("---separator---")
		self.bodies.append("")