#! /usr/bin/env python

from ROOT import TFile, TH1F, TCanvas, gPad, kBlack, kRed, kBlue, kGreen, kMagenta
from Helper import FileReaderException, HistNotFoundException, Style
from SpectrumContainer import SpectrumContainer
import sys

gObjects = []

class TriggerCorrelation:
    def __init__(self, mainclass):
        self.__mainclass = mainclass
        self.__nevents = 0
        self.__otherclasses = {}
        
    def SetMainNumberOfEvents(self, nevents):
        self.__nevents = nevents
        
    def AddTrigger(self, triggername, nevents):
        self.__otherclasses[triggername] = nevents
        
    def CreateHistogram(self, style):
        result = TH1F("%hcorrTrigger%s" %(self.__mainclass), "Number of events with trigger where %s is fired" %(self.__mainclass), 5, -0.5, 4.5)
        result.GetXaxis().SetBinLabel(1, self.__mainclass)
        result.SetBinContent(1, self.__nevents)
        counter = 0
        for icls in self.__otherclasses.keys():
            result.GetXaxis().SetBinLabel(counter + 1, icls)
            result.SetBinContent(counter + 1, self.__otherclasses[icls])
            counter = counter + 1
        result.GetXaxis().SetTitle("Trigger Class")
        result.GetYaxis().SetTitle("Number of events")
        result.SetLineColor(style.GetColor())
        return result

def ReadHistogram(filename):
    inputfile = TFile.Open(filename)
    if not inputfile or inputfile.IsZombie():
        raise FileReaderException(filename)
    rlist = inputfile.Get("results")
    hlist = rlist.FindObject("histosPtEMCalTriggerHistograms")
    triggerhist = hlist.FindObject("hEventTrigger")
    if not triggerhist:
        raise HistNotFoundException(triggerhist)
    return triggerhist
    
def CorrelateToTrigger(data, mainclass):
    trgclasses = ["MinBias", "EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    result = TriggerCorrelation(mainclass)
    dataCont = SpectrumContainer(data)
    axisMain = dataCont.GetDimension(mainclass)
    # get the number of events
    proj = dataCont.ProjectToDimension(axisMain, "h%s" %(mainclass))
    result.SetMainNumberOfEvents(proj.GetBinContent(2))
    for cls in trgclasses:
        if cls == mainclass:
            continue
        axiscls = dataCont.GetDimension(cls)
        proj = dataCont.ProjectToDimension(axiscls, "h%s" %(cls))
        result.AddTrigger(cls, proj.GetBinContent(2))
    return result

def MakeCorrelationPlot(filename, savePlot = False):
    colors = [kBlack, kRed, kBlue, kGreen, kMagenta]
    trgclasses = ["MinBias", "EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    data = ReadHistogram(filename)
    result = TCanvas("trgcorr", "Correlation between trigger classes", 1000, 700)
    result.Divide(3,2)
    counter = 1
    for cls in range(0, len(trgclasses)):
        corr = CorrelateToTrigger(data, trgclasses[cls])
        hist = corr.CreateHistogram(Style(colors[cls], 20))
        result.cd(counter)
        gPad.SetGrid(False,False)
        hist.Draw("box")
        gObjects.append(hist)
    result.cd()
    gObjects.append(result)
    if savePlot:
        result.SaveAs("triggerCorrelation.png")
    
def main():
    filename = sys.argv[1]
    MakeCorrelationPlot(filename, True)

if __name__ == "__main__":
    main()