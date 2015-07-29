#! /usr/mybin/env python

from ROOT import kRed, kBlue, kOrange, kGreen
from base.Graphics import Style
from base.FileHandler import LegoTrainFileReader
from util.TriggerTurnonCurve import TriggerTurnonCurve
from plots.TriggerTurnonPlot import TriggerTurnonPlot

def MakeNormalisedSpectrum(inputdata, name):
    """
    Normalise spectrum by the number of events and by the bin width
    """
    inputdata.SetVertexRange(-10., 10.)
    inputdata.SetPileupRejection(True)
    inputdata.SelectTrackCuts(1)
    return inputdata.MakeProjection(0, "ptSpectrum%s" %(name), "p_{t} (GeV/c)", "1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})")

def ReadData(filename):
    reader = LegoTrainFileReader(filename)
    return reader.ReadFile()

def CreateTurnonPlot(filename, filenameMB, fitminval = 15., requireCluster = False):
    trackHistName = "tracksAll"
    if requireCluster:
        trackHistName = "tracksWithClusters"
    data = ReadData(filename)
    dataMB = ReadData(filenameMB)
    styles = {"EMCJHigh" : Style(kRed, 24), "EMCJLow" : Style(kOrange, 26), "EMCGHigh" : Style(kBlue, 25), "EMCGLow" : Style(kGreen, 27)}
    plot = TriggerTurnonPlot()
    minbiasspectrum = MakeNormalisedSpectrum(dataMB.GetData("MinBias").FindTrackContainer(trackHistName),"MinBias") 
    for trg in styles.keys():
        plot.AddData(trg, TriggerTurnonCurve(trg, MakeNormalisedSpectrum(data.GetData(trg).FindTrackContainer(trackHistName), trg), minbiasspectrum, fitminval), styles[trg])  
    plot.Create()
    return plot

