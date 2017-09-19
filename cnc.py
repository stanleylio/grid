#/usr/bin/python3
# "Command and Control"
# Change the parameter "sample_interval_second" with the argument passed, like so:
#   python3 cnc.py 0.5
# griddemo1 sample interval is now 0.5 second.
import pika,sys,time,traceback,logging,json,argparse
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


exchange = 'grid_cnc'
queue_name = 'to_griddemo1'
user,passwd = cred['rabbitmq']


parser = argparse.ArgumentParser()
parser.add_argument('sample_interval_second',type=float)
args = parser.parse_args()


def mq_init():
    credentials = pika.PlainCredentials(user,passwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,exchange_type='fanout',durable=True)
    return connection,channel


connection,channel = None,None


if args.sample_interval_second < 0.005 or args.sample_interval_second > 3600:
    logging.warning('something something out of range...')
    exit()

config = {'sample_interval_second':args.sample_interval_second}


#line = '{}: command and control'.format(time.time())
#print(line)
if connection is None or channel is None:
    logging.info('Connection to local exchange closed')
    connection,channel = mq_init()
    logging.info('Connection to local exchange re-established')

#config['server_time'] = time.time()
m = {'a':'set','d':config}
line = json.dumps(m,separators=(',',':'))
print(line)

if connection is not None and channel is not None:
    res = channel.basic_publish(exchange,     # name of exchange
                          '',           # routing key
                          line,         # payload
                          properties=pika.BasicProperties(delivery_mode=2,
                                                          user_id=user,
                                                          content_type='text/plain',
                                                          expiration=str(60*1000)))
    print(res)

connection.close()
