'''
Created on 17.09.2014

@author: markusfasel
'''

from ROOT import TF1

class SpectrumFitter:
    '''
    Class fitting a raw spectrum
    '''
    
    class SpectrumFitterException(Exception):
        
        def __init__(self):
            pass
        
        def __str_(self):
            return "Fit of the spectrum not yet performed"

    def __init__(self, name, spectrum):
        '''
        Constructor
        '''
        self.__name = name
        self.__data = spectrum
        self.__model = TF1("fitfunction%s"%(self.__name), "[0] * TMath::Power(x,[1])", 0., 100.)
        self.__fitDone = False
        
    def DoFit(self, rangemin, rangemax = 50):
        self.__data.Fit("fitfunction%s"%(self.__name), "N", "", rangemin, rangemax)
        self.__fitDone = True
        
    def GetParameterisation(self):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model
    
    def GetParameterisedValueAt(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        self.__model.Eval(x)
        
class MinBiasFitter(SpectrumFitter):
    
    def __init__(self, name, data):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(15., 50.)
        
class TriggeredSpectrumFitter(SpectrumFitter):
    
    def __init__(self, name, data):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(50., 100.)

        