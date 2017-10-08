name = 'griddemo2'
location = 'Classified'
note = 'nanopi-based, dummy data, norminal 1 sps'

conf = [
    {
        'dbtag':'ts',
        'description':'Sample time (pi/bone RTC)',
    },
    {
        'dbtag':'TEMP',
        'description':'ADE9000 Temperature',
        'unit':'Deg.C',
    },

    # RMS voltage for 3 phases (call it AVRMS, BVRMS, CVRMS)
    {
        'dbtag':'AVRMS',
        'unit':'V',
    },
    {
        'dbtag':'BVRMS',
        'unit':'V',
    },
    {
        'dbtag':'CVRMS',
        'unit':'V',
    },

    # RMS current for 3 phases (AIRMS, BIRMS, CIRMS)
    {
        'dbtag':'AIRMS',
        'unit':'A',
    },
    {
        'dbtag':'BIRMS',
        'unit':'A',
    },
    {
        'dbtag':'CIRMS',
        'unit':'A',
    },
    
    # Voltage total harmonic distortion for 3 phases (AVTHD, BVTHD, CVTHD)
    {
        'dbtag':'AVTHD',
        'unit':'%',
    },
    {
        'dbtag':'BVTHD',
        'unit':'%',
    },
    {
        'dbtag':'CVTHD',
        'unit':'%',
    },
    
    # Current total harmonic distortion for 3 phases (AITHD, BITHD, CITHD)
    {
        'dbtag':'AITHD',
        'unit':'%',
    },
    {
        'dbtag':'BITHD',
        'unit':'%',
    },
    {
        'dbtag':'CITHD',
        'unit':'%',
    },
    
    # Total active power for 3 phases (AWATT, BWATT, CWATT)
    {
        'dbtag':'AWATT',
        'unit':'W',
    },
    {
        'dbtag':'BWATT',
        'unit':'W',
    },
    {
        'dbtag':'CWATT',
        'unit':'W',
    },
    
    # Fundamental active power for 3 phases (AFWATT, BFWATT, CFWATT)
    {
        'dbtag':'AFWATT',
        'unit':'W',
    },
    {
        'dbtag':'BFWATT',
        'unit':'W',
    },
    {
        'dbtag':'CFWATT',
        'unit':'W',
    },
    
    # Fundamental reactive power for 3 phases (AFVAR, BFVAR, CFVAR)
    {
        'dbtag':'AFVAR',
        'unit':'W',
    },
    {
        'dbtag':'BFVAR',
        'unit':'W',
    },
    {
        'dbtag':'CFVAR',
        'unit':'W',
    },

    # Frequency (FREQ)
    {
        'dbtag':'FREQ',
        'unit':'Hz',
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
