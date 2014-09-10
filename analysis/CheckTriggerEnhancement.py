#! /usr/bin/env python

from ROOT import TF1,TGraphErrors,TMath
from ROOT import kRed, kBlue, kOrange, kGreen
from base.Graphics import Frame, SinglePanelPlot, GraphicsObject, Style
from base.FileHandler import LegoTrainFileReader

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
        
        def MakeGraphicsObject(self):
            return GraphicsObject(self.__data.GetPoints(), self.__style)
    
    def __init__(self):
        self.__data = {}
        
    def AddData(self, name, object, style):
        self.__data[name] = self.StyledObject(object, style)
        
    def SetStyle(self, name, style):
        self.__data[name].SetStyle(style)
        
    def GetGraphicsList(self):
        graphicsList = {}
        for entry in sorted(self.__data.keys()):
            graphicsList[entry] = self.__data[entry].MakeGraphicsObject()
        return graphicsList
            
    def DrawAll(self, frame):
        graphicsList = self.GetGraphicsList()
        for entry in sorted(graphicsList):
            frame.DrawGraphicsObject(graphicsList[entry], addToLegend = True, title = entry)
                    
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
    
    def MakeGraphicsObject(self, style):
        return GraphicsObject(self.__values, style)
         
    def WriteData(self, name):
        self.__values.Write("turnonCurve%s" %(name))
    
    def __GetBinnedParameterisation(self, mbparam, min, max):
        return mbparam.Integral(min, max)/TMath.Abs(max - min)
    
class TriggerTurnonPlot(SinglePanelPlot):
    
    def __init__(self, data):
        SinglePanelPlot.__init__(self)
        self.__data = data
        
    def Create(self):
        self._OpenCanvas("EMCalTurnon", "EMCal Turn-on curve")
        frame = Frame("emcturnon", 0., 100., 0., 3000.)
        frame.SetXtitle("p_{t} (GeV/c)")
        frame.SetYtitle("EMCal/MinBias")
        pad = self._GetFramedPad()
        pad.DrawFrame(frame)
        self.__data.DrawAll(pad)
        pad.CreateLegend(0.55, 0.67, 0.89, 0.89)
            
    def GetData(self):
        return self.__data
    
    def WriteData(self, filename):
        self.__data.Write(filename)
        
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

def ReadData(filename):
    reader = LegoTrainFileReader(filename)
    return reader.ReadFile()

def CreateTurnonPlot(filename, filenameMB, fitmin = 15., requireCluster = False):
    trackHistName = "tracksAll"
    if requireCluster:
        trackHistName = "tracksWithClusters"
    data = ReadData(filename)
    dataMB = ReadData(filenameMB)
    styles = {"EMCJHigh" : Style(kRed, 24), "EMCJLow" : Style(kOrange, 26), "EMCGHigh" : Style(kBlue, 25), "EMCGLow" : Style(kGreen, 27)}
    parMB = ParameteriseMinBiasSpectrum(MakeNormalisedSpectrum(dataMB.GetData("MinBias").FindTrackContainer(trackHistName), "MinBias"), fitmin)
    emcdata = TriggerDataContainer()
    for trg in styles.keys():
        emcdata.AddData(trg, TriggerTurnonCurve(trg, MakeNormalisedSpectrum(data.GetData(trg).FindTrackContainer(trackHistName), trg), parMB), styles[trg])  
    plot = TriggerTurnonPlot(emcdata)
    plot.Create()
    return plot

