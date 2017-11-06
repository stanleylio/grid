import socket

gw_id = socket.gethostname()

signals = ['FREQ',
           'AVRMS', 'AVFRMS', 'AIRMS', 'AIFRMS', 'AWATT', 'AFWATT', 'AFVAR',
           'BVRMS', 'BVFRMS', 'BIRMS', 'BIFRMS', 'BWATT', 'BFWATT', 'BFVAR',
           'CVRMS', 'CVFRMS', 'CIRMS', 'CIFRMS', 'CWATT', 'CFWATT', 'CFVAR',
           'TPMON']
