'''
Created on 21.09.2014

@author: markusfasel
'''
from base.SpectrumContainer import SpectrumContainer
from base.FileHandler import LegoTrainFileReader
from plots.TrackYieldEventPlot import TrackYieldEventPlot
from base.SpectrumCombiner import SpectrumCombiner
from base.SpectrumFitter import PowerLawModel, ModifiedHagedornModel

def MakeNormalisedSpectrum(container):
    inputcontainer = container.FindTrackContainer("tracksAll")
    try:
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
    except SpectrumContainer.RangeException as e:
        print str(e)
    return inputcontainer.MakeProjection(0, "ptSpectrum%s", "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}")

def Draw(filename, trigger = "MinBias"):
    reader = LegoTrainFileReader(filename)
    content = reader.ReadFile()
    content.SetName("RawSpectra")
    isMinBias = trigger == "MinBias"
    fitrange = [15., 50]
    if not isMinBias:
        fitrange = [50., 100.]
    plot = TrackYieldEventPlot(MakeNormalisedSpectrum(content.GetData(trigger)), fitrange, PowerLawModel())
    plot.SetLabel("Fit model: Power Law")
    plot.Create()
    return plot

def DrawCombined(filename, trigger = "EMCJHigh"):
    reader = LegoTrainFileReader(filename)
    content = reader.ReadFile()
    spectrumCombiner = SpectrumCombiner(MakeNormalisedSpectrum(content.GetData("MinBias")), \
                                        MakeNormalisedSpectrum(content.GetData(trigger)))
    
    plot = TrackYieldEventPlot(spectrumCombiner.MakeCombinedSpectrum(50.), [2., 90.], ModifiedHagedornModel())
    plot.SetLabel("Fit model: Modified Hagedorn Function")
    plot.Create()
    return plot
