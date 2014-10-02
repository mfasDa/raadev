"""
Created on 29.09.2014

Comparison plot of trigger efficiencies in MC in different pt-hat bins including underlying data structure

@author: markusfasel
"""

from base.Graphics import SinglePanelPlot, GraphicsObject, Frame, Style
from ROOT import TFile,kBlack

class TriggerEfficiencyClass:

    def __init__(self, data, style):
        self.__triggerdata = data
        self.__style = style
    
    def GetGraphicsObject(self):
        return GraphicsObject(self.__triggerdata, self.__style)
    
    def GetRootPrimitive(self):
        self.__triggerdata.SetName(self.GetTypeName())
        return self.__triggerdata
    
class TriggerEfficiencyClassPtHat(TriggerEfficiencyClass):
    
    def __init__(self, pthatbin, triggerdata, style):
        TriggerEfficiencyClass.__init__(self, triggerdata, style)
        self.__pthatbin = pthatbin
        
    def GetLegendTitle(self):
        return "p_{t}-hat bin %d" %(self.__pthatbin)
    
    def GetTypeName(self):
        return "pthat%d" %(self.__pthatbin)
    
class TriggerEfficiencyClassTriggerType(TriggerEfficiencyClass):
    
    def __init__(self, triggername, triggerdata, style):
        TriggerEfficiencyClass.__init__(self, triggerdata, style)
        self.__triggername =  triggername
        
    def GetLegendTitle(self):
        return self.__triggername
    
    def GetTypeName(self):
        return self.__triggername

class TriggerEfficiencyContainer:
    """
    Underlying data structure for the comparison plot
    """
    
    def __init__(self):
        """
        Initialise container
        """
        self.__trefficiencies = []
    
    def AddEfficiency(self, trclasstype, key, efficiencyCurve, style):
        """
        Add new trigger ifno
        """
        triggerdata = None
        if trclasstype == "pthat":
            triggerdata = TriggerEfficiencyClassPtHat(key, efficiencyCurve, style)
        elif trclasstype == "triggertype":
            triggerdata = TriggerEfficiencyClassTriggerType(key, efficiencyCurve, style)
        self.__trefficiencies.append(triggerdata)
        
    def DrawEfficiencies(self, pad):
        """
        Draw all efficiencies into the pad
        """
        for entry in self.__trefficiencies:
            pad.DrawGraphicsObject(entry.GetGraphicsObject(), True, entry.GetLegendTitle())
            
    def GetListOfTriggerEfficiencies(self):
        """
        Get a list of root-primitive trigger efficiencies
        """
        rootprimitives = []
        for entry in self.__trefficiencies:
            rootprimitives.append(entry.GetRootPrimitive())
        return rootprimitives
            

class TriggerEfficiencyFrame(Frame):
    """
    Frame class for trigger efficiency plots
    """
    
    def __init__(self, name):
        """
        Constructor
        """
        Frame.__init__(self, name, 0., 100., 0., 1.)
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle("Trigger efficiency")
        
class TriggerEfficiencyComparisonPlot(SinglePanelPlot):
    """
    General plot for trigger efficiency comparisons
    """
        
    def __init__(self):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self._efficiencyContainer = TriggerEfficiencyContainer()
        
    def _Create(self, canvasname, canvastitle):
        """
        Make the plot
        """
        self._OpenCanvas(canvasname, canvastitle)
        pad = self._GetFramedPad()
        pad.DrawFrame(TriggerEfficiencyFrame("tframe"))
        self._efficiencyContainer.DrawEfficiencies(pad)
        pad.CreateLegend(0.65, 0.15, 0.89, 0.5)
        
    def WriteData(self, rootfilename):
        """
        Write out trigger efficiency curves to a root file
        """
        outputfile = TFile(rootfilename, "RECREATE")
        for rootprim in self._efficiencyContainer.GetListOfTriggerEfficiencies():
            rootprim.Write()
        outputfile.Close()


class TriggerEfficiencyPlotMC(TriggerEfficiencyComparisonPlot):
    """
    Comparison plot of trigger efficiencies in different pt-hat bins
    """

    def __init__(self):
        """
        Constructor
        """
        TriggerEfficiencyComparisonPlot.__init__(self)
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
        self._efficiencyContainer.AddEfficiency("pthat", pthatbin, efficiency, style)
        
    def Create(self):
        """
        Create the plot
        """
        self._Create("triggerEfficiencyMC", "MC trigger efficiency plot")
        if len(self.__triggername):
            pad = self._GetFramedPad()
            pad.DrawLabel(0.15, 0.8, 0.5, 0.85, self.__triggername)
        
        
class TriggerEfficiencyPlotClasses(TriggerEfficiencyComparisonPlot):
    """
    Plot comparing the trigger efficiency of different trigger types
    """
    
    def __init__(self):
        """
        Constructor
        """
        TriggerEfficiencyComparisonPlot.__init__(self)
    
    def AddTriggerEfficiency(self, triggername, efficiency, style):
        """
        Add trigger class to the comparison data
        """
        self._efficiencyContainer.AddEfficiency("triggertype", triggername, efficiency, style)
        
    def Create(self):
        self._Create("triggerclasses", "Trigger efficiencies")
            
        
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
        pad.DrawFrame(TriggerEfficiencyFrame("tframe"))
        pad.DrawGraphicsObject(GraphicsObject(self.__triggereff.GetEfficiencyCurve(), Style(kBlack, 20)), False, "Trigger Eff")
        pad.DrawLabel(0.5, 0.2, 0.89, 0.25, "Trigger: %s" %(self.__triggername))