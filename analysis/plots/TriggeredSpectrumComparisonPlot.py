'''
Created on 02.10.2014

@author: markusfasel
'''

from base.ComparisonData import ComparisonData,ComparisonObject,ComparisonPlot
from base.Graphics import Frame

class PtSpectrumFrame(Frame):
    
    def __init__(self):
        Frame.__init__(self, "ptframe", 0., 100., 1e-10, 100)
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle("1/N_{event} dN/dp_{t} ((GeV/c)^{-1})")
    
class EnergySpectrumFrame(Frame):
    
    def __init__(self):
        Frame.__init__(self, "ptframe", 0., 100., 1e-10, 100)
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle("1/N_{event} dN/dp_{t} ((GeV/c)^{-1})")
    
class SpectraComparisonObject(ComparisonObject):
    
    def __init__(self, trigger, data, style):
        ComparisonObject.__init__(self, data, style)
        self.__triggername =  trigger
        
    def GetLegendTitle(self):
        return self.__triggername
    
    def GetObjectName(self):
        return "Rawspectrum%s" %(self.__triggername)

class TriggeredSpectrumComparisonPlot(ComparisonPlot):
    """
    Comparing raw spectra of different classes
    """

    def __init__(self, frame, canvasname = "spectrumcomparison"):
        """
        Constructor
        """
        ComparisonPlot.__init__(self)
        self._comparisonContainer = ComparisonData()
        self.SetFrame(frame)
        self.SetLegendAttributes(0.5, 0.65, 0.89, 0.89)
        self.SetPadAttributes(True, True, False, False)
        self.__canvasname = canvasname
        
    def AddSpectrum(self, trigger, spectrum, style):
        self._comparisonContainer.AddEntry(SpectraComparisonObject(trigger, spectrum, style))
        
    def Create(self):
        self._Create(self.__canvasname, "Spectrum Comparison")
        
class PtTriggeredSpectrumComparisonPlot(TriggeredSpectrumComparisonPlot):
    
    def __init__(self, canvasname):
        TriggeredSpectrumComparisonPlot.__init__(self, PtSpectrumFrame(), canvasname)
        
class EnergyTriggeredSpectrumComparisonPlot(TriggeredSpectrumComparisonPlot):
    
    def __init__(self, canvasname):
        TriggeredSpectrumComparisonPlot.__init__(self, EnergySpectrumFrame(), canvasname)
        