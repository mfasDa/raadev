'''
Created on 18.09.2014

@author: markusfasel
'''

from base.SpectrumFitter import MinBiasFitter
from base.Graphics import GraphicsObject
from base.DataCollection import DataCollection, Datapoint

class TriggerTurnonCurve:
    
    def __init__(self, name, emcaldata, minbiasdata, fitmin = 15):
        self.__name = name
        self.__mbfitter = MinBiasFitter("mbfitter", minbiasdata)
        self.__values = self.__Create(emcaldata)
        
    def __Create(self, emcaldata):
        result = DataCollection("turnonCurve%s" %(self.__name));
        for mybin in range(1, emcaldata.GetXaxis().GetNbins()+1):
            minval = emcaldata.GetXaxis().GetBinLowEdge(mybin)
            if minval < 15:
                continue
            maxval = emcaldata.GetXaxis().GetBinUpEdge(mybin)
            binnedMb = self.__mbfitter.CalculateBinned(minval, maxval)
            statError = emcaldata.GetBinError(mybin)/binnedMb
            datapoint = Datapoint(emcaldata.GetXaxis().GetBinCenter(mybin), emcaldata.GetBinContent(mybin)/binnedMb, emcaldata.GetXaxis().GetBinWidth(mybin)/2.)
            datapoint.AddErrorSource("stat", statError, statError)
        return result;
    
    def GetPoints(self):
        return self.__values.MakeErrorGraphForSource("stat")
    
    def GetName(self):
        return self.__name
    
    def MakeGraphicsObject(self, style):
        return GraphicsObject(self.GetPoints(), style)
         
    def WriteData(self, name):
        self.GetPoints().Write("turnonCurve%s" %(name))
