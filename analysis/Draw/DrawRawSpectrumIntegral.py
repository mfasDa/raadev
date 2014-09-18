'''
Created on 18.09.2014

@author: markusfasel
'''

from base.FileHandler import LegoTrainFileReader
from base.SpectrumContainer import SpectrumContainer
from plots.RawDataIntegralPlot import RawDataIntegralPlot

def MakeNormalisedRawSpectrum(data):
    try:
        data.SetVertexRange(-10., 10.)
        data.SetPileupRejection(True)
        data.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return data.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def DrawRawSpectrumIntegral(filename):
    reader = LegoTrainFileReader(filename)
    content = reader.ReadFile()
    
    plot = RawDataIntegralPlot(MakeNormalisedRawSpectrum(content.GetData("MinBias").FindTrackContainer("tracksAll")))
    plot.Create()
    return plot