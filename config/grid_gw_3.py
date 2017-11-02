name = 'grid-gw-3'
location = 'CLASSIFIED'
note = 'nanopi-based, "real" data, norminal 1 sps'


conf = [
    {
        'dbtag':'ts_gw',
        'description':'Sample time (gateway)',
    },
    {
        'dbtag':'ts_pic',
        'description':'Sample time (PIC, probably from GPS)',
    },
    {
        'dbtag':'TPMON',
        'unit':'Deg.C',
        'description':'ADE9000 Temperature',
    },
    {
        'dbtag':'TSBC',
        'unit':'Deg.C',
        'description':'nanopi Temperature',
    },

    {
        'dbtag':'FREQ',
        'unit':'Hz',
    },

    # RMS Voltage
    {
        'dbtag':'AVRMS',
        'unit':'V',
        'description':'RMS voltage phase A)',
    },
    {
        'dbtag':'BVRMS',
        'unit':'V',
        'description':'RMS voltage phase B)',
    },
    {
        'dbtag':'CVRMS',
        'unit':'V',
        'description':'RMS voltage phase C)',
    },

    # Fundamental RMS Voltage
    {
        'dbtag':'AVFRMS',
        'unit':'V',
        'description':'Fundamental RMS Voltage (phase A)',
    },
    {
        'dbtag':'BVFRMS',
        'unit':'V',
        'description':'Fundamental RMS Voltage (phase B)',
    },
    {
        'dbtag':'CVFRMS',
        'unit':'V',
        'description':'Fundamental RMS Voltage (phase C)',
    },

    # RMS Current
    {
        'dbtag':'AIRMS',
        'unit':'A',
        'description':'RMS Current (phase A)',
    },
    {
        'dbtag':'BIRMS',
        'unit':'A',
        'description':'RMS Current (phase B)',
    },
    {
        'dbtag':'CIRMS',
        'unit':'A',
        'description':'RMS Current (phase C)',
    },

    # Fundamental RMS Current
    {
        'dbtag':'AIFRMS',
        'unit':'A',
        'description':'Fundamental RMS Current (phase A)',
    },
    {
        'dbtag':'BIFRMS',
        'unit':'A',
        'description':'Fundamental RMS Current (phase B)',
    },
    {
        'dbtag':'CIFRMS',
        'unit':'A',
        'description':'Fundamental RMS Current (phase C)',
    },
    
    # Total active power
    {
        'dbtag':'AWATT',
        'unit':'W',
        'description':'Total active power (phase A)',
    },
    {
        'dbtag':'BWATT',
        'unit':'W',
        'description':'Total active power (phase B)',
    },
    {
        'dbtag':'CWATT',
        'unit':'W',
        'description':'Total active power (phase C)',
    },
    
    # Fundamental active power
    {
        'dbtag':'AFWATT',
        'unit':'W',
        'description':'Fundamental active power (phase A)',
    },
    {
        'dbtag':'BFWATT',
        'unit':'W',
        'description':'Fundamental active power (phase B)',
    },
    {
        'dbtag':'CFWATT',
        'unit':'W',
        'description':'Fundamental active power (phase C)',
    },
    
    # Fundamental reactive power
    {
        'dbtag':'AFVAR',
        'unit':'W',
        'description':'Fundamental reactive power (phase A)',
    },
    {
        'dbtag':'BFVAR',
        'unit':'W',
        'description':'Fundamental reactive power (phase B)',
    },
    {
        'dbtag':'CFVAR',
        'unit':'W',
        'description':'Fundamental reactive power (phase C)',
    },
]


if '__main__' == __name__:
    for c in conf:
        print('- - -')
        for k,v in c.items():
            print(k,':',v)

    import sys
    sys.path.append('..')
    from storage import create_table
    create_table(conf,__file__.split('.')[0].replace('_','-'))
