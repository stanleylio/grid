#!/usr/bin/python3
import sys
import pika
import json
import time
import logging

from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred
from config.config_support import import_node_config
from . import gw_id, signals

routing_key = gw_id + '.r'

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# Verify that the socket is ready for the signals.
conf = import_node_config(gw_id).conf
tags = [c['dbtag'] for c in conf]
#print(set(tags) - set(signals))
assert set(signals).issubset(set(tags)), \
    "The socket is not ready for the power monitor signals."

class MQ(object):

    def __init__(self, user=gw_id, passwd=cred['rabbitmq'], vhost='grid', 
                 exchange='grid', reconnect_delay=10): # reconnect_delay is in seconds.
        credentials = pika.PlainCredentials(user, passwd)
        self._connection_params = pika.ConnectionParameters('localhost', 5672, 
                                                            vhost, credentials)
        self._pika_props = pika.BasicProperties(delivery_mode=2,
                                                user_id=user,
                                                content_type='text/plain',
                                                expiration=str(7*24*3600*1000))
        self.exchange = exchange
        self.reconnect_delay = reconnect_delay
        self.create_channel()

    def create_channel(self):
        self.channel = pika.BlockingConnection(self._connection_params).channel()
        self.channel.exchange_declare(exchange=self.exchange, 
                                      exchange_type='topic', durable=True)

    def publish(self, nodeid, measurements):

        if self.channel is None:
            logger.info('Connection to local exchange is not open')
            self.create_channel()
            logger.info('Connection to local exchange re-established')

        d = {'v':1, 'from':nodeid, 'd':measurements}

        try:
            self.channel.basic_publish(self.exchange,
                                       routing_key,
                                       body=json.dumps(d, separators=(',', ':')),
                                       properties=self._pika_props)
        except pika.exceptions.ConnectionClosed:
            self.channel = None
            time.sleep(self.reconnect_delay)

