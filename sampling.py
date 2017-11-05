#!/usr/bin/python3
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017

import os, sys, time, logging, pika, socket, json

from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred
from config.config_support import import_node_config#, Config
from grid.drivers.pic import LocalPIC
from parse_support import pretty_print

# Settings
vhost = 'grid'
exchange = 'grid'
reconnect_delay_second = 10  # Wait at least this many seconds before retrying connection
nodeid = socket.gethostname()

# Verify that the socket is ready for the PIC's tags.
conf = import_node_config(nodeid).conf
tags = [c['dbtag'] for c in conf]
#print(set(tags) - set(pic._get_tags()))

routing_key = nodeid + '.r'
user = nodeid
passwd = cred['rabbitmq']
#config_file = expanduser('~/config.db')
#config = Config(config_file)

def mq_init():
    credentials = pika.PlainCredentials(user, passwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, vhost, credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
    return channel

# Don't call mq_init() here or else the script will never run when network is down.

localpic = LocalPIC()
assert set(localpic._get_tags()).issubset(set(tags))
channel = None
properties = pika.BasicProperties(delivery_mode=2,
                                  user_id=user,
                                  content_type='text/plain',
                                  expiration=str(7*24*3600*1000))

logging.basicConfig(level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
logging.info(__name__ + ' is ready')

while True:
    d = localpic.read()       
    d['ts_gw'] = time.time()

    print('\x1b[2J\x1b[;H')
    pretty_print(d)
    
    d = {'v':1, 'from':nodeid, 'd':d}
    
    if channel is None:
        logging.info('Connection to local exchange is not open')
        channel = mq_init()
        logging.info('Connection to local exchange re-established')

    try:
        channel.basic_publish(exchange,
                              routing_key,
                              body=json.dumps(d, separators=(',', ':')),
                              properties=properties)
    except pika.exceptions.ConnectionClosed:
        channel = None
        time.sleep(reconnect_delay_second)
