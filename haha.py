# time.time() firehose
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017
import os,sys,traceback,time,logging,pika,socket
from cred import cred


exchange = 'grid'
node_id = socket.gethostname()
routing_key = node_id + '.r'
#routing_key = 'griddemo1.r'


def mq_init():
    credentials = pika.PlainCredentials(node_id,cred['rabbitmq'])
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,exchange_type='topic',durable=True)
    return connection,channel


connection,channel = mq_init()


while True:
    line = str(time.time())
    print(line)
    
    try:
        if connection is None or channel is None:
            logging.info('Connection to local exchange closed')
            connection,channel = mq_init()
            logging.info('Connection to local exchange re-established')

        if connection is not None and channel is not None:
            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=line,
                                  properties=pika.BasicProperties(delivery_mode=2,
                                                                  content_type='text/plain',
                                                                  expiration=str(60*24*3600*1000),
                                                                  timestamp=time.time()))
        else:
            print('wut?')
    except pika.exceptions.ConnectionClosed:
        connection = None
        channel = None
        time.sleep(1)
        
    time.sleep(0.1)
