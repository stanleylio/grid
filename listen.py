import pika,socket,traceback,sys,time,logging,json,sqlite3
from os.path import expanduser
sys.path.append(expanduser('~'))
from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer,reactor,protocol,task
from twisted.web import xmlrpc,server
from cred import cred


exchange_name = 'grid_cnc'
queue_name = 'to_griddemo1'
routing_key = 'griddemo1.c'
user,passwd = cred['rabbitmq']


'''def mq_init():
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
                   routing_key=routing_key)'''


dbfile = '/home/griddemo1/config.db'
conn = sqlite3.connect(dbfile)
cursor = conn.cursor()
cmd = 'CREATE TABLE IF NOT EXISTS `config` (ts DOUBLE, interval DOUBLE);'
cursor.execute(cmd)


@defer.inlineCallbacks
def run(connection):
    channel = yield connection.channel()
    exchange = yield channel.exchange_declare(exchange=exchange_name,exchange_type='fanout',durable=True)
    queue = yield channel.queue_declare(queue=queue_name,durable=True,exclusive=False,arguments={'x-message-ttl': 24*3600*1000})
    yield channel.queue_bind(exchange=exchange_name,queue=queue_name,routing_key=routing_key)
    yield channel.basic_qos(prefetch_count=5)
    queue_object,consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=False)
    l = task.LoopingCall(read,queue_object)
    l.start(0.01)

@defer.inlineCallbacks
def read(queue_object):
    ch,method,properties,body = yield queue_object.get()
    if body:
        try:
            d = json.loads(body.strip())
            cmd = 'INSERT INTO `config` (ts,interval) VALUES (?,?)'
            cursor.execute(cmd,(d['ts'],d['interval']))
            conn.commit()
            print(d)
            #ch.basic_ack(delivery_tag=method.delivery_tag)
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            traceback.print_exc()


'''def callback(ch,method,properties,body):
    #print(body)
    try:
        d = json.loads(body)
        cmd = 'INSERT INTO `config` (ts,interval) VALUES (?,?)'
        cursor.execute(cmd,(d['ts'],d['interval']))
        conn.commit()
        print(d)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except:
        traceback.print_exc()'''


class P(xmlrpc.XMLRPC):
    def xmlrpc_get_config(self):
        dbfile = '/home/griddemo1/config.db'
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cmd = 'SELECT ts,interval FROM `config` ORDER BY ts DESC LIMIT 1;'
        cursor.execute(cmd)
        conn.commit()
        row = cursor.fetchone()
        #print(row)
        return dict(zip(['ts','interval'],list(row)))
    

logging.info(__file__ + ' is ready')
credentials = pika.PlainCredentials(user,passwd)
parameters = pika.ConnectionParameters(credentials=credentials)
cc = protocol.ClientCreator(reactor,twisted_connection.TwistedProtocolConnection,parameters)
d = cc.connectTCP('localhost',5672)
d.addCallback(lambda protocol: protocol.ready)
d.addCallback(run)
reactor.listenTCP(8000,server.Site(P()))
reactor.run()

#channel.basic_consume(callback,queue=queue_name)    # ,no_ack=True
#try:
#    channel.start_consuming()
#except KeyboardInterrupt:
#    logging.info('user interrupted')
logging.info(__file__ + ' terminated')
