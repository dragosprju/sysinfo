import unittest

import sys
sys.path.append('.\\tests')
sys.path.append('.\\inc')
sys.path.append('.\\inc\\sysinfo')
sys.path.append('.\\inc\\sysinfoc')
from ReportingEngineTests import *
from ReportingEngineQueueTests import *
from ReceivingEngineTests import *

def main():
    unittest.main()

if __name__ == '__main__':
    main()