'''
Created on 19.09.2014

@author: markusfasel
'''

from base.FileHandler import LegoTrainFileReader
from plots.RawspectrumPeriodComparisonPlot import RawspectrumPeriodComparisonPlot
from base.Graphics import Style
from ROOT import kRed, kBlack, kBlue, kGreen, kMagenta, kOrange, kYellow, kTeal

def MakeNormalisedRawSpectrum(data):
    pass

def GetRawSpectrum(filename, trigger):
    reader = LegoTrainFileReader(filename)
    return MakeNormalisedRawSpectrum(reader.ReadFile().GetData(trigger).FindTrackContainer("tracksAll")) 

def DrawPeriodComparison(reference, periods, trigger):
    styles = [Style(kRed, 24), Style(kBlue, 25), Style(kGreen, 26), Style(kMagenta, 27), Style(kOrange, 28), Style(kYellow, 29), Style(kTeal, 30)]
    plot = RawspectrumPeriodComparisonPlot()
    plot.AddRawSpectrum(reference["period"], GetRawSpectrum(reference["file"], trigger), Style(kBlack, 20), True)
    counter = 0
    for period in periods:
        plot.AddRawSpectrum(period["period"], GetRawSpectrum(period["file"]), styles[counter], False)
        counter += 1
    plot.AddLabel("Trigger: %s" %(trigger))
    plot.Create()
    return plot