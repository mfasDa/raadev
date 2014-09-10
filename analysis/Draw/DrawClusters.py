#! /usr/bin/env python

from FileHandler import LegoTrainFileReader
from Graphics import FourPanelPlot,GraphicsObject,Style,Frame
from ROOT import kBlack,kBlue,kGreen,kRed,kOrange

from Helper import MakeRatio,HistToGraph

class ClusterComparisonPlot(FourPanelPlot):
    
    def __init__(self, comparisonCalib, comparisonUncalib):
        FourPanelPlot.__init__(self)
        self.__comparisonCalib = comparisonCalib
        self.__comparisonUncalib = comparisonUncalib
        
    def Create(self):
        self._OpenCanvas("clusterComparison", "Comparison of the cluster energy spectrum for different triggers")
        
        spectrumFrame = Frame("specfram", 0., 100., 1e-10, 100)
        spectrumFrame.SetXtitle("E (GeV)")
        spectrumFrame.SetYtitle("1/N_{ev} 1/(#Delta E) dN/dE (1/(GeV/c)^{2})")
        ratioFrame = Frame("ratioframe", 0., 100., 0., 2000.)
        ratioFrame.SetXtitle("E (GeV)")
        ratioFrame.SetYtitle("Triggered / Min. Bias")

        frames = [spectrumFrame, ratioFrame]
        comparisonObjects = [self.__comparisonCalib, self.__comparisonUncalib]
        modes = ["Calibrated clusters", "UncalibratedClusters"]
        for row in range(0,2):
            for col in range(0,2):
                pad = self._OpenPadByRowCol(row, col)
                pad.DrawFrame(frames[col])
                doRatio = False
                if col == 1:
                    doRatio = True
                else:
                    pad.GetPad().SetLogy(True)
                    pad.DrawLabel(0.15, 0.15, 0.65, 0.22, modes[row])
                if col == 0:
                    pad.DrawGraphicsObject(comparisonObjects[row].GetGraphicsInRange("MinBias", False), True, "Min. Bias")
                for t in ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]:
                    pad.DrawGraphicsObject(comparisonObjects[row].GetGraphicsInRange(t, doRatio), True, t)
                if row == 0 and col == 0:
                    pad.CreateLegend(0.5, 0.65, 0.89, 0.89)
        self._canvas.cd()
            
class ClusterComparison:
    
    def __init__(self, type, minbias, triggered):
        self.__minBias = minbias
        self.__triggered = triggered
        self.__ratios = self.__CalculateRatios()
        
    def GetGraphicsInRange(self, trigger, isRatio = False):
        graphics = None
        styles = {"MinBias":Style(kBlack, 20), "EMCJHigh":Style(kBlue, 24), "EMCJLow":Style(kRed, 26), "EMCGHigh":Style(kGreen,25), "EMCGLow":Style(kOrange,27)}
        if trigger is "MinBias":
            graphics = GraphicsObject(HistToGraph(self.__minBias, 0.1, 100.), styles["MinBias"])
        else:
            dict = self.__triggered
            if isRatio:
                dict = self.__ratios
            graphics = GraphicsObject(HistToGraph(dict[trigger], 0.1, 100.), styles[trigger])
        return graphics
        
    def __CalculateRatios(self):
        ratios = {}
        for trg in self.__triggered.keys():
            ratios[trg] = MakeRatio(self.__triggered[trg], self.__minBias)
        return ratios
    
def MakeClusterEnergySpectrum(data, trigger):
    cont = data.GetData(trigger)
    cont.SetVertexRange(-10, 10)
    cont.SetPileupRejection(True)
    result = {"Calib": cont.MakeClusterProjection(0, "Calib", "ClustECalib%s" %(trigger)), "Uncalib":cont.MakeClusterProjection(0, "Uncalib", "ClustEUncalib%s" %(trigger))}
    cont.Reset()
    return result
    
def DrawClusters():
    readerDE = LegoTrainFileReader("merged_DE/AnalysisResults.root")
    dataDE = readerDE.ReadFile()
    dataDE.SetName("LHC13de")
    readerC = LegoTrainFileReader("LHC13c/AnalysisResults.root")
    dataC = readerC.ReadFile()
    dataC.SetName("LHC13c")
    
    clustersCalibTRG = {}
    clustersUncalibTRG = {}
    clustersMB = MakeClusterEnergySpectrum(dataC, "MinBias")
    for t in ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]:
        res = MakeClusterEnergySpectrum(dataDE, t)
        clustersCalibTRG[t] = res["Calib"]
        clustersUncalibTRG[t] = res["Uncalib"]
    
    plot = ClusterComparisonPlot(ClusterComparison("Calib", clustersMB["Calib"], clustersCalibTRG),  ClusterComparison("Uncalib", clustersMB["Uncalib"], clustersUncalibTRG))
    plot.Create()
    return plot
    