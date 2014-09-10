#! /usr/bin/env python
"""
GetRawCount.py
 Created on: 28.08.2014
     Author: markusfasel
"""

from base.FileHandler import LegoTrainFileReader

from ROOT import TCanvas

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
    fhandler = LegoTrainFileReader("AnalysisResults.root")
    filecontent = fhandler.ReadFile()
    canvas = TCanvas("spectra", "Spectra", 1000, 800)
    canvas.Divide(3,2)
    counter =1
    results = []
    mainclasses = ["EMCGHigh", "EMCGLow", "EMCJHigh", "EMCJLow", "MinBias"]
    for trigger in sorted(filecontent.GetListOfTriggers()):
        rawspectrum = MakeRawSpectrum(filecontent.GetData(trigger).FindTrackContainer("tracksAll"), trigger)
        print "%s: 50 - G0 GeV/c: %d, 80 - 100 GeV/c: %d" %(trigger, CountTracks(rawspectrum, 51, 59), CountTracks(rawspectrum, 82, 100))
        if trigger in mainclasses:
            canvas.cd(counter)
            rawspectrum.Draw("ep")
            results.append(rawspectrum)
            counter = counter + 1
    results.append(canvas)
    return results

if __name__ == "__main__":
    Run()