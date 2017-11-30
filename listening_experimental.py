#!/usr/bin/python3
# (supposed to) Listen for config change from server via RabbitMQ
#
# https://github.com/pika/pika/blob/master/examples/twisted_service.py
# if it's just gonna roll over and die on channel closure why bother with twisted
# just let supervisor restart it
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017
import pika,socket,traceback,sys,time,logging,json
from os.path import expanduser
sys.path.append(expanduser('~'))
from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer,reactor,protocol,task
#from twisted.web import xmlrpc,server
from twisted.internet.defer import setDebugging
from twisted.python import log
from config.config_support import Config
from cred import cred


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pika').setLevel(logging.WARNING)

setDebugging(True)


nodeid = socket.gethostname()
exchange_name = 'grid_cnc'
queue_name = 'to_' + nodeid
routing_key = nodeid + '.c'
user,passwd = nodeid,cred['rabbitmq']
config_file = expanduser('~/config.db')
config = Config(config_file)





class PikaFactory(protocol.ReconnectingClientFactory):
    name = 'AMQP:Factory'

    def __init__(self, parameters):
        self.parameters = parameters
        self.client = None
        self.queued_messages = []
        self.read_list = []

    def startedConnecting(self, connector):
        log.msg('Started to connect.', system=self.name)

    def buildProtocol(self, addr):
        self.resetDelay()
        log.msg('Connected', system=self.name)
        self.client = PikaProtocol(self.parameters)
        self.client.factory = self
        self.client.ready.addCallback(self.client.connected)
        return self.client

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection.  Reason: %s' % reason, system=self.name)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, system=self.name)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def send_message(self, exchange = None, routing_key = None, message = None):
        self.queued_messages.append((exchange, routing_key, message))
        if self.client is not None:
            self.client.send()

    def read_messages(self, exchange, routing_key, callback):
        """Configure an exchange to be read from."""
        self.read_list.append((exchange, routing_key, callback))
        if self.client is not None:
            self.client.read(exchange, routing_key, callback)







def duh(e):
    logging.exception(e)
    reactor.stop()
    #sys.exit()

@defer.inlineCallbacks
def run(connection):
    try:
        channel = yield connection.channel()
        exchange = yield channel.exchange_declare(exchange=exchange_name,exchange_type='fanout',durable=True)
        queue = yield channel.queue_declare(queue=queue_name,durable=True,exclusive=False,arguments={'x-message-ttl': 24*3600*1000})
        yield channel.queue_bind(exchange=exchange_name,queue=queue_name,routing_key=routing_key)
        yield channel.basic_qos(prefetch_count=5)
        queue_object,consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=False)
        l = task.LoopingCall(read,queue_object)
        d = l.start(0.01)
        d.addErrback(duh)
    except:
        logging.exception('Cannot connect to local C&C exchange')
        sys.exit()

@defer.inlineCallbacks
def read(queue_object):
    try:
        ch,method,properties,body = yield queue_object.get()
        if body:
            logging.debug(body)
            #d = json.loads(body.strip())
            d = json.loads(body.decode("utf-8","strict"))
            #{'a':'set','node':'griddemoX','d':...}
            if d.get('node',None) != nodeid:
                logging.debug('no recipient, or message not for me. ignore')
            elif 'a' not in d or 'd' not in d:
                logging.warning('missing action and/or data. ignore')
            elif d.get('a',None) != 'set':
                logging.debug('not \'set\'. ignore')
            else:
                d = d['d']
                # have to give up 'server_time' for now...
                #assert 'server_time' in d and type(d['server_time']) in [float,int]

                for k in d:
                    logging.info('Attempt to set {} to {}'.format(k,d[k]))
                    if config.set(k,d[k]):
                        logging.info('{} changed to {}'.format(k,d[k]))
                    else:
                        logging.info('No change for {}'.format(k))
                
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
    except pika.exceptions.ChannelClosed:
        # but how to create a new channel here?
        traceback.print_exc()
        raise
    except:
        traceback.print_exc()
        raise
    

credentials = pika.PlainCredentials(user,passwd)
parameters = pika.ConnectionParameters(credentials=credentials)
cc = protocol.ClientCreator(reactor,twisted_connection.TwistedProtocolConnection,parameters)

d = cc.connectTCP('localhost',5672)
d.addCallback(lambda protocol: protocol.ready)
d.addCallback(run)
d.addErrback(duh)

logging.info(__file__ + ' is ready')
reactor.run()

logging.info(__file__ + ' terminated')
