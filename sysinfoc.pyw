#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from inc.autoscrollbar import *
from inc.constants import *
from inc.sysinfoc.receivingengine import *
from inc.sysinfoc.databaseengine import *
from inc.sysinfoc.guiengine import *
from inc.sysinfoc.window import *
from inc.sysinfoc.tab import *

import sys
sys.path.append('.\inc')
#from autoscrollbar import *
#from constants import *
#from wmi2 import *

sys.path.append('.\inc\sysinfoc')
#from receivingengine import *
#from databaseengine import *
#from guiengine import *
#from window import *
#from tab import *

def startTheEngines(window, databaseEngine, receivingEngine, guiEngine):	
	databaseEngine.begin()	
	receivingEngine.begin()
	guiEngine.begin()

# def tracefunc(frame, event, arg, indent=[0]):
#       if event == "call":
#           indent[0] += 2
#           print "-" * indent[0] + "> call " +  frame.f_code.co_name + " (" + str(frame.f_lineno) + ")"
#       elif event == "return":
#           print "<" + "-" * indent[0], "exit " + frame.f_code.co_name + " (" + str(frame.f_lineno) + ")"
#           indent[0] -= 2
#       return tracefunc

#sys.settrace(tracefunc)

def main():

	tkinter = Tk()
	window = Window(tkinter)

	databaseEngine = DatabaseEngine()
	receivingEngine = ReceivingEngine(databaseEngine)
	guiEngine = GuiEngine(window, databaseEngine, tkinter)

	tkinter.title(NAMEC + "")
	tkinter.after(100, startTheEngines, window, databaseEngine, receivingEngine, guiEngine)
	tkinter.mainloop()

if __name__ == '__main__':
	main() 
