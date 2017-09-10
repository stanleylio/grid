import MySQLdb,sys
from os.path import expanduser
sys.path.append(expanduser('~'))


def create_table(conf,table,dbname='grid',user=None,password=None,host='localhost',noreceptiontime=False):
    if user is None or password is None:
        from cred import cred
        user,passwd = cred['mysql']
        
    if not noreceptiontime:
        conf.insert(0,{'dbtag':'rt','dbtype':'DOUBLE PRIMARY KEY'})
    
    conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=dbname)
    cur = conn.cursor()

    tmp = ','.join([' '.join(tmp) for tmp in [(column['dbtag'],column.get('dbtype','DOUBLE')) for column in conf]])
    cmd = 'CREATE TABLE IF NOT EXISTS {}.`{}` ({})'.format(dbname,table,tmp)
    print(cmd)
    cur.execute(cmd)


class storage():
    def __init__(self,dbname='grid',user='root',passwd=None,host='localhost'):
        if passwd is None:
            from cred import cred
            user,passwd = cred['mysql']
        self._dbname = dbname

        #print(host,user,passwd,dbname)
        self._conn = MySQLdb.connect(host=host,
                                     user=user,
                                     passwd=passwd,
                                     db=dbname)
        self._cur = self._conn.cursor()

    def insert(self,table,sample):
        # strip the keys not defined in the db
        sample = {k:sample[k] for k in self.get_list_of_columns(table) if k in sample}
        cols,vals = zip(*sample.items())
        cmd = 'INSERT IGNORE INTO {}.`{table}` ({cols}) VALUES ({vals})'.\
              format(self._dbname,
                     table=table,
                     cols=','.join(cols),
                     vals=','.join(['%s']*len(cols)))
        #print(cmd)
        self._cur.execute(cmd,vals)
        self._conn.commit()


