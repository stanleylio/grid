import xmlrpclib,sqlite3
from SimpleXMLRPCServer import SimpleXMLRPCServer


dbfile = '/home/griddemo1/config.db'
conn = sqlite3.connect(dbfile)
cursor = conn.cursor()
#cmd = 'CREATE TABLE IF NOT EXISTS `config` (ts DOUBLE, interval DOUBLE);'
#cursor.execute(cmd)

def get_config():
    cmd = 'SELECT ts,interval FROM `config` ORDER BY ts DESC LIMIT 1;'
    cursor.execute(cmd)
    conn.commit()
    row = cursor.fetchone()
    print(row)
    return dict(zip(['ts','interval'],list(row)))

server = SimpleXMLRPCServer(('localhost',8000))
server.register_function(get_config,'get_config')
server.serve_forever()
