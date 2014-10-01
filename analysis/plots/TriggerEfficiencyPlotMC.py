"""
Created on 29.09.2014

Comparison plot of trigger efficiencies in MC in different pt-hat bins including underlying data structure

@author: markusfasel
"""

from base.Graphics import SinglePanelPlot, GraphicsObject, Frame, Style
from ROOT import kBlack

class TriggerEfficiencyContainer:
    """
    Underlying data structure for the comparison plot
    """
    
    def __init__(self):
        """
        Initialise container
        """
        self.__pthatbins = {}
    
    def AddEfficiency(self, pthatbin, efficiencyCurve, style):
        """
        Add new pt-hat bin
        """
        self.__pthatbins[pthatbin] = GraphicsObject(efficiencyCurve, style)
        
    def DrawEfficiencies(self, pad):
        """
        Draw all efficiencies into the pad
        """
        for pthatbin, efficiency in self.__pthatbins.iteritems():
            pad.DrawGraphicsObject(efficiency, True, "p_{t}-hat bin %d" %(pthatbin))
    

class TriggerEfficiencyPlotMC(SinglePanelPlot):
    """
    Comparison plot of trigger efficiencies in different pt-hat bins
    """

    def __init__(self):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__efficiencyContainer = TriggerEfficiencyContainer()
        self.__triggername = ""
        
    def SetTriggerName(self, trname):
        """
        Set triggername for the label
        """
        self.__triggername = trname
    
    def AddEfficiency(self, pthatbin, efficiency, style):
        """
        Add new efficiency container to the data structure
        """
        self.__efficiencyContainer.AddEfficiency(pthatbin, efficiency, style)
        
    def Create(self):
        """
        Create the plot
        """
        self._OpenCanvas("triggerEfficiencyMC", "MC trigger efficiency plot")
        pad = self._GetFramedPad()
        frame = Frame("tframe", 0., 100., 0., 1.)
        frame.SetXtitle("p_{t} (GeV/c)")
        frame.SetYtitle("Trigger efficiency")
        pad.DrawFrame(frame)
        self.__efficiencyContainer.DrawEfficiencies(pad)
        pad.CreateLegend(0.65, 0.15, 0.89, 0.5)
        pad.DrawLabel(0.15, 0.8, 0.5, 0.85, self.__triggername)
        
class TriggerEfficiencySumPlot(SinglePanelPlot):
    """
    Plot the summed trigger efficiency from different pt-hard bins
    """
    
    def __init__(self, triggername, triggerefficiency):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__triggername = triggername
        self.__triggereff = triggerefficiency
        
    def Create(self):
        """
        Create the plot
        """
        self._OpenCanvas("trgEffSumm", "Summed trigger efficiency")
        pad = self._GetFramedPad()
        frame = Frame("tframe", 0., 100., 0., 1.)
        frame.SetXtitle("p_{t} (GeV/c)")
        frame.SetYtitle("Trigger efficiency")
        pad.DrawFrame(frame)
        pad.DrawGraphicsObject(GraphicsObject(self.__triggereff.GetEfficiencyCurve(), Style(kBlack, 20)), False, "Trigger Eff")
        pad.DrawLabel(0.5, 0.2, 0.89, 0.25, "Trigger: %s" %(self.__triggername))