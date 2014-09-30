"""
Created on 29.09.2014

Comparison plot for spectra in different pt-hat bins

@author: markusfasel
"""

from base.Graphics import SinglePanelPlot, Style, GraphicsObject, Frame
from base.SpectraSum import SpectraSum
from ROOT import kBlack

class MCSpectrumPtHatBin:
    """
    Entry class of a spectrum for a given pt-hat bin
    """
    
    def __init__(self, pthatbin, spectrum, style = None):
        """
        Constructor
        """
        self.__pthatbin = pthatbin
        self.__spectrum = spectrum
        self.__style = None
        if style:
            self.__style = style
        else:
            self.__style = Style(kBlack, 20)
    
    def GetPtHatBin(self):
        """
        Access to value of the pt-hat bin
        """
        return self.__pthatbin
    
    def GetSpectrum(self):
        """
        Access to spectrum
        """
        return self.__spectrum
    
    def Set(self, pthatbin, spectrum):
        """
        Set the values for pt-hat bin and spectrum
        """
        self.__pthatbin = pthatbin
        self.__spectrum = spectrum
        
    def SetStyle(self, style):
        """
        Change style of the spectrum
        """
        self.__style = style
        
    def DrawSpectrum(self, pad, addToLegend = True):
        """
        Draw spectrum as graphics object into a pad
        """
        pad.DrawGraphicsObject(GraphicsObject(self.__spectrum, self.__style), addToLegend, "Pt-hat bin %d" %(self.__pthatbin))
        
    def __cmp__(self, other):
        """
        Sort spectra according to pt hat bins
        """
        ownvalue = self.__pthatbin
        othervalue = 0
        if type(other) is int:
            othervalue = int(other)
        elif type(other) is MCSpectrumPtHatBin:
            othervalue = other.GetPtHatBin()
        else:
            return -1
        if ownvalue < othervalue:
            return -1
        if ownvalue > othervalue:
            return 1
        return 0
    
class MCSpectrumContainer:
    """
    Container class for spectra in different pt-hat bins
    """
    
    def __init__(self):
        """
        Constructor, initialising list of bins
        """
        self.__spectra = []
    
    def AddPtHatBin(self, pthatbin, spectrum, style = None):
        """
        Add new pt-hat bin to the container
        """
        self.__spectra.append(MCSpectrumPtHatBin(pthatbin, spectrum, style))
        
    def GetSpectraSum(self):
        """
        sum up the spectra in different pt-hard bins
        """
        summer = SpectraSum("binsSummed")
        for pthatbin in self.__spectra:
            summer.AddSpectrum(pthatbin.GetSpectrum())
        return summer.GetSummedSpectrum()
        
    def FindSpectrum(self, pthatbin):
        """
        Find spectrum inside the container
        """
        if not pthatbin in self.__spectra:
            return None
        return self.__spectra[self.__spectra.index(pthatbin)]
        
    def SetBinStyle(self, pthatbin, style):
        """
        Change style of the spectrum for a given bin
        """
        spectrum = self.FindSpectrum(pthatbin)
        if spectrum:
            spectrum.SetStyle(style)
            
    def DrawSpectra(self, pad, addtolegend = True):
        """
        Draw all spectra inside the container into a given pad
        """
        for entry in sorted(self.__spectra):
            entry.DrawSpectrum(pad, addtolegend)
        # draw also sum of the different bins
        pad.DrawGraphicsObject(GraphicsObject(self.GetSpectraSum(), Style(kBlack, 20)), addtolegend, "Sum")
    
class MCTruthSpectrumPlot(SinglePanelPlot):
    """
    Comparison plot of spectra for different pt-hat bins
    """

    def __init__(self):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__spectrumContainer = MCSpectrumContainer()
        self.__labeltext = "MC-true spectrum"
        
    def SetLabelText(self, text):
        """
        Change text of the label
        """
        self.__labeltext = text
        
    def AddMCSpectrum(self, pthatbin, spectrum, style = None):
        """
        Add new spectrum in pt-hat bin to the plot
        """
        self.__spectrumContainer.AddPtHatBin(pthatbin, spectrum, style)
        
    def Create(self):
        """
        Create the plot
        """
        self._OpenCanvas("MCtruthPlot", "Plot of MC-true spectra")
        pad = self._GetFramedPad()
        pad.GetPad().SetLogx(True)
        pad.GetPad().SetLogy(True)
        frame = Frame("sframe", 0., 100., 1e-10, 100.)
        frame.SetXtitle("p_{t} (GeV)/c")
        frame.SetYtitle("d#sigma/dp_{t} (mb/(GeV/c))" )
        pad.DrawFrame(frame)
        self.__spectrumContainer.DrawSpectra(pad, True)
        pad.CreateLegend(0.5, 0.5, 0.89, 0.89)
        pad.DrawLabel(0.15, 0.15, 0.45, 0.21, self.__labeltext)
    
    
class MCWeightPlot(SinglePanelPlot):
    """
    Class for the plot of the weights for different pt-hard bins
    """
    
    def __init__(self, weights):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__points = weights
        
    def Create(self):
        """
        Creator function for the plot
        """
        self._OpenCanvas("weightplot", "Monte-Carlo weights")
        pad = self._GetFramedPad()
        pad.GetPad().SetLogy()
        frame = Frame("wframe", 0., 11., 1e-12, 1e-5)
        frame.SetXtitle("p_{t,hard} bin")
        frame.SetYtitle("weight factor")
        pad.DrawFrame(frame)
        pad.DrawGraphicsObject(GraphicsObject(self.__points.GetWeightingCurve(), Style(kBlack, 20)), False, "weights")