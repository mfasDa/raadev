'''
Created on 22.09.2014

@author: markusfasel
'''

from base.FileHandler import LegoTrainFileReader
from base.SpectrumContainer import SpectrumContainer
from test.PlotScaledTriggered import PlotScaledTriggeredToMinBias

def MakeNormalisedSpectrum(container):
    inputcontainer = container.FindTrackContainer("tracksAll")
    try:
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return inputcontainer.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def Draw(filename, trigger):
    reader = LegoTrainFileReader(filename)
    content = reader.ReadFile()
    content.SetName("RawSpectra")
    minbiasspectrum = MakeNormalisedSpectrum(content.GetData("MinBias"))
    triggeredspectrum = MakeNormalisedSpectrum(content.GetData(trigger))
    plot = PlotScaledTriggeredToMinBias(minbiasspectrum, triggeredspectrum)
    plot.Create()
    plot.SetLabel("Trigger: %s" %(trigger))
    return plot