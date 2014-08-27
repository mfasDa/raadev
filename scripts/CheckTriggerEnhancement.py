#! /usr/bin/env python

from ROOT import TCanvas,TF1,TFile,TGraphErrors,TLegend,TMath
from ROOT import kRed, kBlue, kOrange, kGreen
from Helper import ReadHistList,Frame, Style
from SpectrumContainer import DataContainer

class TriggerDataContainer():
    
    class StyledObject:
        
        def __init__(self, data, style):
            self.__data = data
            self.__style = style
            
        def SetData(self, data):
            self.__data = data
            
        def GetData(self):
            return self.__data
        
        def SetStyle(self, style):
            self.__style = style
            
        def GetStyle(self):
            return self.__style
    
    def __init__(self):
        self.__data = {}
        
    def AddData(self, name, object, style):
        self.__data[name] = self.StyledObject(object, style)
        
    def SetStyle(self, style):
        self.__data[name].SetStyle(style)
        
    def DrawAll(self):
        for entry in sorted(self.__data.keys()):
            self.__data[entry].GetData().Draw(self.__data[entry].GetStyle())
        
    def AddAllToLegend(self, legend):
        for entry in sorted(self.__data.keys()):
            self.__data[entry].GetData().AddToLegend(legend, entry)
            
    def Write(self, filename):
        outputfile = TFile(filename, "RECREATE")
        outputfile.cd()
        for trigger in sorted(self.__data.keys()):
            self.__data[trigger].GetData().WriteData(trigger)
        outputfile.Close()

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
        
    def AddToLegend(self, legend, name):
        legend.AddEntry(self.__values, name, "lep")
        
    def WriteData(self, name):
        self.__values.Write("turnonCurve%s" %(name))
    
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
        self.__legend = TLegend(0.55, 0.75, 0.89, 0.89)
        self.__legend.SetBorderSize(0)
        self.__legend.SetFillStyle(0)
        self.__legend.SetTextFont(42)
        self.__data.DrawAll()
        self.__data.AddAllToLegend(self.__legend)
        self.__legend.Draw()
            
    def SaveAs(self, filenamebase):
        """
        Save plot as image file
        """
        types = ["eps", "pdf", "jpeg", "gif", "png"]
        for t in types:
            self.__canvas.SaveAs("%s.%s" %(filenamebase, t))
            
    def GetData(self):
        return self.__data
    
    def WriteData(self, filename):
        self.__data.Write(filename)
        
def ReadSpectra(filename, triggers):
    """
    Read the spectra for different trigger classes from the root file
    Returns a dictionary of triggers - spectrum container
    """
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

def ParameteriseMinBiasSpectrum(spectrum, fitmin = 15.):
    """
    Parameterise fit function by power law
    """
    fitfunction = TF1("fitfunction", "[0] * TMath::Power(x,[1])", 0., 100.)
    spectrum.Fit("fitfunction", "N", "", fitmin, 50.)
    return fitfunction

def CreateTurnonPlot(filename, filenameMB, fitmin = 15.):
    triggers = ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    triggersMB = ["MinBias"]
    data = ReadSpectra(filename, triggers)
    dataMB = ReadSpectra(filenameMB, triggersMB)
    emctriggers = ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    styles = {"EMCJHigh" : Style(kRed, 24), "EMCJLow" : Style(kOrange, 26), "EMCGHigh" : Style(kBlue, 25), "EMCGLow" : Style(kGreen, 27)}
    parMB = ParameteriseMinBiasSpectrum(MakeNormalisedSpectrum(dataMB["MinBias"], "MinBias"), fitmin)
    emcdata = TriggerDataContainer()
    for trg in emctriggers:
        emcdata.AddData(trg, TriggerTurnonCurve(trg, MakeNormalisedSpectrum(data[trg], trg), parMB), styles[trg])  
    plot = TriggerTurnonPlot(emcdata)
    plot.Create()
    return plot

