import pika
import sys
import unittest

sys.path.append('..')
sys.path.append('..\inc\sysinfoc')
from receivingengine import *

class ReceivingEngineTests(unittest.TestCase):

    @classmethod 
    def setUpClass(self):
        self.receivingEngine = ReceivingEngine(None)

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()

    def disconnect(self):
        self.connection.close()

    # def testIfMessagesGetReceived(self):
    #     self.connect()
    #     self.channel.basic_publish(exchange='',
    #                                routing_key="sysinfo",
    #                                body="test")
    #     self.channel.basic_publish(exchange='',
    #                                routing_key="sysinfo",
    #                                body="woo")
    #     self.disconnect()

    #     self.receivingEngine.begin()
    #     self.receivingEngine.stop()

    #     self.assertEqual(self.receivingEngine.macs, ["test", "woo"])

    def testStringSplit(self):
        splitted = str.split("ONE : TWO", " : ")
        one = splitted[0]
        two = splitted[1]
        self.assertEqual([one, two], splitted)

    def testIfQueueIsEmptyAfterFirstTest(self):
        self.connect()
        strStats = self.channel.queue_declare(queue="sysinfo", passive=True)
        intStats = re.findall("\d+", str(strStats))
        self.assertEqual(int(intStats[3]), 0)

    @classmethod
    def tearOffClass(self):
        self.channel.queue_delete(queue="sysinfo")
        self.channel.queue_delete(queue=self.reportingEngine.mac)