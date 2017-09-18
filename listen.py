# Listen for config change from server via RabbitMQ
# Respond to config param query via XMPRPC
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017
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

table_name = 'config'

# set of defined configurable parameters
# NOT the whole set of parameters defined in the db
schema = [('server_time','REAL NOT NULL'),
          ('sample_interval_second','REAL NOT NULL'),
          ]
param_list = [tmp[0] for tmp in schema]

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

fields = ','.join(['`{}`\t{}'.format(*tmp) for tmp in schema])
cmd = '''CREATE TABLE IF NOT EXISTS `{table_name}` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`device_time`	REAL NOT NULL,
	{fields}
);'''.format(table_name=table_name,fields=fields)
#print(cmd)
cursor.execute(cmd)

conn.commit()


@defer.inlineCallbacks
def run(connection):
    channel = yield connection.channel()
    exchange = yield channel.exchange_declare(exchange=exchange_name,exchange_type='fanout',durable=True)
    queue = yield channel.queue_declare(queue=queue_name,durable=True,exclusive=False,arguments={'x-message-ttl': 24*3600*1000})
    yield channel.queue_bind(exchange=exchange_name,queue=queue_name,routing_key=routing_key)
    yield channel.basic_qos(prefetch_count=5)
    queue_object,consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=True)
    l = task.LoopingCall(read,queue_object)
    l.start(0.01)

@defer.inlineCallbacks
def read(queue_object):
    ch,method,properties,body = yield queue_object.get()
    if body:
        try:
            d = json.loads(body.strip())
            assert 'a' in d and 'd' in d;
            #{'a':'set','d':...}
            if d.get('a',None) != 'set':
                logging.debug('not \'set\'')
                return
            d = d['d']
            assert 'server_time' in d and type(d['server_time']) in [float,int]
            
            a = param_list
            b = d.keys()
            logging.debug('Defined: {}'.format(','.join(a)))
            logging.debug('Supplied: {}'.format(','.join(b)))
            if len(a) > len(b):
                logging.warning('{} defined but not supplied'.format(set(a) - set(b)))
            elif len(a) < len(b):
                logging.error('{} supplied but not defined'.format(set(b) - set(a)))
                return

# if RabbitMQ guarantees in-order delivery then id can be used. otherwise server_time must be used, but
# that assumes server_time is trustworthy (not the case when I first got access to adems.)

# so much work, may as well make it one table per param TODO

            cmd = 'SELECT {} FROM `{}` ORDER BY `server_time` DESC LIMIT 1;'.format(','.join(param_list),table_name)
            cursor.execute(cmd)
            tmp = cursor.fetchone()
# forget about "need_update". how big can a config db grow?
            need_update = False
            if tmp is not None:
                latest = dict(zip(param_list,tmp))
                need_update = any([latest[k] != d[k] for k in d])
            else:
                logging.warning('config db is empty')
                latest = {}
                need_update = True

            if need_update:
                latest.update(d)
            
                assert 'device_time' not in latest
                latest['device_time'] = time.time()

                print(latest)

                cmd = 'INSERT INTO `{}` ({}) VALUES ({})'.\
                      format(table_name,
                             ','.join(latest.keys()),
                             ','.join(['?']*len(latest)))
                #print(cmd)
                cursor.execute(cmd,tuple(latest[k] for k in latest))
                conn.commit()
                print(d)
            else:
                logging.info('no update required')
            #ch.basic_ack(delivery_tag=method.delivery_tag)
            #yield ch.basic_ack(delivery_tag=method.delivery_tag)
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
        try:
            cmd = 'SELECT server_time,sample_interval_second FROM `{}` ORDER BY server_time DESC LIMIT 1;'.format(table_name)
            cursor.execute(cmd)
            conn.commit()
            row = cursor.fetchone()
            #print(row)
            return {'sample_interval_second':row[1]}
        except:
            return {'sample_interval_second':1}
    

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
