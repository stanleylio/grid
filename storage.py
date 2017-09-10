import MySQLdb,sys
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


def create_table(conf,table,dbname='grid',user=None,password=None,host='localhost',noreceptiontime=False):
    if user is None or password is None:
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
            user,passwd = cred['mysql']
        self._dbname = dbname

        #print(host,user,passwd,dbname)
        self._conn = MySQLdb.connect(host=host,
                                     user=user,
                                     passwd=passwd,
                                     db=dbname)
        self._cur = self._conn.cursor()

    def get_list_of_columns(self,table):
        self._cur.execute('SELECT * FROM {}.`{}` LIMIT 1;'.format(self._dbname,table))
        return [tmp[0] for tmp in self._cur.description]

    def read_time_range(self,table,time_col,cols,begin,end):
        """Retrieve records in the given time period.
        If end is not specified, end = the moment this is called.
        Would be nice to auto-convert begin and end to suit the type of column time_col
        but that would mean doing a query just to find out the type... not worth it.
        """
        assert type(cols) is list,'cols must be a list of string'
        assert time_col in self.get_list_of_columns(table),'no such time_col: {}'.format(time_col)
        assert type(end) in [float,int]
        if end is None:
            end = time.time()

        assert type(end) in [float,int] and type(begin) in [float,int]
        # also require type(end) == type(begin) == type(stuff in column time_col)

        #cmd = 'SELECT {} FROM {}.`{}` {time_range} ORDER BY {time_col} DESC'.\
        cmd = 'SELECT {} FROM {}.`{}`'.\
                format(','.join(cols),
                       self._dbname,
                       table)
        time_range = ' WHERE {time_col} BETWEEN "{begin}" AND "{end}"'.\
                     format(time_col=time_col,begin=begin,end=end)
        cmd = cmd + time_range
        #print(cmd)
        self._cur.execute(cmd)
        r = self._cur.fetchall()
        self._conn.commit() # see: stale read
        if len(r):
            r = zip(*r)
            # {a:[],b:[]} vs. [[a0,b0],[a1,b1],[a2,b2]...]
            # this is the former, but the latter is more efficient.
            # once the API is public, it is set in stone. lesson learned.
            return {c:r[k] for k,c in enumerate(cols)}
        else:
            return {c:[] for k,c in enumerate(cols)}

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


