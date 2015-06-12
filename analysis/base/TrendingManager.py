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
Simple python trending manager based on ROOT and the Graphics Framework

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved

:author: Markus Fasel
:contact: <markus.fasel@cern.ch>
:organization: Lawrence Berkeley National Laboratory
"""

from base.Graphics import SinglePanelPlot, GraphicsObject, Style 
from base.FrameTemplates import AdjustableRangeFrame
from ROOT import TGraph
from ROOT import kBlack, kRed, kBlue, kGreen, kMagenta, kOrange, kTeal, kViolet, kYellow, kGray, kAzure

class TrendingPlot(SinglePanelPlot):
    """
    Plot class for trending plots, connected to the trending manager
    """
    
    def __init__(self, trendmgr):
        """
        Constructor of the trending plot
        
        :param dataset: Name of the dataset
        :type dataset: str
        :param trendmgr: Associated trending manager
        :type trendmgr: Trending manager
        """
        self.__trendmanager = trendmgr
        
    def Create(self, ytitle):
        """
        Creating the trending plot using with all curves from the trending manager
        
        :param ytitle: title of the y-axis
        :type ytitle: str
        """
        self._OpenCanvas("TrendingPlot%s" %self.__trendmanager.GetDataset(), "Trending plot for %s" %self.__trendmanager.GetDataset())
        
        trendpad = self._GetFramedPad()
        trendpad.DrawFrame(AdjustableRangeFrame("trendingframe", 
                                                {
                                                 "xmin": self.__trendmanager.GetMin("X"), 
                                                 "ymin": self.__trendmanager.GetMin("Y"), 
                                                 "xmax": self.__trendmanager.GetMax("X"),
                                                 "ymax": self.__trendmanager.GetMax("Y")
                                                 }, 
                                                {"xtitle":"run number", "ytitle":ytitle}))
        for data in self.__trendmanager.GetDataList():
            trendpad.DrawGraphicsObject(data["graphics"], addToLegend=True, title=data["name"])
        trendpad.CreateLegend(0.55, 0.65, 0.89, 0.89)
        trendpad.DrawLabel(0.15, 0.15, 0.45, 0.22, self.__trendmanager.GetDataset())

class TrendingManager(object):
    """
    Simple trending manager. Creates graphs for different trending variables
    and fills them for given runs.
    """
    
    class TrendingData(object):
        """
        Helper class encapsulating information needed for trending data (name, datapoints, style)
        used in the trending manager
        """
        
        def __init__(self, name):
            """
            Constructor
            
            :param name: name of the data type
            :type name: str
            """
            self.__name = name
            self.__points = TGraph()
            self.__style = Style(kBlack, 20)
            self.__styleinitialized = False
            
        def __cmp__(self, other):
            """
            Compare  name of this trending data to the other object by the name. Other is supposed
            to be of type str or TrendingData
            
            :param other: object to compare with
            :type other: str or base.TrendingManager.TrendingManager.TrendingData
            :return: 0 if names are the same, -1 if this name is smaller, 1 if this name is larger or other is not of compatible type
            :rtype: int
            """
            if isinstance(other, str):
                return self.__CompareNames(str(other))
            elif isinstance(other, TrendingManager.TrendingData):
                return self.__CompareNames(other.GetName())
            else:
                return 1
            
        def __CompareNames(self, othername):
            """
            Compare this name to another name

            :param othername: name to compare with
            :type other: str
            :return: 0 if names are the same, -1 if this name is smaller, 1 if this name is larger
            :rtype: int
            """
            if self.__name == othername:
                return 0
            elif self.__name < othername:
                return -1
            else:
                return 1
            
        def AddDatapoint(self, run, value):
            """
            Add new datapoint to the trending data
            """
            self.__datapoints.SetPoint(self.__datapoints.GetN(), run, value)
            
        def BuildGraphicsObject(self):
            """
            Build a graphics object from the datapoints and the style
            
            :return: The graphics object
            :rtype: base.Graphics.GraphicsObject
            """
            return GraphicsObject(self.__datapoints, self.__style, drawoption="lp")
        
        def GetName(self):
            """
            Get the name of the data
            
            :return: Name of the data
            :rtype: str
            """
            return self.__name
        
        def GetStyle(self):
            """
            Get the style of the data type
            
            :return: style of the data type
            :rtype: base.Graphics.Style
            """
            return self.__style
        
        def IsStyleInitialzed(self):
            """
            Check if the style is initialized
            
            :return: True if the style is initialized, False otherwise
            :rtype: bool
            """
            return self.__styleinitialized
        
        def SetName(self, name):
            """
            Set the name of the trending data
            
            :param name: Name of the data type
            :type name: str
            """
            self.__name = name

        def SetStyle(self, style):
            """
            Change the style of the trending data
            
            :param style: new style
            :type style: base.Graphics.Style
            """
            self.__style = style
            self.__styleinitialized = True
             
    class StyleManager(object):
        """
        Helper class managing a set of default plot styles
        """
        
        def __init__(self):
            """
            Constructor
            """
            self.__colors = [kBlack, kRed, kBlue, kGreen, kMagenta, kOrange, kTeal, kViolet, kYellow, kGray, kAzure]
            self.__markers = [24, 25, 26, 27, 28, 29, 30]
            self.__indexColor = 0
            self.__indexMarker = 0
            
        def GetNextSyle(self):
            """
            Iterate over styles (color and marker) to get the next style
            
            :return: The next plot style
            :rtype: Style
            """
            mycolor = self.__colors[self.__indexColor]
            mymarker = self.__markers[self.__indexMarker]
            # Forward iterators
            self.__indexColor = self.__indexColor + 1 if self.__indexColor + 1 < len(self.__colors) else 0
            self.__indexMaker = self.__indexMarker + 1 if self.__indexMarker + 1 < len(self.__colors) else 0
            return Style(mycolor, mymarker)
            
    def __init__(self, dataset):
        """
        Constructor
        
        :param dataset: name of the dataset
        :type dataset: str
        """
        self.__dataset = dataset
        self.__datapoints = []
        
    def AddDatapoint(self, name, run, value):
        """
        Adding a datapoint to the trending manager. If a graph for the datatype does not
        exist yet, create it
        
        :param name: Name of the datapoint
        :type name: str
        :param run: Run number
        :type run: int
        :param value: Value of the datapoint for the given run
        :type value: float
        """
        datapoints = None
        if not name in self.__datapoints:
            datapoints = self.TrendingData(name)
            self.__datapoints.append(datapoints)
        else:
            datapoints = self.__datapoints[self.__datapoints.index(name)]
        datapoints.AddDatapoint(run, value)
        
    def SetStyleForDatatype(self, typename, style):
        """
        Set the style for a given data type
        
        :param typename: name of the type using the new style
        :type typename: str
        :param style: new style for the given type
        :type style: base.Graphics.Style
        """
        if typename in self.__datapoints:
            self.__datapoints[self.__datapoints.index(typename)].SetStyle(style)
        
    def CreateTrendingPlot(self, ytitle):
        """
        Create a plot for the trending curves connected to this trending manager
        
        :param ytitle: title of the 
        :type ytitle: str
        """
        # fix styles of the datapoints
        stylemgr = self.StyleManager()
        for data in self.__datapoints:
            if not data.IsStyleInitialzed():
                data.SetStyle(stylemgr.GetNextSyle())
        # create the plot
        plot = TrendingPlot(self)
        plot.Create(ytitle)
        return plot
    
    def GetDataset(self):
        """
        Get the name of the data set the trending manager is used for
        
        :return: Name of the dataset
        :rtype: str
        """
        return self.__dataset
    
    def GetDataList(self):
        """
        Create a list of dictionaries with the trending graphs (as graphics object) and 
        the cooresponding names
        
        :return: list of trending graphs
        :rtype: list
        """
        result = []
        for data in self.__datapoints:
            result.append({"name":data.GetName(), "graphics":data.BuildGraphicsObject()})
        return result
        
    def GetMin(self, coordinate):
        """
        Determine minimum for a given coordinate for all datatypes.
        
        :param coordinate: Coordinate (X or Y)
        :type coordinate: str
        :return: Min. value of all data types
        :rtype: float
        """
        xmin = 0
        initialised = False
        for graph in self.__datapoints.values():
            gmin = self.__GetGraphLimit(coordinate, "MIN", graph)
            if not initialised:
                xmin = gmin
                initialised = True
            else:
                if gmin < xmin:
                    xmin = gmin
        return xmin
    
    def GetMax(self, coordinate):
        """
        Determine maximum for a given coordinate for all datatypes.
        
        :param coordinate: Coordinate (X or Y)
        :type coordinate: str
        :return: Max. value of all data types
        :rtype: float
        """
        xmin = 0
        initialised = False
        for graph in self.__datapoints.values():
            gmin = self.__GetGraphLimit(coordinate, "MAX", graph)
            if not initialised:
                xmin = gmin
                initialised = True
            else:
                if gmin > xmin:
                    xmin = gmin
        return xmin
    
    
    def __GetGraphLimit(self, coordinate, direction, graph):
        """
        Determine extremum (MIN or MAX) for a given graph in a given coordinate
        
        :param coordinate: coordinate to check
        :type coordinate: str
        :param direction: direction (MIN or MAX) to check
        :type direction: str
        :param graph: graph to check
        :type graph: TGraph
        :return: the extremum of the graph in a given coordinate
        :rtype: float
        """
        mylimit = 0
        isinitialised = 0
        for point in range(0, graph.GetN()):
            value = graph.GetX()[point] if coordinate == "X" else graph.GetY()[point]
            if not isinitialised:
                mylimit = value
                isinitialised = True
            else:
                if direction == "MIN" and value < mylimit:
                    mylimit = value
                elif direction == "MAX" and value > mylimit:
                    mylimit = value
        return mylimit