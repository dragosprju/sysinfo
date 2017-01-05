import re
import unittest

import sys
sys.path.append('..\\inc\\sysinfo')
from reportingengine import *

class ReportingEngineTests(unittest.TestCase):

    @staticmethod
    def isValidMACAddress(value):
        allowed = re.compile(r"""
                     (
                         ^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$
                        |^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$
                     )
                     """,
                    re.VERBOSE|re.IGNORECASE)
        if allowed.match(value) is None:
            return False
        else:
            return True

    @staticmethod
    def checkIfQueueExists(address, name):
        connection = pika.BlockingConnection(pika.ConnectionParameters(address))
        channel = connection.channel()
        channel.queue_declare(queue=name, passive=True)

    def testValidIP(self):
        truthValue = ReportingEngine.validIP("192.168.1.1")
        self.assertEqual(truthValue, True)

    def testValidIPwithPort(self):
        truthValue = ReportingEngine.validIP("192.168.1.1:1234")
        self.assertEqual(truthValue, False)

    def testValidIPwithGibberish(self):
        truthValue = ReportingEngine.validIP("hellojusttesting")
        self.assertEqual(truthValue, False)

    def testValidIPwithLocalhost(self):
        truthValue = ReportingEngine.validIP("localhost")
        self.assertEqual(truthValue, True)

    def testIfMACAddressIsValid(self):
        reportingEngine = ReportingEngine("", None, None)
        reportingEngine.initialize()
        reportingEngine.getMACAddress2()
        self.assertEqual(self.isValidMACAddress(reportingEngine.mac), True)

    