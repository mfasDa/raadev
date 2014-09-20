'''
Created on 18.09.2014

@author: markusfasel
'''

from base.Graphics import SinglePanelPlot, Frame, GraphicsObject, Style
from base.SpectrumFitter import MinBiasFitter, TriggeredSpectrumFitter
from base.DataCollection import DataCollection, Datapoint
from ROOT import kRed, kBlue, kGreen

class RawDataIntegralPlot(SinglePanelPlot):
    """
    Plot checking the raw spectrum and the integral calculated
    """
    
    class RawData:
        """
        Container class for the data to be plotted
        """
        
        def __init__(self, rawspectrum, isMinBias = True):
            """
            Constructor
            """
            self.__rawspectrum = rawspectrum
            self.__mbfitter = None
            if isMinBias:
                self.__mbfitter = MinBiasFitter("MinBiasFitter", self.__rawspectrum)
            else:
                self.__mbfitter = TriggeredSpectrumFitter("TriggeredFitter", self.__rawspectrum)
            self.__datafitted = DataCollection("MinBiasFitted")
        
        def MakeRawSpectrum(self):
            """
            Access to the raw spectrum itself
            """
            return GraphicsObject(self.__rawspectrum, Style(kRed, 24))
        
        def MakeFitted(self):
            for mybin in range(1, self.__rawspectrum.GetXaxis().GetNbins()+1):
                xmin = self.__rawspectrum.GetXaxis().GetBinLowEdge(mybin)
                xmax = self.__rawspectrum.GetXaxis().GetBinUpEdge(mybin)
                self.__datafitted.AddDataPoint(Datapoint(self.__rawspectrum.GetXaxis().GetBinCenter(mybin), self.__mbfitter.CalculateBinned(xmin, xmax),self.__rawspectrum.GetXaxis().GetBinWidth(mybin)/2.))
            return GraphicsObject(self.__datafitted.MakeLimitCurve(None, direction="central"), Style(kGreen, 27))
    
        def MakeAntiderivativeNormalised(self):
            """
            Access to the antiderivative function
            """
            # return GraphicsObject(self.__mbfitter.GetNormalisedAntiDerivative(), Style(kBlue, 25))
            return GraphicsObject(self.__mbfitter.GetAntiderivative(), Style(kBlue, 25))

    def __init__(self, rawspectrum, isMinBias):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__rawspectrum = self.RawData(rawspectrum, isMinBias)
        
    def Create(self):
        """
        Create the figure
        """
        self._OpenCanvas("RawSpectrumIntegral", "Raw Spectrum integral plot")
        pad = self._GetFramedPad()
        pad.GetPad().SetLogx(True)
        pad.GetPad().SetLogy(True)
        frame = Frame("frame", 0., 100., 1e-10, 1000)
        frame.SetXtitle("p_{t} (GeV/C)")
        frame.SetYtitle("1/N_{event} dN/dp_{t} ((GeV/c)^{-1})")
        pad.DrawFrame(frame)
        pad.DrawGraphicsObject(self.__rawspectrum.MakeRawSpectrum(), True, "Raw spectrum")
        pad.DrawGraphicsObject(self.__rawspectrum.MakeFitted(), True, "Fit to raw spectrum")
        #pad.DrawGraphicsObject(self.__rawspectrum.MakeAntiderivativeNormalised(), True, "Integral to infinity")
        pad.CreateLegend(0.5, 0.75, 0.89, 0.89)
        