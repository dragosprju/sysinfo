#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
import sys
sys.path.append('.\inc')
from wmi2 import *
from constants import *

sys.path.append('.\inc\sysinfo')
from infoengine import *
from statsengine import *
from reportingengine import *
from window import * 
from engine import *


def startTheEngines(tkinter, infoTab, statsTab, infoEngine, statsEngine, reportingEngine):
	# Prepare predefined labels
	infoEngine.loadPredefined()
	statsEngine.loadPredefined()

	# Populate window with predefined labels
	infoTab.processLabels()
	statsTab.processLabels()

	# Start the actual populating and refreshing (if applicable)
	infoEngine.populate()
	statsEngine.populate()
	reportingEngine.begin()

	if (reportingEngine.status() == False):
		tkinter.title(NAME + " - Not reporting")
	else:
		tkinter.title(NAME + " - Reporting to '" + reportingEngine.ip + "'")

def main(argv):
  
	tkinter = Tk()
	window = Window(tkinter)

	# System Information Tab & Engine Declaration
	infoTab = window.getTab(1)
	infoEngine = InfoEngine(window, infoTab)
   
	# System Statistics Tab & Engine Declaration   
	statsTab = window.getTab(2)
	statsEngine = StatsEngine(window, statsTab)

	# Subsystem that will send information about computer to another Python script
	reportingEngine = ReportingEngine(argv, infoEngine, statsEngine)

	# tkinter.mainloop() is a blocking method, but tkinter.after() sets a method (2nd argument) to run after specified miliseconds, along with .mainloop()
	tkinter.title(NAME + " - Pooling WMI...")
	tkinter.after(100, startTheEngines, tkinter, infoTab, statsTab, infoEngine, statsEngine, reportingEngine)
	tkinter.mainloop()

if __name__ == '__main__':
	main(sys.argv) 