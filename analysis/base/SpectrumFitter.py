'''
Created on 17.09.2014

@author: markusfasel
'''

from ROOT import TF1, TGraph, TH1F

class FitModel:
    
    def __init__(self):
        self._model = None
        
    def GetFunction(self):
        return self._model
    
    def SetFunctionName(self, name):
        self._model.SetName(name)
        
    def GetFunctionName(self):
        return self._model.GetName()
    
    def SetParLimits(self, parnum, parmin, parmax):
        self._model.SetParLimits(parnum, parmin, parmax)
        
    def SetParameter(self, parnum, parval):
        self._model.SetParameter(parnum, parval)
        
    def FixParameter(self, parnum, parval):
        self._model.FixParameter(parnum, parval)
        
    def GetParValue(self, parnum):
        return self._model.GetParameter(parnum)
        
class ExpoModel(FitModel):
    
    def __init__(self):
        self._model = TF1("expoBin", "expo", 0, 100)
    
class PowerLawModel(FitModel):
    
    def __init__(self):
        self._model = TF1("fitfunctionPowerlaw", "[0] * TMath::Power(x,[1])", 0., 100.)
    
class ModifiedHagedornModel(FitModel):
    
    def __init__(self):
        self._model = TF1("fitfunctionModHagedorn", "[0]/TMath::Power(TMath::Exp(-[1]*x - [2]*x*x) + x/[3], [4])", 0., 100.)
        self._model.SetParName(0, "A")
        self._model.SetParName(1, "a")
        self._model.SetParName(2, "b")
        self._model.SetParName(3, "p0")
        self._model.SetParName(4, "n")
        # Force all parameters to be positive 
        self._model.SetParLimits(0, 1e-5, 10000)
        self._model.SetParLimits(1, 1e-3, 1)
        self._model.SetParLimits(2, 1e-3, 1)
        self._model.SetParLimits(3, 1e-3, 1)
        self._model.SetParLimits(4, 1e-5, 10)
        self._model.SetParameter(0, 100)
        self._model.SetParameter(1, 0.5)
        self._model.SetParameter(2, 0.5)
        self._model.SetParameter(3, 0.5)
        self._model.SetParameter(4, 5.)
        
class ExpoModifiedHagedornModel(FitModel):
    
    def __init__(self):
        self._model = TF1("fitfunctionModHagedorn", "expo(0) + [2]/TMath::Power(TMath::Exp(-[3]*x - [4]*x*x) + x/[5], [6])", 0., 100.)
        self._model.SetParName(2, "A");
        self._model.SetParName(3, "a");
        self._model.SetParName(4, "b");
        self._model.SetParName(5, "p0");
        self._model.SetParName(6, "n");
  
        # Force all parameters to be positive 
        self._model.SetParLimits(2, 1e-5, 1000000);
        self._model.SetParLimits(3, 1e-7, 1000);
        self._model.SetParLimits(4, 1e-7, 1000);
        self._model.SetParLimits(3, 1e-7, 1000);
        self._model.SetParLimits(5, 1e-7, 1000);
        self._model.SetParameter(2, 100);
        self._model.SetParameter(3, 0.5);
        self._model.SetParameter(4, 0.5);
        self._model.SetParameter(5, 0.5);
        self._model.SetParameter(6, 5.);

