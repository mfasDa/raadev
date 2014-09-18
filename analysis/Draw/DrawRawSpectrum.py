#! /usr/bin/env python
from ROOT import kRed
from base.Graphics import Frame, GraphicsObject, SinglePanelPlot, Style
from base.SpectrumContainer import SpectrumContainer
from base.FileHandler import LegoTrainFileReader
import sys

gObjects = []

class RawSpectrumPlot(SinglePanelPlot):
    
    def __init__(self, spectrum):
        SinglePanelPlot.__init__(self)
        
    def Create(self, spectrum, trigger):
        canvas = self._OpenCanvas("plot", "Plot")
        canvas.SetLogx(True)
        canvas.SetLogy(True)
        pad = self._GetFramedPad()
        frame = Frame("rawframe", 0, 100, 1e-10, 100)
        frame.SetXtitle("p_{#rm{t}} (GeV/c)")
        frame.SetYtitle("1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")
        pad.DrawFrame(frame)
        pad.DrawGraphicsObject(GraphicsObject(spectrum, Style(kRed, 24)))
        pad.DrawLabel(0.65, 0.77, 0.89, 0.85, "Trigger: %s" %(trigger))

def MakeNormalisedSpectrum(inputcontainer):
    try:
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return inputcontainer.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")


def CreatePlot(filename, trigger, saveCanvas = False):
    reader = LegoTrainFileReader(filename)
    data = reader.ReadData().GetData(trigger)
    spectrum = MakeNormalisedSpectrum(data.FindTrackContainer("tracksAll"))
    
    plot = RawSpectrumPlot()
    plot.Create(spectrum, trigger)    
    if(saveCanvas):
        plot.SaveAs("rawSpectrum%s.png" %(trigger))
    return plot

def main(): 
    filename = sys.argv[1]
    trigger = sys.argv[2]
    CreatePlot(filename, trigger, True)
    
if __name__ == "__main__":
    main()