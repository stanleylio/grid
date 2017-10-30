# Refactored version of "new_1.py".
#
# Stanley H.I. Lio
# hlio@hawaii.edu
import serial,struct,csv
from datetime import datetime


tags = ['FREQ',
        'AVRMS','AVFRMS','AIRMS','AIFRMS','AWATT','AFWATT','AFVAR',
        'BVRMS','BVFRMS','BIRMS','BIFRMS','BWATT','BFWATT','BFVAR',
        'CVRMS','CVFRMS','CIRMS','CIFRMS','CWATT','CFWATT','CFVAR',
        'TPMON',
        'ts_pic']


class PIC:
    def __init__(self):
        self.pic = serial.Serial(port='/dev/ttyS1',baudrate=115200,rtscts=True,timeout=1)
        self.pic.reset_input_buffer()

    def read(self):
        """Sample all variables and return as a dictionary."""
        self._sync()
        d = {}
        for key in tags:
            pic_response = self.pic.read(4)
            if 'ts_pic' == key:
                value = struct.unpack('<i',pic_response)[0]
                time_now = datetime.fromtimestamp(value)
            else:
                value = struct.unpack('<f',pic_response)[0]

            d[key] = value
        return d

    def _sync(self):
# TODO add max_retry to avoid potential deadlock
        count = 0
        while count < 4:
            if b';' == self.pic.read(1):
                count += 1
            else:
                count = 0

    def _get_tags(self):
        return tags


if '__main__' == __name__:

    pic = PIC()
    while True:
        print('- - - - -')
        print(pic.read())
