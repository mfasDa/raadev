#! /usr/bin/env python

from ROOT import TCanvas,TF1,TGraphErrors,TLegend,TMath
from ROOT import kRed, kBlue, kOrange, kGreen
from Helper import ReadHistList,Frame, Style
from SpectrumContainer import DataContainer

class TriggerTurnonCurve:
    
    def __init__(self, name, emcaldata, minbiasdata):
        self.__values = self.__Create(emcaldata, minbiasdata)
        self.__name = name
        
    def __Create(self, emcaldata, mbparam):
        result = TGraphErrors();
        npoints = 0;
        for bin in range(1, emcaldata.GetXaxis().GetNbins()+1):
            min = emcaldata.GetXaxis().GetBinLowEdge(bin)
            if min < 15:
                continue
            max = emcaldata.GetXaxis().GetBinUpEdge(bin)
            binnedMb = self.__GetBinnedParameterisation(mbparam, min, max)
            result.SetPoint(npoints, emcaldata.GetXaxis().GetBinCenter(bin), emcaldata.GetBinContent(bin)/binnedMb)
            result.SetPointError(npoints, emcaldata.GetXaxis().GetBinWidth(bin)/2., emcaldata.GetBinError(bin)/binnedMb)
            npoints = npoints + 1
        return result;
    
    def GetPoints(self):
        return self.__values
    
    def GetName(self):
        return self.__name
 
    def Draw(self,style):
        self.__values.SetMarkerColor(style.GetColor())
        self.__values.SetMarkerStyle(style.GetMarker())
        self.__values.SetLineColor(style.GetColor())
        self.__values.Draw("epsame")
    
    def __GetBinnedParameterisation(self, mbparam, min, max):
        return mbparam.Integral(min, max)/TMath.Abs(max - min)
    
class TriggerTurnonPlot:
    
    def __init__(self, data):
        self.__data = data
        self.__canvas = None
        self.__Frame = None
        self.__legend = None
        
    def Create(self):
        self.__canvas = TCanvas("EMCalTurnon", "EMCal Turn-on curve", 800, 600)
        topad = self.__canvas.cd()
        topad.SetGrid(False, False)
        self.__Frame = Frame("emcturnon", 0., 100., 0., 3000.)
        self.__Frame.SetXtitle("p_{t} (GeV/c)")
        self.__Frame.SetYtitle("EMCal/MinBias")
        self.__Frame.Draw()
        styles = {"EMCJHigh" : Style(kRed, 24), "EMCJLow" : Style(kOrange, 26), "EMCGHigh" : Style(kBlue, 25), "EMCGLow" : Style(kGreen, 27)}
        self.__legend = TLegend(0.55, 0.75, 0.89, 0.89)
        self.__legend.SetBorderSize(0)
        self.__legend.SetFillStyle(0)
        self.__legend.SetTextFont(42)
        for trg in self.__data.keys():
            self.__data[trg].Draw(styles[trg])
            self.__legend.AddEntry(self.__data[trg].GetPoints(), self.__data[trg].GetName(), "lep")
        self.__legend.Draw()
            
    def SaveAs(self, filenamebase):
        """
        Save plot as image file
        """
        types = ["eps", "pdf", "jpeg", "gif", "png"]
        for t in types:
            self.__canvas.SaveAs("%s.%s" %(filenamebase, t))
        
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

def MakeNormalisedSpectrum(inputdata, name):
    """
    Normalise spectrum by the number of events and by the bin width
    """
    inputdata.SetVertexRange(-10., 10.)
    inputdata.SetPileupRejection(True)
    inputdata.SelectTrackCuts(1)
    return inputdata.MakeProjection(0, "ptSpectrum%s" %(name), "p_{t} (GeV/c)", "1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})")

def ParameteriseMinBiasSpectrum(spectrum):
    """
    Parameterise fit function by power law
    """
    fitfunction = TF1("fitfunction", "[0] * TMath::Power(x,[1])", 0., 100.)
    spectrum.Fit("fitfunction", "N", "", 15., 50.)
    return fitfunction

def CreateTurnonPlot(filename):
    data = ReadSpectra(filename)
    emctriggers = ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    parMB = ParameteriseMinBiasSpectrum(MakeNormalisedSpectrum(data["MinBias"], "MinBias"))
    emcdata = {}
    for trg in emctriggers:
        emcdata[trg] = TriggerTurnonCurve(trg, MakeNormalisedSpectrum(data[trg], trg), parMB)
    plot = TriggerTurnonPlot(emcdata)
    plot.Create()
    return plot

