#! /usr/bin/env python
from ROOT import TFile,TCanvas,TH1F,TPaveText,kRed,gROOT
from Helper import FileReaderException, HistNotFoundException
from SpectrumContainer import DataContainer, SpectrumContainer
import sys

gObjects = []

def ReadSpectrum(filename, trigger):
    inputfile = TFile.Open(filename)
    if not inputfile or inputfile.IsZombie():
        raise FileReaderException(filename)
    rlist = inputfile.Get("results")
    if not rlist:
        raise FileReaderException("%s#results" %(filename))
    hlist = rlist.FindObject("histosPtEMCalTriggerHistograms")
    if not hlist:
        raise FileReaderException("%s#results/histosPtEMCalTriggerHistograms" %(filename))
    htrack = hlist.FindObject("hTrackHist%s" %(trigger))
    hevent = hlist.FindObject("hEventHist%s" %(trigger))
    hevent.SetDirectory(gROOT)
    if not htrack:
        raise HistNotFoundException("hTrackHist%s" %(trigger))
    if not hevent:
        raise HistNotFoundException("hEventHist%s" %(trigger))
    return DataContainer(eventHist=hevent, trackHist=htrack)

def CreatePlot(filename, trigger, saveCanvas = False):
    try:
        spectrumContainer = ReadSpectrum(filename, trigger)
    except FileReaderException as e:
        print str(e)
        sys.exit(1)
    except HistNotFoundException as e:
        print str(e)
        sys.exit(1)
    try:
        spectrumContainer.SetVertexRange(-10., 10.)
        spectrumContainer.SetPileupRejection(True)
        spectrumContainer.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    normalisedSpectrum = spectrumContainer.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

    plot = TCanvas("plot", "Plot", 800, 800)
    plot.cd()
    plot.SetLogx(True)
    plot.SetLogy(True)
    plot.SetGrid(False,False)
    
    normalisedSpectrum.SetTitle("")
    normalisedSpectrum.SetStats(False)
    normalisedSpectrum.GetYaxis().SetRangeUser(1e-10, 100)
    normalisedSpectrum.SetMarkerColor(kRed)
    normalisedSpectrum.SetLineColor(kRed)
    normalisedSpectrum.SetMarkerStyle(24)
    normalisedSpectrum.Draw("ep")
    gObjects.append(normalisedSpectrum)
    
    label = TPaveText(0.65, 0.77, 0.89, 0.85, "NDC")
    label.SetBorderSize(0)
    label.SetFillStyle(0)
    label.SetTextFont(42)
    label.SetTextSize(0.045)
    label.AddText("Trigger: %s" %(trigger))
    label.Draw()
    gObjects.append(label)
    gObjects.append(plot)
    
    if(saveCanvas):
        plot.SaveAs("rawSpectrum%s.png" %(trigger))

def main(): 
    filename = sys.argv[1]
    trigger = sys.argv[2]
    CreatePlot(filename, trigger, True)
    
if __name__ == "__main__":
    main()