#! /usr/bin/env python
"""
GetRawCount.py
 Created on: 28.08.2014
     Author: markusfasel
"""

from Helper import ReadHistList
from SpectrumContainer import DataContainer

from ROOT import TCanvas

def ReadSpectra(filename):
    """
    Read the spectra for different trigger classes from the root file
    Returns a dictionary of triggers - spectrum container
    """
    triggers = ["MinBias", "EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    hlist = ReadHistList(filename, "PtEMCalTriggerTask")
    result = {}
    for trg in triggers:
        result[trg] = DataContainer(eventHist = hlist.FindObject("hEventHist%s" %(trg)), trackHist = hlist.FindObject("hTrackHist%s" %(trg)))
    return result

def CountTracks(data, ptmin, ptmax):
    binmin = data.GetXaxis().FindBin(ptmin)
    binmax = data.GetXaxis().FindBin(ptmax)
    trackCount = 0
    for bin in range(binmin, binmax + 1):
        trackCount = trackCount + data.GetBinContent(bin)
    return trackCount


def MakeRawSpectrum(inputdata, name):
    """
    Normalise spectrum by the number of events and by the bin width
    """
    inputdata.SetVertexRange(-10., 10.)
    inputdata.SetPileupRejection(True)
    inputdata.SelectTrackCuts(1)
    return inputdata.MakeProjection(0, "ptSpectrum%s" %(name), "p_{t} (GeV/c)", "1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})", doNorm = False)

def Run():
    spectra = ReadSpectra("AnalysisResults.root")
    results = []
    canvas = TCanvas("spectra", "Spectra", 1000, 800)
    canvas.Divide(3,2)
    counter =1
    for trigger in sorted(spectra.keys()):
        rawspectrum = MakeRawSpectrum(spectra[trigger], trigger)
        print "%s: 50 - G0 GeV/c: %d, 80 - 100 GeV/c: %d" %(trigger, CountTracks(rawspectrum, 51, 59), CountTracks(rawspectrum, 82, 100))
        canvas.cd(counter)
        rawspectrum.Draw("ep")
        results.append(rawspectrum)
        counter = counter + 1
    results.append(canvas)
    return results