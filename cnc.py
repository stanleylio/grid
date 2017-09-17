import pika,sys,time,traceback,logging,json
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


exchange = 'grid_cnc'
queue_name = 'to_griddemo1'
user,passwd = cred['rabbitmq']


def mq_init():
    credentials = pika.PlainCredentials(user,passwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,exchange_type='fanout',durable=True)
    return connection,channel


connection,channel = None,None


config = {'interval':0.1}


while True:
    #line = '{}: command and control'.format(time.time())
    #print(line)
    try:
        if connection is None or channel is None:
            logging.info('Connection to local exchange closed')
            connection,channel = mq_init()
            logging.info('Connection to local exchange re-established')

        config['ts'] = time.time()
        line = json.dumps(config,separators=(',',':'))
        print(line)
        
        if connection is not None and channel is not None:
            res = channel.basic_publish(exchange,     # name of exchange
                                  '',           # routing key
                                  line,         # payload
                                  properties=pika.BasicProperties(delivery_mode=2,
                                                                  user_id=user,
                                                                  content_type='text/plain',
                                                                  expiration=str(60*1000),
                                                                  timestamp=time.time()))
            print(res)
    except:
        traceback.print_exc()

    time.sleep(5)

connection.close()
