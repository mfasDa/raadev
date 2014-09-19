'''
Created on 19.09.2014

@author: markusfasel
'''

from base.FileHandler import LegoTrainFileReader
from base.SpectrumContainer import SpectrumContainer
from test.IntegralRangePlot import IntegralRangePlot

def MakeNormalisedSpectrum(container):
    inputcontainer = container.FindTrackContainer("tracksAll")
    try:
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return inputcontainer.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def Draw(filename, intmin = 30):
    reader = LegoTrainFileReader(filename)
    plot = IntegralRangePlot(MakeNormalisedSpectrum(reader.ReadFile().GetData("MinBias")))
    plot.Create(intmin)
    return plot