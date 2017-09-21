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


logging.basicConfig(level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)


nodeid = socket.gethostname()
exchange_name = 'grid_cnc'
queue_name = 'to_' + nodeid
routing_key = nodeid + '.c'
user,passwd = nodeid,cred['rabbitmq']
config_file = expanduser('~/config.db')


config = Config(config_file)


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
        l.start(0.01)
    except:
        logging.exception('Cannot connect to local C&C exchange')
        sys.exit()

@defer.inlineCallbacks
def read(queue_object):
    ch,method,properties,body = yield queue_object.get()
    if body:
        try:
            logging.debug(body)
            #d = json.loads(body.strip())
            d = json.loads(body.decode("utf-8","strict"))
            #{'a':'set','node':'griddemoX','d':...}
            if d.get('node',None) != nodeid:
                logging.debug('no recipient, or message not for me. ignore')
            elif 'a' not in d or 'd' not in d:
                logging.warning('missing action and/or data')
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
                
            #ch.basic_ack(delivery_tag=method.delivery_tag)
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            traceback.print_exc()


class P(xmlrpc.XMLRPC):
    def xmlrpc_get_config(self,variable_name):
        try:
            v = config.get(variable_name)
            logging.debug('{} == {}'.format(variable_name,v))
            return v
        except:
            logging.warning('Using default for {}'.format(variable_name))
            return 1    # safe defaults? where to store them? boundaries? TODO TODO TODO
    

credentials = pika.PlainCredentials(user,passwd)
parameters = pika.ConnectionParameters(credentials=credentials)
cc = protocol.ClientCreator(reactor,twisted_connection.TwistedProtocolConnection,parameters)
d = cc.connectTCP('localhost',5672)
d.addCallback(lambda protocol: protocol.ready)
d.addCallback(run)
reactor.listenTCP(8000,server.Site(P()))
logging.info(__file__ + ' is ready')
reactor.run()

#channel.basic_consume(callback,queue=queue_name)    # ,no_ack=True
#try:
#    channel.start_consuming()
#except KeyboardInterrupt:
#    logging.info('user interrupted')
logging.info(__file__ + ' terminated')
