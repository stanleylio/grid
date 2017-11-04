# Package to retrieve data from the power monitor database via the json api.
#
# Charles White, Kevin Davies, Stanley Lio

import numpy as np
import pandas as pd
import requests
import time

from datetime import datetime

URL_TEMPLATE = "http://adems.soest.hawaii.edu/api/v1?node={node}&variable={variable}&begin={begin}&end={end}"

class MeterData(object):
    """Class for power monitor data via the json api

    Valid variables:
        FREQ,
        AVRMS, AVFRMS, AIRMS, AIFRMS, AWATT, AFWATT, AFVAR, AFTHETA, AFPF, 
        BVRMS, BVFRMS, BIRMS, BIFRMS, BWATT, BFWATT, BFVAR, BFTHETA, BFPF, 
        CVRMS, CVFRMS, CIRMS, CIFRMS, CWATT, CFWATT, CFVAR, CFTHETA, CFPF, 
        TPMON, ts_pic

    Access these variables as attributes.
    """
    def __init__(self, begin=time.time() - 24*3600, end=time.time(), node="grid-gw-3"):
        self.begin = begin
        self.end = end
        self.node = node

    @property
    def AFTHETA(self):
        """Fundamental phase angle on line A"""
        return np.arctan2(self.AFVAR, self.AFWATT)

    @property
    def BFTHETA(self):
        """Fundamental phase angle on line B"""
        return np.arctan2(self.BFVAR, self.BFWATT)

    @property
    def CFTHETA(self):
        """Fundamental phase angle on line C"""
        return np.arctan2(self.CFVAR, self.CFWATT)

    @property
    def AFPF(self):
        """Fundamental power factor on line A"""
        FWATT = self.AFWATT
        return FWATT/(np.square(FWATT) + np.square(self.AFVAR))

    @property
    def BFPF(self):
        """Fundamental power factor on line B"""
        FWATT = self.BFWATT
        return FWATT/(np.square(FWATT) + np.square(self.BFVAR))

    @property
    def CFPF(self):
        """Fundamental power factor on line C"""
        FWATT = self.CFWATT
        return FWATT/(np.square(FWATT) + np.square(self.CFVAR))

    @property
    def ATHD(self):
        """Total harmonic distortion (voltage) on line A"""
        FVRMS = self.AFVRMS
        return np.sqrt(np.square(self.AVRMS) + np.square(FVRMS))/FVRMS

    @property
    def BTHD(self):
        """Total harmonic distortion (voltage) on line B"""
        FVRMS = self.BFVRMS
        return np.sqrt(np.square(self.BVRMS) + np.square(FVRMS))/FVRMS

    @property
    def CTHD(self):
        """Total harmonic distortion (voltage) on line C"""
        FVRMS = self.CFVRMS
        return np.sqrt(np.square(self.CVRMS) + np.square(FVRMS))/FVRMS

    @property
    def ATDD(self):
        """Total demand distortion (current) on line A"""
        FIRMS = self.AFIRMS
        return np.sqrt(np.square(self.AIRMS) + np.square(FIRMS))/FIRMS

    @property
    def BTDD(self):
        """Total demand distortion (current) on line B"""
        FIRMS = self.BFIRMS
        return np.sqrt(np.square(self.BIRMS) + np.square(FIRMS))/FIRMS

    @property
    def CTDD(self):
        """Total demand distortion (current) on line C"""
        FIRMS = self.CFIRMS
        return np.sqrt(np.square(self.CIRMS) + np.square(FIRMS))/FIRMS

    def __getattr__(self, variable):
        url = URL_TEMPLATE.format(node=self.node, variable=variable, begin=self.begin, end=self.end)
        time, data = zip(*requests.get(url).json())
        return pd.DataFrame(np.array(data), pd.to_datetime(time, unit='s'))

if '__main__' == __name__:

    import matplotlib.pyplot as plt

    # Example: Plot the past 24hr of data.
    d = MeterData(node="grid-gw-3")
    d.AVRMS.plot()
    plt.show()
