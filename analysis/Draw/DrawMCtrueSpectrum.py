""""
Created on 29.09.2014

@author: markusfasel
"""

from base.MonteCarloFileHandler import MonteCarloFileHandler
from base.Graphics import Style
from base.Helper import NormaliseBinWidth
from os import getcwd
from plots.MCTruthPlot import MCTruthSpectrumPlot, MCWeightPlot
from ROOT import kRed, kBlue, kBlack, kGreen, kMagenta, kViolet, kOrange, kTeal, kYellow, kGray, kCyan

class MCTrueDrawer():
    
    def __init__(self):
        self.__handler = MonteCarloFileHandler(True)
        self.__plotter = MCTruthSpectrumPlot()
        self.__nbins = 1
    
    def SetNumberOfPtHatBins(self, nbins):
        self.__nbins = nbins
        
    def SetBaseDirectory(self, path):
        for i in range(1, self.__nbins + 1):
            self.__handler.AddFile("%s/%02d/AnalysisResults.root" %(path, i), i)
            
    def CreatePlot(self):
        datacol = self.__handler.GetCollection()
        styles = [Style(kGreen-2, 24), Style(kBlue, 25), Style(kRed, 26), Style(kGreen, 27), Style(kMagenta, 28), Style(kOrange, 29), \
                  Style(kTeal, 30), Style(kViolet, 31), Style(kGray, 32), Style(kYellow + 2, 33), Style(kCyan+3, 34), Style(kRed-9, 35)]
        for i in range(1, self.__nbins + 1):
            cont = datacol.GetData(i).GetMCTruth()
            spectrum = cont.ProjectToDimension(0,"MCtruth%d" %(i))
            spectrum.Sumw2()
            NormaliseBinWidth(spectrum)
            trackCont = datacol.GetData(i).GetData("MinBias").FindTrackContainer("tracksAll")
            spectrum.Scale(1./trackCont.GetEventCount())
            datacol.GetWeigthHandler().ReweightSpectrum(i, spectrum)
            self.__plotter.AddMCSpectrum(i, spectrum, styles[i])
        self.__plotter.Create()
        return self.__plotter
    
class WeightPlotter():
    
    def __init__(self):
        self.__handler = MonteCarloFileHandler(True)
        self.__plotter = None
        self.__nbins = 1
    
    def SetNumberOfPtHatBins(self, nbins):
        self.__nbins = nbins
        
    def SetBaseDirectory(self, path):
        for i in range(1, self.__nbins + 1):
            self.__handler.AddFile("%s/%02d/AnalysisResults.root" %(path, i), i)
            
    def CreatePlot(self):
        self.__plotter = MCWeightPlot(self.__handler.GetCollection().GetWeigthHandler())
        self.__plotter.Create()
        return self.__plotter

def DrawWeights(basedir = None):
    drawer = WeightPlotter()
    drawer.SetNumberOfPtHatBins(9)
    if not basedir:
        basedir = getcwd()
    print "Using results from directory %s" %(basedir)
    drawer.SetBaseDirectory(basedir)
    return drawer.CreatePlot()    

def DrawMC(basedir = None):
    drawer = MCTrueDrawer()
    drawer.SetNumberOfPtHatBins(9)
    if not basedir:
        basedir = getcwd()
    print "Using results from directory %s" %(basedir)
    drawer.SetBaseDirectory(basedir)
    return drawer.CreatePlot()