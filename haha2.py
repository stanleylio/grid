import os,sys,traceback,time,logging,pika,socket,json
from os.path import expanduser
sys.path.append(expanduser('~'))
from itertools import izip
from random import random
from datetime import datetime
from cred import cred
from config.griddemo1 import conf


tags = [c['dbtag'] for c in conf]


def random_var(m,sd):
    v = m
    while True:
        v = v + sd*(2*random() - 1)
        yield round(v,3)

vargens = [random_var(380*random(),2*random()) for i in range(len(tags))]

#for v in izip(*vargens):
#    print v
#    time.sleep(0.1)
#exit()


def pretty_print(d):
    """Pretty-print to terminal the given dictionary of readings"""
    max_len = max([len(k) for k in d.keys()])
    if 'node' in d.keys():
        print('From {}:'.format(d['node']))
    if 'ReceptionTime' in d.keys():
        tmp = d['ReceptionTime']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Received at {}'.format(tmp))
    if 'Timestamp' in d.keys():
        tmp = d['Timestamp']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Sampled at {}'.format(tmp))
    if 'ts' in d.keys():
        tmp = d['ts']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Sampled at {}'.format(tmp))
    for k in sorted(set(d.keys()) - set(['Timestamp','node','ReceptionTime','ts'])):
        print('{}{}{}'.format(k,' '*(max_len + 4 - len(k)),d[k]))



exchange = 'grid'
node_id = socket.gethostname()
routing_key = node_id + '.r'
#routing_key = 'griddemo1.r'


def mq_init():
    credentials = pika.PlainCredentials(cred['rabbitmq'][0],cred['rabbitmq'][1])
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,exchange_type='topic',durable=True)
    return connection,channel


connection,channel = mq_init()


#while True:
for v in izip(*vargens):
    #line = str(time.time())
    #print(line)
    v = dict(zip(tags,v))
    v['ts'] = time.time()

    print('\x1b[2J\x1b[;H')
    pretty_print(v)
    line = json.dumps(v,separators=(',',':'))
    #continue
    
    try:
        if connection is None or channel is None:
            logging.info('Connection to local exchange closed')
            connection,channel = mq_init()
            logging.info('Connection to local exchange re-established')

        if connection is not None and channel is not None:
            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=line,
                                  properties=pika.BasicProperties(delivery_mode=1,
                                                                  content_type='text/plain',
                                                                  expiration=str(60*24*3600*1000),
                                                                  timestamp=time.time()))
        else:
            print('wut?')
    except pika.exceptions.ConnectionClosed:
        connection = None
        channel = None
        time.sleep(1)
        
    time.sleep(0.2)
