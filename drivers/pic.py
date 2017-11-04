# Refactored version of "new_1.py" from Thai Tran.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
import serial, struct

tags = ['FREQ',
        'AVRMS', 'AVFRMS', 'AIRMS', 'AIFRMS', 'AWATT', 'AFWATT', 'AFVAR',
        'BVRMS', 'BVFRMS', 'BIRMS', 'BIFRMS', 'BWATT', 'BFWATT', 'BFVAR',
        'CVRMS', 'CVFRMS', 'CIRMS', 'CIFRMS', 'CWATT', 'CFWATT', 'CFVAR',
        'TPMON']

class PIC:
    def __init__(self):
        self.pic = serial.Serial(port='/dev/ttyS1', baudrate=115200, rtscts=True, timeout=1)
        self.pic.reset_input_buffer()

    def read(self):
        """Sample all variables and return as a dictionary."""
        self._sync():
        d = {tag: struct.unpack('<f', self.pic.read(4))[0] for tag in tags}
        d['ts_pic'] = struct.unpack('<i', self.pic.read(4))[0]
        return d

    def _sync(self):
        count = 0
        while count < 4:
            if self.pic.read(1) == b';':
                count += 1
            else:
                count = 0

    def _get_tags(self):
        return tags + ['ts_pic']

if '__main__' == __name__:

    pic = PIC()
    while True:
        print('- - - - -')
        print(pic.read())
