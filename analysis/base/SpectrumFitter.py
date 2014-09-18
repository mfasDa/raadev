'''
Created on 17.09.2014

@author: markusfasel
'''

from ROOT import TF1, TGraph

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
        self.__antider = TGraph()
        self.__antiderNorm = TGraph()
        self.__fitDone = False
        
    def DoFit(self, rangemin, rangemax = 50):
        self.__data.Fit("fitfunction%s"%(self.__name), "N", "", rangemin, rangemax)
        self.__fitDone = True
        self.__ConstructAntiDerivatives()
        
    def GetParameterisation(self):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model
    
    def GetParameterisedValueAt(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model.Eval(x)
    
    def GetIntegralAbove(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__antider.Eval(x)
   
    def GetNormalisedIntegralAbove(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__antiderNorm.Eval(x)

    def CalculateIntegralAbove(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model.Integral(x, 10000)
   
    def CalculateNormalisedIntegralAbove(self, x):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        maxint = 10000
        return self.__model.Integral(x, maxint)/(maxint - x)

    def __ConstructAntiDerivatives(self):
        counter = 0
        for point in range(1,1000):
            self.__antider.SetPoint(counter, float(point), self.CalculateIntegralAbove(float(point)))
            self.__antiderNorm.SetPoint(counter, float(point), self.CalculateNormalisedIntegralAbove(float(point)))
            counter += 1
            
    def CalculateIntegral(self, xmin, xmax):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model.Integral(xmin, xmax)
    
    def CalculateBinned(self, xmin, xmax):
        if not self.__fitDone:
            raise self.SpectrumFitterException()
        return self.__model.Integral(xmin, xmax)/(xmax - xmin)
            
    def GetAntiderivative(self):
        return self.__antider
    
    def GetNormalisedAntiDerivative(self):
        return self.__antiderNorm
        
class MinBiasFitter(SpectrumFitter):
    
    def __init__(self, name, data, fitmin = 15.):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(fitmin, 50.)
        
class TriggeredSpectrumFitter(SpectrumFitter):
    
    def __init__(self, name, data):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(50., 100.)

        