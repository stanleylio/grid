#!/usr/bin/python3
# Listen for config change from server via RabbitMQ
# Respond to config param query via XMPRPC
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
from twisted.web import xmlrpc,server
from config.config_support import Config
from cred import cred


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pika').setLevel(logging.DEBUG)


exchange_name = 'grid'
queue_name = 'rabbitmq2stdout'
nodeid = socket.gethostname()
user,passwd = nodeid,cred['rabbitmq']


@defer.inlineCallbacks
def run(connection):
    channel = yield connection.channel()
    exchange = yield channel.exchange_declare(exchange=exchange_name,exchange_type='topic',durable=True)
    queue = yield channel.queue_declare(queue=queue_name,durable=False,exclusive=True,arguments={'x-message-ttl': 24*3600*1000})
    yield channel.queue_bind(exchange=exchange_name,queue=queue_name)
    yield channel.basic_qos(prefetch_count=5)
    queue_object,consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=True)
    l = task.LoopingCall(read,queue_object)
    l.start(0.01)

@defer.inlineCallbacks
def read(queue_object):
    ch,method,properties,body = yield queue_object.get()
    if body:
        try:
            print(body)
            #ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            traceback.print_exc()


logging.info(__file__ + ' is ready')
credentials = pika.PlainCredentials(user,passwd)
parameters = pika.ConnectionParameters(credentials=credentials)
cc = protocol.ClientCreator(reactor,twisted_connection.TwistedProtocolConnection,parameters)
d = cc.connectTCP('localhost',5672)
d.addCallback(lambda protocol: protocol.ready)
d.addCallback(run)
reactor.run()

#channel.basic_consume(callback,queue=queue_name)    # ,no_ack=True
#try:
#    channel.start_consuming()
#except KeyboardInterrupt:
#    logging.info('user interrupted')
logging.info(__file__ + ' terminated')