class SpectrumFitter:
    '''
    Class fitting a raw spectrum
    '''
    
    class SpectrumFitterException(Exception):
        
        def __init__(self):
            pass
        
        def __str_(self):
            return "Fit of the spectrum not yet performed"

    def __init__(self, name, spectrum, fitmodel = None):
        '''
        Constructor
        '''
        self._name = name
        self._data = spectrum
        self._model = fitmodel
        if not self._model:
            self._model = PowerLawModel()
        self._fitDone = False
        
    def SetFitModel(self, fitmodel):
        self._model = fitmodel
        
    def DoFit(self, rangemin, rangemax = 50):
        self._data.Fit(self._model.GetFunction(), "N", "", rangemin, rangemax)
        self._fitDone = True
        
    def GetParameterisation(self):
        if not self._fitDone:
            raise self.SpectrumFitterException()
        return self._model.GetFunction()
    
    def GetParameterisedValueAt(self, x):
        if not self._fitDone:
            raise self.SpectrumFitterException()
        return self._model.GetFunction().Eval(x)
   
    def CalculateIntegralAbove(self, x):
        if not self._fitDone:
            raise self.SpectrumFitterException()
        return self._model.GetFunction().Integral(x, 10000)
   
    def CalculateNormalisedIntegralAbove(self, x):
        """
        Calculate per-event yield above a certain pt, done as sum in 1 GeV bins of the 
        binned content from a min. pt to a max. pt.
        """
        if not self._fitDone:
            raise self.SpectrumFitterException()
        maxint = 1000.
        ptstart = x
        yieldval = 0
        while ptstart < maxint:
            yieldval += self._model.GetFunction().Integral(ptstart, ptstart+10)/10.
            ptstart += 10
        return yieldval
            
    def MakeBinnedParameterisation(self, nbins, xmin, xmax, normBinWidth = False):
        """
        Make binned parameterisation. If normBinWith is set to True, the integral is 
        normalised by the bin width
        """
        result = TH1F("binned%s" %(self._name), "", nbins, xmin, xmax)
        for mybin in range(2, result.GetXaxis().GetNbins()+1):
            value = 0
            if normBinWidth:
                value = self.CalculateBinMean(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin))
            else:
                value = self.CalculateIntegral(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin))
            #print "min %f, max %f, value %e" %(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin), value)
            result.SetBinContent(mybin, value)
        return result
    
    def MakeBinnedParameterisationDefault(self, normBinWidth = False):
        """
        Make binned parameterisation. If normBinWith is set to True, the integral is 
        normalised by the bin width
        """
        result = TH1F("binned%s" %(self._name), "", self._data.GetXaxis().GetNbins(), self._data.GetXaxis().GetXbins().GetArray())
        for mybin in range(2, result.GetXaxis().GetNbins()+1):
            value = 0
            if normBinWidth:
                value = self.CalculateBinMean(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin))
            else:
                value = self.CalculateIntegral(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin))
            #print "min %f, max %f, value %e" %(result.GetXaxis().GetBinLowEdge(mybin),result.GetXaxis().GetBinUpEdge(mybin), value)
            result.SetBinContent(mybin, value)
            result.SetBinError(mybin, 0)
        return result
            
    def CalculateIntegral(self, xmin, xmax):
        if not self._fitDone:
            raise self.SpectrumFitterException()
        return self._model.GetFunction().Integral(xmin, xmax)
    
    def CalculateBinMean(self, xmin, xmax):
        if not self._fitDone:
            raise self.SpectrumFitterException()
        return self._model.GetFunction().Integral(xmin, xmax)/(xmax - xmin)
                
    def GetFitFunction(self):
        return self._model.GetFunction()
    
    def GetData(self):
        return self._data
    
    
class ConstrainedSpectrumFitter(SpectrumFitter):
    
    class ConstrainParameter(object):
        
        def __init__(self, parIDconstrain, parIDfull):
            self.__parIDconstrain = parIDconstrain
            self.__parIDfull = parIDfull
            
        def GetParIDConstrain(self):
            return self.__parIDconstrain
        
        def GetParIDFull(self):
            return self.__parIDfull
        
        def SetParIDConstrain(self, parid):
            self.__parIDconstrain = parid
            
        def SetParIDFull(self, parid):
            self.__parIDfull = parid
    
    def __init__(self, name, spectrum, fullmodel, constrainmodel):
        SpectrumFitter.__init__(self, name, spectrum, fullmodel)
        self.__constrainmodel = constrainmodel
        self.__constrainrange = {"min":0, "max":100}
        self.__constrainparameters = []
    
    def SetConstrainFitrange(self, xmin, xmax):
        self.__constrainrange["min"] = xmin
        self.__constrainrange["max"] = xmax
    
    def SetConstrainParameter(self, paridConstrain, parIdFull):
        self.__constrainparameters.append(self.ConstrainParameter(paridConstrain, parIdFull))
    
    def DoConstrain(self):
        constrainfitter = SpectrumFitter("constrainfitter", self._data, self.__constrainmodel)
        constrainfitter.DoFit(self.__constrainrange["min"], self.__constrainrange["max"])
        # fix  parameters
        for param in self.__constrainparameters:
            print "Constraining parameter %d from parameter %d in constrain model" %(param.GetParIDFull(), param.GetParIDConstrain())
            self._model.FixParameter(param.GetParIDFull(), self.__constrainmodel.GetParValue(param.GetParIDConstrain()))
        
class MinBiasFitter(SpectrumFitter):
    
    def __init__(self, name, data, fitmin = 15., model = None):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(fitmin, 50.)
        
class TriggeredSpectrumFitter(SpectrumFitter):
    
    def __init__(self, name, data, model = None):
        SpectrumFitter.__init__(self, name, data)
        self.DoFit(50., 90.)

        