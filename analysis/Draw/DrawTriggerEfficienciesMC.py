"""
Created on 29.09.2014

@author: markusfasel
"""

from base.MonteCarloFileHandler import MonteCarloFileHandler
from base.Graphics import Style
from plots.TriggerEfficiencyPlotMC import TriggerEfficiencyPlotMC,TriggerEfficiencySumPlot
from base.TriggerEfficiency import TriggerEfficiency
from os import getcwd
from ROOT import kRed, kBlue, kBlack, kGreen, kMagenta, kViolet, kOrange, kTeal, kYellow, kGray, kCyan

class TriggerEffDrawerMC(object):
    """
    Controller class drawing the trigger efficiency plot
    """

    def __init__(self):
        """ 
        Constructor initialising basic variables
        """
        self.__filehandler = MonteCarloFileHandler(True)
        self.__plotter = TriggerEfficiencyPlotMC()
        self.__nbins = 1
        
    def SetNumberOfPtHatBins(self, nbins):
        """
        Set the number of pthat bins
        """
        self.__nbins = nbins
        
    def SetBaseDirectory(self, path):
        """
        Change the base directory, and read in files for all pt-hat bins
        """
        for i in range(1, self.__nbins + 1):
            self.__filehandler.AddFile("%s/%02d/AnalysisResults.root" %(path, i), i)

    def CreatePlot(self, trigger):
        """
        Create the plot
        """
        styles = [Style(kBlack, 24), Style(kBlue, 25), Style(kRed, 26), Style(kGreen, 27), Style(kMagenta, 28), Style(kOrange, 29), \
                  Style(kTeal, 30), Style(kViolet, 31), Style(kGray, 32), Style(kYellow + 2, 33), Style(kCyan+3, 34), Style(kRed-9, 35)]
        triggerCalculator = None
        for i in range(1, self.__nbins + 1):
            collection = self.__filehandler.GetCollection().GetData(i)
            tcname = "tracksWithClusters"
            #tcname = "tracksAll"
            triggerCalculator = TriggerEfficiency(trigger, collection.GetData("MinBias").FindTrackContainer(tcname), collection.GetData(trigger).FindTrackContainer(tcname))
            self.__plotter.AddEfficiency(i, triggerCalculator.GetEfficiencyCurve(), styles[i-1])
        self.__plotter.Create()
        return self.__plotter
    
class TriggerEffSumDrawer(object):
    """
    Controller class drawing the trigger efficiency plot
    """

    def __init__(self):
        """ 
        Constructor initialising basic variables
        """
        self.__filehandler = MonteCarloFileHandler(True)
        self.__plotter = None
        self.__nbins = 1
        self.__summedData = None
        
    def SetNumberOfPtHatBins(self, nbins):
        """
        Set the number of pthat bins
        """
        self.__nbins = nbins
        
    def SetBaseDirectory(self, path):
        """
        Change the base directory, and read in files for all pt-hat bins
        """
        for i in range(1, self.__nbins + 1):
            self.__filehandler.AddFile("%s/%02d/AnalysisResults.root" %(path, i), i)
            
    def WriteSummedData(self, filename):
        self.__summedData.Write(filename)

    def CreatePlot(self, trigger):
        """
        Create the plot
        """
        self.__summedData = self.__filehandler.GetCollection().SumWeightedData()
        tcname = "tracksWithClusters"
        self.__plotter = TriggerEfficiencySumPlot(trigger, TriggerEfficiency(trigger, self.__summedData.GetData("MinBias").FindTrackContainer(tcname), self.__summedData.GetData(trigger).FindTrackContainer(tcname)))
        self.__plotter.Create()
        return self.__plotter

        
def DrawTriggerEfficiency(trigger, basedir = None):
    drawer = TriggerEffDrawerMC()
    drawer.SetNumberOfPtHatBins(9)
    if not basedir:
        basedir = getcwd()
    print "Using results from directory %s" %(basedir)
    drawer.SetBaseDirectory(basedir)
    return drawer.CreatePlot(trigger)

def DrawTriggerEfficiencySummed(trigger, basedir = None):
    drawer = TriggerEffSumDrawer()
    drawer.SetNumberOfPtHatBins(4)
    if not basedir:
        basedir = getcwd()
    print "Using results from directory %s" %(basedir)
    drawer.SetBaseDirectory(basedir)
    plot = drawer.CreatePlot(trigger)
    drawer.WriteSummedData("SumPtHatBins.root")
    return plot
