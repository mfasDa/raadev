#! /usr/bin/env python
from ROOT import kRed,kBlue,kGreen,kOrange,kBlack
from base.FileHandler import ResultDataBuilder
from base.Graphics import Style
from plots.TriggeredSpectrumComparisonPlot import PtTriggeredSpectrumComparisonPlot, EnergyTriggeredSpectrumComparisonPlot

class RawSpectrumDrawer(object):
    styles = {"MinBias": Style(kBlack, 20), "EMCJHigh":Style(kRed,24), "EMCJLow":Style(kOrange,26), "EMCGHigh":Style(kBlue,25), "EMCGLow":Style(kGreen, 27)}
    
    def __init__(self, filename, filetype = "lego"):
        reader = ResultDataBuilder(filetype, filename)
        self.__data = reader.GetResults()
        self.__plots = {}
        for tracks in ["tracksAll", "tracksWithClusters"]:
            self.__plots[tracks] = self.MakeTrackComparisonPlot(tracks)
        for clusters in ["Calib", "Uncalib"]:
            self.__plots[clusters] = self.MakeClusterComparisonPlot(clusters)
        
    def MakeTrackComparisonPlot(self, contname):
        plot = PtTriggeredSpectrumComparisonPlot(contname)
        for trg in self.styles.keys():
            plot.AddSpectrum(trg, self.MakeNormalisedSpectrum(self.__data.GetData(trg).FindTrackContainer(contname), "%s%s" %(trg, contname), True), self.styles[trg])
        plot.Create()
        return plot
    
    def MakeClusterComparisonPlot(self, contname):
        plot = EnergyTriggeredSpectrumComparisonPlot(contname)
        nminbias = self.__data.GetData("MinBias").FindClusterContainer(contname).GetEventCount()
        for trg in self.styles.keys():
            plot.AddSpectrum(trg, self.MakeNormalisedSpectrum(self.__data.GetData(trg).FindClusterContainer(contname), "%s%s" %(trg, contname), False), self.styles[trg])
        plot.Create()
        return plot
        
    def MakeNormalisedSpectrum(self, spectrum, name, istrack):
        spectrum.SetVertexRange(-10., 10.)
        spectrum.SetPileupRejection(True)
        if istrack:
            spectrum.SelectTrackCuts(1)
        projected = spectrum.MakeProjection(0, "rawspectrum%s" %(name), "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")
        return projected

    def MakeNormalisedSpectrumV1(self, spectrum, name, nminbias, istrack):
        spectrum.SetVertexRange(-10., 10.)
        spectrum.SetPileupRejection(True)
        if istrack:
            spectrum.SelectTrackCuts(1)
        spectrum.RequestSeenInMinBias()
        projected =  spectrum.MakeProjection(0, "rawspectrum%s" %(name), "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}", doNorm = False)
        projected.Scale(nminbias)
        return projected
    
    def FindPlots(self, plotname):
        return self.__plots[plotname]
    
    def GetListOfPlots(self):
        return self.__plots


def CreatePlot(filename, filetype = "lego"):
    plotter = RawSpectrumDrawer(filename, filetype)
    return plotter

