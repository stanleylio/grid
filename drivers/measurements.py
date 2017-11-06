import serial, struct, time

from . import signals, gw_id

class LocalMeasurements(dict):
    """Class to store local power monitor measurements and update them via UART

    This is a dictionary.  Once :meth:`refresh` is called, there will be items 
    (key, value pairs) for all signals and timestamps.  Each time 
    :meth:`refresh` is subsequently called, the values will be updated.
 
    Initialization parameters
    -------------------------

    *callback* (*None*) - a function that will be called each time 
    :meth:`refresh` is called 

        The first argument is the meter id, which is the gateway id (*gw_id* 
        from this package) + '.0'.  The second argument is this dictionary.

    All initialization parameters of :class:`serial.Serial` are also accepted. 
    The following initialization parameters have different defaults than in
    :class:`serial.Serial`:

    - *port* ('/dev/ttyS1')

    - *baudrate* (115200)

    - *rtscts* (*True*)

    - *timeout* (1) - the timeout period in seconds for each read operation (for 
      the value of each item)
    """

    def __init__(self, callback=None, port='/dev/ttyS1', baudrate=115200, 
                 rtscts=True, timeout=1, **kwargs):
        self.uart = serial.Serial(port=port, baudrate=baudrate, rtscts=rtscts,
                                  timeout=timeout, **kwargs)
        self.uart.reset_input_buffer()
        self.callback = callback

    def _sync(self):
        count = 0
        while count < 4:
            if self.uart.read(1) == b';':
                count += 1
            else:
                count = 0
        # TODO: Implement COBS.

    def refresh(self):
        """Refresh the values of all signals and timestamps."""
        self._sync()
        # TODO: Validate the checksum or CRC (will need to read the entire frame up front).
        for signal in signals:
            self[signal] = struct.unpack('<f', self.uart.read(4))[0]
        self['ts_pic'] = struct.unpack('<i', self.uart.read(4))[0]
        self['ts_gw'] = time.time()
        if self.callback:
            self.callback(gw_id + '.0', self) # TODO: Prepare the database to expect '.0' to be appended for local measurements.


class RemoteMeasurements(dict):
    """Class to store remote power monitor measurements and update them via UART

    This is a dictionary with items for each remote power monitor.  The value 
    of each item is a dictionary with all the signals and timestamps for a 
    single remote meter.  Once :meth:`refresh` is called, there will be items 
    (key, value pairs) for all signals and timestamps.  

    Initialization parameters
    -------------------------

    *callback* (*None*) - a function that will be called each time 
    :meth:`refresh` is called 

        The dictionary representing the meter that was last updated will be 
        passed as an argument.

    All initialization parameters of :class:`serial.Serial` are also accepted. 
    The following initialization parameters have different defaults than in
    :class:`serial.Serial`:

    - *port* ('/dev/ttyS2')

    - *baudrate* (115200)

    - *rtscts* (*True*)

    - *timeout* (1)
    """

    def __init__(self, callback=None, port='/dev/ttyS2', baudrate=115200, 
                 rtscts=True, timeout=1, **kwargs):
        self.uart = serial.Serial(port=port, baudrate=baudrate, rtscts=rtscts,
                                  timeout=timeout, **kwargs)
        self.uart.reset_input_buffer()
        self.callback = callback

    def _sync(self):
        count = 0
        while count < 4:
            if self.uart.read(1) == b';':
                count += 1
            else:
                count = 0
        # TODO: Implement COBS.

    def refresh(self):
        """Refresh the values of all signals and timestamps."""
        self._sync()
        # TODO: Deconstruct the XBee frame here.
        # TODO: Validate the checksum or CRC (will need to read the entire frame up front).
        meter_num = 1 # Set meter_num according to the remote meter that is reporting data.
        if meter_num not in self:
            self[meter_num] = {}
        for signal in signals:
            self[meter_num][signal] = struct.unpack('<f', self.uart.read(4))[0]
        self[meter_num]['ts_pic'] = struct.unpack('<i', self.uart.read(4))[0]
        self[meter_num]['ts_gw'] = time.time()
        if self.callback:
            self.callback("{}.{}".format(gw_id, meter_num), self[meter_num]) 
            # TODO: Prepare the database to expect '.n' to be appended for remote measurements, where n (>0) is the remote meter number.

if '__main__' == __name__:

    from parse_support import pretty_print

    measurements = LocalMeasurements()
    while True:
        print('- - - - -')
        measurements.refresh()
        pretty_print(measurements)
