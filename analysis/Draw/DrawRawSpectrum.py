#! /usr/bin/env python
from ROOT import kRed,kBlue,kGreen,kOrange
from base.FileHandler import ResultDataBuilder
from base.Graphics import Style
from plots.TriggeredSpectrumComparisonPlot import PtTriggeredSpectrumComparisonPlot, EnergyTriggeredSpectrumComparisonPlot

class RawSpectrumDrawer(object):
    styles = {"EMCJHigh":Style(kRed,24), "EMCJLow":Style(kOrange,26), "EMCGHigh":Style(kBlue,25), "EMCGLow":Style(kGreen, 28)}
    
    def __init__(self, filename, filetype = "lego"):
        reader = ResultDataBuilder(filetype, filename)
        self.__data = reader.GetResults()
        plots = {}
        for tracks in ["tracksAll", "tracksWithClusters"]:
            plots[tracks] = self.MakeTrackComparisonPlot(tracks)
        for clusters in ["Calib", "Uncalib"]:
            plots[clusters] = self.MakeClusterComparisonPlot(clusters)
        
    def MakeTrackComparisonPlot(self, contname):
        plot = PtTriggeredSpectrumComparisonPlot("canvas%s" %(contname))
        for trg in self.styles.keys():
            plot.AddSpectrum(trg, self.MakeNormalisedSpectrum(self.__data.GetData(trg).FindTrackContainer(contname), True), self.styles[trg])
        plot.Create()
        return plot
    
    def MakeClusterComparisonPlot(self, contname):
        plot = EnergyTriggeredSpectrumComparisonPlot("canvas%s" %(contname))
        for trg in self.styles.keys():
            plot.AddSpectrum(trg, self.MakeNormalisedSpectrum(self.__data.GetData(trg).FindClusterContainer(contname), False), self.styles[trg])
        plot.Create()
        return plot
        
    def MakeNormalisedSpectrum(self, spectrum, istrack):
        spectrum.SetVertexRange(-10., 10.)
        spectrum.SetPileupRejection(True)
        if istrack:
            spectrum.SelectTrackCuts(1)
        return spectrum.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")


def CreatePlot(filename, filetype = "lego"):
    plotter = RawSpectrumDrawer(filename, filetype)
    return plotter

