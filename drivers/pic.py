# Refactored version of "new_1.py" from Thai Tran.
#
# Stanley H.I. Lio
# hlio@hawaii.edu

import serial, struct, time

class LocalMeasurements(dict):
    """Class to store local power monitor measurements and update them via UART

    All initialization parameters of :class:`serial.Serial` are accepted. The
    following initialization parameters have different defaults than in
    :class:`serial.Serial`:

    - *port* ('/dev/ttyS1')

    - *baudrate* (115200)

    - *rtscts* (*True*)

    - *timeout* (1)
    """
    signals = ['FREQ',
               'AVRMS', 'AVFRMS', 'AIRMS', 'AIFRMS', 'AWATT', 'AFWATT', 'AFVAR',
               'BVRMS', 'BVFRMS', 'BIRMS', 'BIFRMS', 'BWATT', 'BFWATT', 'BFVAR',
               'CVRMS', 'CVFRMS', 'CIRMS', 'CIFRMS', 'CWATT', 'CFWATT', 'CFVAR',
               'TPMON']

    def __init__(self, port='/dev/ttyS1', baudrate=115200, rtscts=True,
                 timeout=1, **kwargs):
        self.pic = serial.Serial(port=port, baudrate=baudrate, rtscts=rtscts,
                                 timeout=timeout, **kwargs)
        self.pic.reset_input_buffer()
        self.refresh()

    def _sync(self):
        count = 0
        while count < 4:
            if self.pic.read(1) == b';':
                count += 1
            else:
                count = 0

    def refresh(self):
        """Refresh the values of all signals and timestamps."""
        self._sync()
        for signal in self.signals:
            self[signal] = struct.unpack('<f', self.pic.read(4))[0]
        self['ts_pic'] = struct.unpack('<i', self.pic.read(4))[0]
        self['ts_gw'] = time.time()

if '__main__' == __name__:

    from parse_support import pretty_print

    measurements = LocalMeasurements()
    while True:
        print('- - - - -')
        measurements.refresh()
        pretty_print(measurements)
