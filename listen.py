import pika,socket,traceback,sys,time,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


exchange = 'grid_cnc'
queue_name = 'to_griddemo1'
routing_key = 'griddemo1.c'
user,passwd = cred['rabbitmq']


def mq_init():
    credentials = pika.PlainCredentials(user,passwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    channel = connection.channel()
    return connection,channel

connection,channel = mq_init()

#
channel.exchange_declare(exchange=exchange,exchange_type='fanout',durable=True)

result = channel.queue_declare(queue=queue_name,
                               exclusive=False,
                               durable=True,
                               arguments={'x-message-ttl': 24*3600*1000})
queue_name = result.method.queue
channel.queue_bind(exchange=exchange,
                   queue=queue_name,
                   routing_key=routing_key)

def callback(ch,method,properties,body):
    print(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
logging.info(__file__ + ' is ready')
channel.basic_consume(callback,queue=queue_name)    # ,no_ack=True
try:
    channel.start_consuming()
except KeyboardInterrupt:
    logging.info('user interrupted')
logging.info(__file__ + ' terminated')
