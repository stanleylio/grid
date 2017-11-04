# Package to data from the power monitor database via the json api.
#
# Charles White, Kevin Davies, Stanley Lio

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

from datetime import datetime

URL_TEMPLATE = "http://adems.soest.hawaii.edu/api/v1?node={node}&variable={variable}&begin={begin}&end={end}"

class MeterData(object):
    """Class for power monitor data via the json api
    """
    def __init__(self, begin=time.time() - 24*3600, end=time.time(), node="grid-gw-3"):
        self.begin = begin
        self.end = end
        self.node = node

    @property
    def ATHETA(self):
        return np.arctan2(self.AFVAR, self.AFWATT)

    @property
    def BTHETA(self):
        return np.arctan2(self.BFVAR, self.BFWATT)

    @property
    def CTHETA(self):
        return np.arctan2(self.CFVAR, self.CFWATT)

    @property
    def APF(self):
        FWATT = self.AFWATT
        return FWATT/(np.square(FWATT) + np.square(self.AFVAR))

    @property
    def BPF(self):
        FWATT = self.BFWATT
        return FWATT/(np.square(FWATT) + np.square(self.BFVAR))

    @property
    def CPF(self):
        FWATT = self.CFWATT
        return FWATT/(np.square(FWATT) + np.square(self.CFVAR))

    def __getattr__(self, variable):
        url = URL_TEMPLATE.format(node=self.node, variable=variable, begin=self.begin, end=self.end)
        time, data = zip(*requests.get(url).json())
        return pd.DataFrame(np.array(data), pd.to_datetime(time, unit='s'))

    def __getitem__(self, variable):
        return self.__getattr__(variable)

if '__main__' == __name__:

    # Example: Plot the past 24hr of data.
    d = MeterData(node="grid-gw-3")
    d.AVRMS.plot()
    plt.show()
