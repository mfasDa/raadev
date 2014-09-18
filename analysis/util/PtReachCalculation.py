'''
Created on 18.09.2014

@author: markusfasel
'''
from base.SpectrumFitter import MinBiasFitter, TriggeredSpectrumFitter
from scipy.optimize import fsolve

class PtReachCalculator(object):
    """
    classdocs
    """

    def __init__(self, name, data, isMinBias, limit):
        '''
        Constructor
        '''
        self.__fitter = None
        if isMinBias:
            self.__fitter = MinBiasFitter(name, data)
        else:
            self.__fitter = TriggeredSpectrumFitter(name, data)
        self.__limit = limit
        
    def GetPtReach(self, numberOfEvents):
        """
        Get the Pt reach for a given number of events
        """
        model = lambda p : numberOfEvents * self.__fitter.GetParameterisedValueAt(p) - self.__limit
        initialGuess = 10.
        result = fsolve(model, initialGuess)
        return result
    
    def GetPtReachForIntegral(self, numberOfEvents):
        """
        Get the Pt reach for a given number of events using integrated yield above 
        """
        model = lambda p : numberOfEvents * self.__fitter.GetNormalisedIntegralAbove(p) - self.__limit
        initialGuess = 10.
        result = fsolve(model, initialGuess)
        return result
