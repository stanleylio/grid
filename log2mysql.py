#!/usr/bin/python3
# This taps into the local RabbitMQ exchange and store .samples msgs into MySQL
#
# Now commiting once every two seconds (instead of on every message).
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved, 2017
import pika,socket,traceback,sys,time,math,MySQLdb,logging,json
from os.path import expanduser,basename
sys.path.append(expanduser('~'))
from twisted.internet import defer,reactor,protocol,task
from twisted.internet.task import LoopingCall
from pika.adapters import twisted_connection
from parse_support import pretty_print
from storage import storage
from cred import cred


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pika').setLevel(logging.WARNING)


exchange_name = 'grid'
queue_name = basename(__file__)
nodeid = socket.gethostname()
routing_key = '*.r'


def init_storage():
    return storage()
store = init_storage()


@defer.inlineCallbacks
def run(connection):
    try:
        channel = yield connection.channel()
        exchange = yield channel.exchange_declare(exchange=exchange_name,exchange_type='topic',durable=True)
        queue = yield channel.queue_declare(queue=queue_name,
                                            durable=True,
                                            exclusive=False,
                                            arguments={'x-message-ttl':2**31-1})    # ~24 days.
        yield channel.queue_bind(exchange=exchange_name,queue=queue_name,routing_key=routing_key)
        yield channel.basic_qos(prefetch_count=5)
        queue_object,consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=False)
        l = task.LoopingCall(read,queue_object)
        l.start(0.00001)                        # !!!!!
    except:
        logging.exception('Cannot connect to local C&C exchange')
        sys.exit()

@defer.inlineCallbacks
def read(queue_object):
    ch,method,properties,body = yield queue_object.get()
    if body:
        global store
        try:
            logging.debug(body)
            d = json.loads(body)
            #version = d['v']
            #from = d['from']
            d = d['d']
            d['rt'] = time.time()
            print('= = = = = = = = = = = = = = =')
            pretty_print(d)

            for k in d.keys():
                try:
                    if math.isnan(d[k]):
                        d[k] = None
                except TypeError:
                    pass
            #store.insert(properties.user_id,d)
            store.insert(properties.user_id,d,autocommit=False)
            
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
        except MySQLdb.OperationalError:
            traceback.print_exc()
            store = init_storage()
        except:
            logging.exception(body)

def taskCommit():
    global store
    store.commit()


credentials = pika.PlainCredentials(nodeid,cred['rabbitmq'])
parameters = pika.ConnectionParameters('localhost',5672,'/',credentials)
cc = protocol.ClientCreator(reactor,twisted_connection.TwistedProtocolConnection,parameters)
d = cc.connectTCP('localhost',5672)
d.addCallback(lambda protocol: protocol.ready)
d.addCallback(run)
LoopingCall(taskCommit).start(2)
logging.info(__file__ + ' is ready')
reactor.run()
logging.info(__file__ + ' terminated')
