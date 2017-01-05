import pika
import unittest
import sys

sys.path.append('..')
sys.path.append('..\inc\sysinfo')
from reportingengine import *

class ReportingEngineTestable(ReportingEngine):

    def __init__(self, argv, infoEngine, statsEngine):
        super(ReportingEngineTestable, self).__init__(argv, infoEngine, statsEngine)

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip))
        self.channel = self.connection.channel()

    def declareQueue(self, queueName):
        self.channel.queue_declare(queue=queueName)

    def deleteQueue(self, queueName):
        self.channel.queue_delete(queue=queueName)

    def sendThroughQueue(self, queueName, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=queueName,
                                   body=message)

    def disconnect(self):
        self.connection.close()

class ConnectionMaintainer(object):

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()     

    def disconnect(self):
         self.connection.close()

    def deleteQueue(self, queueName):
        self.channel.queue_delete(queue=queueName)

    def declareQueue(self, queueName, passiv=False):
        self.channel.queue_declare(queue=queueName, passive=passiv)

    def basicConsume(self, queueName, callback):
        self.channel.basic_consume(callback, queue=queueName, no_ack=True)


class ReportingEngineQueueTests(unittest.TestCase):

    def consumeOnce(self, ch, method, properties, body):
        self.lastMessage = body
        ch.stop_consuming()

    @classmethod
    def setUpClass(self):
        self.connectionMaintainer = ConnectionMaintainer()

        self.lastMessage = None
        self.reportingEngine = ReportingEngineTestable(["", "localhost"], None, None)

        self.w = wmi.WMI()
        self.reportingEngine.w = self.w
        self.reportingEngine.getMACAddress2()

        self.macQueue = self.reportingEngine.mac

        self.connectionMaintainer.connect()
        self.connectionMaintainer.deleteQueue(self.macQueue)
        self.connectionMaintainer.disconnect()

    def connect(self):
        self.connectionMaintainer.connect()

    def disconnect(self):
        self.connection

    def checkIfQueueExists(self, queueName):
        try:
            self.connectionMaintainer.declareQueue(self.macQueue, True)
            return True
        except:
            return False

    def testIfQueueNotCreatedYet(self):
        self.connectionMaintainer.connect()
        truthValue = self.checkIfQueueExists(self.macQueue)
        self.connectionMaintainer.disconnect()
        self.assertEqual(truthValue, False)

    def testIfQueueWasCreated(self):
        self.reportingEngine.connect()
        self.reportingEngine.declareQueue(self.macQueue)
        self.reportingEngine.disconnect()

        self.connectionMaintainer.connect()
        truthValue = self.checkIfQueueExists(self.macQueue)
        self.connectionMaintainer.disconnect()

        self.assertEqual(truthValue, True)

    def testIfQueueGetsDeleted(self):
        self.connectionMaintainer.connect()
        self.connectionMaintainer.declareQueue(self.macQueue)
        self.connectionMaintainer.disconnect()

        self.reportingEngine.connect()
        self.reportingEngine.deleteQueue(self.macQueue)
        self.reportingEngine.disconnect()

        self.connectionMaintainer.connect()
        truthValue = self.checkIfQueueExists(self.macQueue)
        self.connectionMaintainer.disconnect()

        self.assertEqual(truthValue, False)

    def testIfMessageIsBeingSent(self):
        self.reportingEngine.connect()
        self.reportingEngine.declareQueue(self.macQueue)
        self.reportingEngine.sendThroughQueue(self.macQueue, "test")
        self.reportingEngine.disconnect()

        self.connectionMaintainer.connect()
        self.connectionMaintainer.basicConsume(self.macQueue, self.consumeOnce)
        self.connectionMaintainer.disconnect()

        self.assertEqual(self.lastMessage, "test")

    def testForWrongMessage(self):
        self.reportingEngine.connect()
        self.reportingEngine.declareQueue(self.macQueue)
        self.reportingEngine.sendThroughQueue(self.macQueue, "tablespoon")
        self.reportingEngine.disconnect()

        self.connectionMaintainer.connect()
        self.connectionMaintainer.basicConsume(self.macQueue, self.consumeOnce)
        self.connectionMaintainer.disconnect()

        self.assertTrue(self.lastMessage != "test")

    @classmethod
    def tearDownClass(self):
        self.connectionMaintainer.connect()
        self.connectionMaintainer.deleteQueue(self.macQueue)
        self.connectionMaintainer.disconnect()