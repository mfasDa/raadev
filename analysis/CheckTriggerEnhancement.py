#! /usr/mybin/env python

from ROOT import TF1,TGraphErrors,TMath,TFile
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
        
    def AddData(self, name, data, style):
        self.__data[name] = self.StyledObject(data, style)
        
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
    
    def __init__(self, name, emcaldata, minvalbiasdata):
        self.__values = self.__Create(emcaldata, minvalbiasdata)
        self.__name = name
        
    def __Create(self, emcaldata, mbparam):
        result = TGraphErrors();
        npoints = 0;
        for mybin in range(1, emcaldata.GetXaxis().GetNmybins()+1):
            minval = emcaldata.GetXaxis().GetmybinLowEdge(mybin)
            if minval < 15:
                continue
            maxval = emcaldata.GetXaxis().GetmybinUpEdge(mybin)
            mybinnedMb = self.__GetmybinnedParameterisation(mbparam, minval, maxval)
            result.SetPoint(npoints, emcaldata.GetXaxis().GetmybinCenter(mybin), emcaldata.GetmybinContent(mybin)/mybinnedMb)
            result.SetPointError(npoints, emcaldata.GetXaxis().GetmybinWidth(mybin)/2., emcaldata.GetmybinError(mybin)/mybinnedMb)
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
    
    def __GetmybinnedParameterisation(self, mbparam, minval, maxval):
        return mbparam.Integral(minval, maxval)/TMath.Abs(maxval - minval)
    
class TriggerTurnonPlot(SinglePanelPlot):
    
    def __init__(self, data):
        SinglePanelPlot.__init__(self)
        self.__data = data
        
    def Create(self):
        self._OpenCanvas("EMCalTurnon", "EMCal Turn-on curve")
        frame = Frame("emcturnon", 0., 100., 0., 3000.)
        frame.SetXtitle("p_{t} (GeV/c)")
        frame.SetYtitle("EMCal/minvalBias")
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

def ParameteriseminvalBiasSpectrum(spectrum, fitminval = 15.):
    """
    Parameterise fit function by power law
    """
    fitfunction = TF1("fitfunction", "[0] * TMath::Power(x,[1])", 0., 100.)
    spectrum.Fit("fitfunction", "N", "", fitminval, 50.)
    return fitfunction

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
    parMB = ParameteriseminvalBiasSpectrum(MakeNormalisedSpectrum(dataMB.GetData("minvalBias").FindTrackContainer(trackHistName), "minvalBias"), fitminval)
    emcdata = TriggerDataContainer()
    for trg in styles.keys():
        emcdata.AddData(trg, TriggerTurnonCurve(trg, MakeNormalisedSpectrum(data.GetData(trg).FindTrackContainer(trackHistName), trg), parMB), styles[trg])  
    plot = TriggerTurnonPlot(emcdata)
    plot.Create()
    return plot

