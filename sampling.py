#!/usr/bin/python3
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017
import os,sys,traceback,time,logging,pika,socket,json
from os.path import expanduser
sys.path.append(expanduser('~'))
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from cred import cred
from config.config_support import import_node_config,Config
from grid.drivers.pic import PIC
from parse_support import pretty_print


logging.basicConfig(level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)


conf = import_node_config().conf
tags = [c['dbtag'] for c in conf]


pic = PIC()
#print(set(tags) - set(pic._get_tags()))
assert set(pic._get_tags()).issubset(set(tags))



exchange = 'grid'
vhost = 'grid'
nodeid = socket.gethostname()
routing_key = nodeid + '.r'         # ignored for fanout exchange
user,passwd = nodeid,cred['rabbitmq']
reconnect_delay_second = 10         # wait this many seconds before retrying connection
sample_interval_second = 1          # TODO: fail-safe default, min, max
config_file = expanduser('~/config.db')
config = Config(config_file)


def mq_init():
    credentials = pika.PlainCredentials(user,passwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,vhost,credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,exchange_type='topic',durable=True)
    return connection,channel

# don't call mq_init() here or else the script never gets a chance to run when network is down
connection,channel = None,None


def taskSample():
    global connection,channel

    d = pic.read()
    if d:        
        d['ts_gw'] = time.time()

        print('\x1b[2J\x1b[;H')
        pretty_print(d)
        
        d = {'v':1,'from':nodeid,'d':d}
        line = json.dumps(d,separators=(',',':'))
        #continue
        
        try:
            if connection is None or channel is None:
                logging.info('Connection to local exchange is not open')
                connection,channel = mq_init()
                logging.info('Connection to local exchange re-established')

            if connection is not None and channel is not None:
                channel.basic_publish(exchange,
                                      routing_key,
                                      line,
                                      properties=pika.BasicProperties(delivery_mode=2,
                                                                      user_id=user,
                                                                      content_type='text/plain',
                                                                      expiration=str(7*24*3600*1000)))
            else:
                logging.error('wut?')
        except pika.exceptions.ConnectionClosed:
            connection,channel = None,None
            time.sleep(reconnect_delay_second)
    else: 
        logging.info('no pic data; skipping this sample')

    reactor.callLater(sample_interval_second,taskSample)


logging.info(__name__ + ' is ready')

reactor.callLater(sample_interval_second,taskSample)

reactor.run()
if connection is not None:
    connection.close()
logging.info(__name__ + ' terminated')
