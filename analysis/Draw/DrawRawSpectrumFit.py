'''
Created on 18.09.2014

@author: markusfasel
'''

from base.ResultDataBuilder import ResultDataBuilder

from plots.RawDataFittingPlot import RawDataFittingPlot

def MakeNormalisedRawSpectrum(data):
    data.SetVertexRange(-10., 10.)
    data.SetPileupRejection(True)
    data.SelectTrackCuts(1)
    return data.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def DrawRawSpectrumIntegral(filename, trigger = "MinBias"):
    reader = ResultDataBuilder("lego", filename)
    content = reader.ReadFile()
    isMinBias = (trigger == "MinBias")
    
    plot = RawDataFittingPlot(MakeNormalisedRawSpectrum(content.GetData(trigger).FindTrackContainer("tracksAll")), isMinBias)
    plot.Create()
    return plot
