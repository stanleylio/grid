# Enable read and write to configuration parameters.
# sqlite3 database as backend. One table per parameter.
# New entries are only added to database only if it's different from existing one.
# Time of change (device's clock) is reocrded.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii
# All Rights Reserved. 2017
import socket,traceback,sys,time,sqlite3,logging
from os.path import exists
from importlib import import_module


logger = logging.getLogger(__name__)


def import_node_config(node=None):
    if node is None:
        node = socket.gethostname()
    return import_module('config.{node}'.format(node=node))


class Config():
    def __init__(self,dbfile,create_if_not_exists=True):
        logger.debug('dbfile={}'.format(dbfile))
        if not (create_if_not_exists or exists(dbfile)):
            raise RuntimeError('{} doesn\'t exist but create_if_not_exists=False'.format(dbfile))
        self.conn = sqlite3.connect(dbfile)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def get(self,variable_name):
        if not self.is_defined(variable_name):
            #return None
            raise LookupError('Variable {} has no defined value'.format(variable_name))
        
        # BY id? BY ts?
        cmd = 'SELECT {variable_name} FROM {variable_name} ORDER BY `id` DESC LIMIT 1;'.\
              format(variable_name=variable_name)
        self.cursor.execute(cmd)
        self.conn.commit()
        tmp = self.cursor.fetchone()
        return tmp[str(variable_name)]  # sqlite doesn't like unicode column name

    def set(self,variable_name,new_value):
        """Attempt to set 'variable_name' to value 'new_value'.
Return True if it new_value is different from variable's previous value; False otherwise"""
        if variable_name not in self.get_list_of_variables():
            logger.debug('new variable {} created'.format(variable_name))
            cmd = '''CREATE TABLE IF NOT EXISTS `{variable_name}` (
                    `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    `ts`	REAL NOT NULL,
                    `{variable_name}`	REAL NOT NULL
            );'''.format(variable_name=variable_name)
            self.cursor.execute(cmd)
            self.conn.commit()

        try:
            tmp = self.get(variable_name)
        except LookupError:
            logger.info('Variable {} is not yet defined'.format(variable_name))
            tmp = None
        if tmp is None or tmp != new_value:
            logger.debug('variable {} set to new value {}'.format(variable_name,new_value))
            cmd = 'INSERT INTO `{variable_name}` (`ts`,`{variable_name}`) VALUES ({ts},{new_value})'.\
                  format(variable_name=variable_name,
                         new_value=new_value,
                         ts=time.time())
            self.cursor.execute(cmd)
            self.conn.commit()
            return True
        else:
            logger.debug('{} is already {}'.format(variable_name,new_value))
            return False

    def is_defined(self,variable_name):
        """True if the table exists AND there is at least one row"""
        try:
            cmd = 'SELECT * FROM {} LIMIT 1;'.format(variable_name)
            self.cursor.execute(cmd)
            self.conn.commit()
            tmp = self.cursor.fetchone()
            return tmp is not None
        except sqlite3.OperationalError:
            return False
        
    def get_list_of_variables(self):
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return sorted([t[0] for t in cursor.fetchall() if not t[0].startswith('sqlite_')])



if '__main__' == __name__:
    exit()
    logger.basicConfig(level=logging.DEBUG)
    
    c = Config('config.db')
    print(c.get('sample_interval_second'))
    c.set('sample_interval_second',0.1)
    print(c.get('sample_interval_second'))

    print(c.get('AVTHD_P'))
    c.set('AVTHD_P',-1)
    print(c.get('AVTHD_P'))
