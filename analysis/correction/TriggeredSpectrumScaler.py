'''
Created on 22.09.2014

@author: markusfasel
'''

from base.SpectrumFitter import MinBiasFitter, TriggeredSpectrumFitter
import numpy as np

class TriggeredSpectrumScaler(object):
    '''
    classdocs
    '''


    def __init__(self, minbiasspectrum, triggeredSpectrum):
        """
        Constructor
        """
        self.__triggeredspectrum = triggeredSpectrum
        self.__mbfitter = MinBiasFitter("minbiasfitter", minbiasspectrum)
        self.__trfitter = TriggeredSpectrumFitter("triggeredfittter", self.__triggeredspectrum)
        self.__isScaled = False
        
    def ScaleDownTriggeredSpectrum(self):
        """
        Scale down the triggered spectrum by a mean scale factor
        evaluated from the two fits above 60 GeV
        """
        if not self.__isScaled:
            pointlist = [60,65,70,75,80,85]
            scalingfactors = []
            for point in pointlist:
                scalingfactors.append(self.__mbfitter.GetParameterisedValueAt(point)/self.__trfitter.GetParameterisedValueAt(point))
            scalingfactor = np.array(scalingfactors, np.float64).mean()
            print "Using scaling factor %.2f" %(scalingfactor)
            self.__triggeredspectrum.Scale(scalingfactor)
            self.__isScaled = True
        
    def GetScaledTriggeredSpectrum(self):
        if not self.__isScaled:
            self.ScaleDownTriggeredSpectrum()
        return self.__triggeredspectrum