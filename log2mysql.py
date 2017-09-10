# This taps into the local RabbitMQ exchange and store .samples msgs into MySQL
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved, 2017
import pika,socket,traceback,sys,time,math,MySQLdb,logging,json
from os.path import expanduser,basename
sys.path.append(expanduser('~'))
from parse_support import pretty_print
from storage import storage
from cred import cred


logging.basicConfig(level=logging.INFO)


exchange = 'grid'
nodeid = socket.gethostname()

credentials = pika.PlainCredentials(cred['rabbitmq'][0],cred['rabbitmq'][1])
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
channel = connection.channel()
#channel.queue_delete(queue='nameofqueue')
#exit()

channel.exchange_declare(exchange=exchange,exchange_type='topic',durable=True)
result = channel.queue_declare(queue=basename(__file__),
                               durable=True,
                               arguments={'x-message-ttl':2**31-1}) # ~24 days.

queue_name = result.method.queue
channel.queue_bind(exchange=exchange,
                   queue=queue_name,
                   routing_key='*.r')

def init_storage():
    return storage()
store = init_storage()

#n6last_stored = 0
def callback(ch,method,properties,body):
    global store
    #print(method.routing_key,body)
    try:
        d = json.loads(body)
        d['rt'] = time.time()
        print('= = = = = = = = = = = = = = =')
        pretty_print(d)

        for k in d.keys():
            try:
                if math.isnan(d[k]):
                    d[k] = None
            except TypeError:
                pass

        store.insert(properties.user_id,d)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except MySQLdb.OperationalError:
        traceback.print_exc()
        store = init_storage()
    except:
        traceback.print_exc()
        logging.exception(body)

    #ch.basic_ack(delivery_tag=method.delivery_tag)


logging.info(__file__ + ' is ready')
channel.basic_consume(callback,queue=queue_name)    # ,no_ack=True
try:
    channel.start_consuming()
except KeyboardInterrupt:
    logging.info('user interrupted')
logging.info(__file__ + ' terminated')
