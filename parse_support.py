from datetime import datetime


def pretty_print(d):
    """Pretty-print to terminal the given dictionary of readings"""
    max_len = max([len(k) for k in d.keys()])
    if 'node' in d.keys():
        print('From {}:'.format(d['node']))
    if 'ReceptionTime' in d.keys():
        tmp = d['ReceptionTime']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Received at {}'.format(tmp))
    if 'Timestamp' in d.keys():
        tmp = d['Timestamp']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Sampled at {}'.format(tmp))
    if 'ts' in d.keys():
        tmp = d['ts']
        if isinstance(tmp,float):
            tmp = datetime.fromtimestamp(tmp)
        print('Sampled at {}'.format(tmp))
    for k in sorted(set(d.keys()) - set(['Timestamp','node','ReceptionTime','ts'])):
        print('{}{}{}'.format(k,' '*(max_len + 4 - len(k)),d[k]))
