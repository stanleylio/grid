nodeid = '8f1c3a38-d5e2-421a-a12f-a9db155ffc76'
name = 'grid-gw-4'
location = 'CLASSIFIED'
note = 'dummy'


conf = [
    {
        'dbtag':'ts_A',
        'description':'Sample time (gateway)',
    },
    {
        'dbtag':'ts_B',
        'description':'Sample time (PIC, probably from GPS)',
    },
    {
        'dbtag':'FANCY_VAR_1',
        'unit':'unit',
        'description':'description',
    },
    {
        'dbtag':'FANCY_VAR_2',
        'unit':'unit',
        'description':'description',
    },
    {
        'dbtag':'FANCY_VAR_3',
        'unit':'unit',
        'description':'description',
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
