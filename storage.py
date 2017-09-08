import MySQLdb


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
