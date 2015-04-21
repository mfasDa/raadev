#**************************************************************************
#* Copyright(c) 1998-2014, ALICE Experiment at CERN, All rights reserved. *
#*                                                                        *
#* Author: The ALICE Off-line Project.                                    *
#* Contributors are mentioned in the code where appropriate.              *
#*                                                                        *
#* Permission to use, copy, modify and distribute this software and its   *
#* documentation strictly for non-commercial purposes is hereby granted   *
#* without fee, provided that the above copyright notice appears in all   *
#* copies and that both the copyright notice and this permission notice   *
#* appear in the supporting documentation. The authors make no claims     *
#* about the suitability of this software for any purpose. It is          *
#* provided "as is" without express or implied warranty.                  *
#**************************************************************************
"""
Module for spectrum comparison plots

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""
from base.Graphics import GraphicsObject,SinglePanelPlot
from ROOT import TFile

class ComparisonObject(object):
    """
    Base entry type for object inside comparison data
    """
    
    def __init__(self, data, style):
        """
        Constructor
        
        :param data: Data of the object to be plotted 
        :type data: TGraph (and deriving), TH1 (and deriving), TF1
        :param style: Plotting style
        :type style: Style
        """
        self.__data = data
        self.__style = style
        
    def GetData(self):
        """
        Get the raw data
        
        :return: Data of the object to be plotted 
        :rtype: TGraph (and deriving), TH1 (and deriving), TF1
        """
        return self.__data
        
    def GetGraphicsObject(self):
        """
        Get the graphics object
        
        :return: Object to be drawn
        :rtype: GraphicsObject
        """
        return GraphicsObject(self.__data, self.__style)
    
    def GetRootPrimitive(self):
        """
        Get the underlying root object
        
        :return: Underlying ROOT object
        :rtype: TGraph (and deriving), TH1 (and deriving), TF1
        """
        self.__data.SetName(self.GetObjectName())
        return self.__data
    
    def Draw(self, pad, addToLegend = True):
        """
        Draw the graphics object into a given pad

        :param pad: 
        :type pad: FramedPad
        :param addToLegend: If true the object is added to a legend
        :type addToLegend: bool
        """
        pad.DrawGraphicsObject(self.GetGraphicsObject(), addToLegend, self.GetLegendTitle())
    
    def GetLegendTitle(self):
        """
        To be implemented in inheriting classes
        """
        return ""
    
    def GetObjectName(self):
        """
        To be implemented in inheriting classes
        """
        return ""
    
class ComparisonData(object):
    """
    General comparison data collection
    """

    def __init__(self):
        """
        Constructor
        """
        self.__entries = []
        
    def GetEntries(self):
        """
        Get entry list of the data collection
        
        :return: The list of plot objects
        :rtype: list
        """
        return self.__entries
        
    def AddEntry(self, entry):
        """
        Add new entry to the list
        
        :param entry: New entry to be plotted
        :type entry: ComparisonObject
        """
        self.__entries.append(entry)
        
    def DrawObjects(self, pad, addToLegend = True):
        """
        Draw all objects in the comparison data
        
        :param pad: Pad where the objects are plotted
        :type pad: FramedPad
        :param addToLegend: If true the object is added to a legend
        :type addToLegend: bool
        """
        for entry in self.__entries:
            entry.Draw(pad, addToLegend)
            
    def GetListOfRootObjects(self):
        """
        Get a list of root-primitive objects
        
        :return: list of root objects
        :rtype: list
        """
        rootprimitives = []
        for entry in self.__entries:
            rootprimitives.append(entry.GetRootPrimitive())
        return rootprimitives
    
class ComparisonPlot(SinglePanelPlot):
    """
    General comparison plot type
    """
        
    def __init__(self):
        """
        Constructor
        """
        SinglePanelPlot.__init__(self)
        self.__frame = None
        self._comparisonContainer = None    # be specified in inheriting classes
        self.__legendAttributes = None
        self.__padattributes = {"logx":False, "logy":False, "gridx":False, "gridy":False}
        
    def SetFrame(self, frame):
        """
        Define the frame shown in the plot
        
        :param frame: Frame of the plot
        :type frame: Frame
        """
        self.__frame = frame
        
    def SetLegendAttributes(self, xmin, ymin, xmax, ymax):
        """
        Set the legend position
        
        :param xmin: Min. x coordinate
        :type xmin: float
        :param xmax: Max. x coordinate
        :type xmax: float
        :param xmin: Min. y coordinate
        :type xmin: float
        :param ymax: Max. y coordinate
        :type ymax: float
        """
        self.__legendAttributes = {"xmin":xmin, "xmax":xmax, "ymin":ymin, "ymax":ymax}
        
    def SetPadAttributes(self, logx, logy, gridx, gridy):
        """
        Set attributes (log style, grid style) of the pad
        
        :param logx: If true logscale is used in x direction
        :type logx: bool
        :param logy: If true logscale is used in y direction
        :type logy: bool
        :param gridx: If true a grid is shown in x direction
        :type gridx: bool
        :param gridy: If true a grid is shown in y direction
        :type gridy: bool
        """
        self.__padattributes["logx"] = logx
        self.__padattributes["logy"] = logy
        self.__padattributes["gridx"] = gridx
        self.__padattributes["gridy"] = gridy
        
    def _Create(self, canvasname, canvastitle):
        """
        Make the plot
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Name of the canvas
        :type canvastitle: str
        """
        self._OpenCanvas(canvasname, canvastitle)
        pad = self._GetFramedPad()
        if self.__padattributes["logx"]:
            pad.GetPad().SetLogx()
        if self.__padattributes["logy"]:
            pad.GetPad().SetLogy()
        pad.DrawFrame(self.__frame)
        doLegend = False
        if self.__legendAttributes:
            doLegend = True
        self._comparisonContainer.DrawObjects(pad, doLegend)
        if doLegend:
            pad.CreateLegend(self.__legendAttributes["xmin"], self.__legendAttributes["ymin"], self.__legendAttributes["xmax"], self.__legendAttributes["ymax"])
        
    def WriteData(self, rootfilename):
        """
        Write out trigger efficiency curves to a root file
        
        :param rootfilename: Filename of the output root file
        :type rootfilename: str
        """
        outputfile = TFile(rootfilename, "RECREATE")
        for rootprim in self._comparisonContainer.GetListOfRootObjects():
            rootprim.Write()
        outputfile.Close()