'''
Created on 19.09.2014

@author: markusfasel
'''

from base.FileHandler import ResultDataBuilder
from base.struct.DataContainers import SpectrumContainer
from plots.RawspectrumPeriodComparisonPlot import RawspectrumPeriodComparisonPlot
from base.Graphics import Style
from ROOT import kRed, kBlack, kBlue, kGreen, kMagenta, kOrange, kYellow, kTeal

def MakeNormalisedRawSpectrum(data):
    try:
        data.SetVertexRange(-10., 10.)
        data.SetPileupRejection(True)
        data.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return data.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def GetRawSpectrum(filename, trigger):
    reader = ResultDataBuilder("lego", filename)
    return MakeNormalisedRawSpectrum(reader.GetResults().GetData(trigger).FindTrackContainer("tracksAll")) 

def DrawPeriodComparison(reference, periods, trigger):
    styles = [Style(kRed, 24), Style(kBlue, 25), Style(kGreen, 26), Style(kMagenta, 27), Style(kOrange, 28), Style(kYellow, 29), Style(kTeal, 30)]
    plot = RawspectrumPeriodComparisonPlot()
    plot.AddRawSpectrum(reference["period"], GetRawSpectrum(reference["file"], trigger), Style(kBlack, 20), True)
    counter = 0
    for period in periods:
        plot.AddRawSpectrum(period["period"], GetRawSpectrum(period["file"], trigger), styles[counter], False)
        counter += 1
    plot.AddLabel("Trigger: %s" %(trigger))
    plot.Create()
    return plot