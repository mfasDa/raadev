"""
Created on 02.10.2014

@author: markusfasel
"""

from base.Graphics import GraphicsObject

class ComparisonObject(object):
    """
    Base entry type for object inside comparison data
    """
    
    def __init__(self, data, style):
        self.__data = data
        self.__style = style
        
    def GetData(self):
        return self.__data
        
    def GetGraphicsObject(self):
        return GraphicsObject(self.__data, self.__style)
    
    def GetRootPrimitive(self):
        self.__data.SetName(self.GetObjectName())
        return self.__data
    
    def Draw(self, pad, addToLegend = True):
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


    def __init__(self, params):
        """
        Constructor
        """
        self.__entries = []
        
    def AddEntry(self, entry):
        self.__entries.append(entry)
        
    def DrawObjects(self, pad, addToLegend = True):
        for entry in self.__entries:
            entry.Draw(pad, addToLegend)
            
    def GetListOfRootObjects(self):
        """
        Get a list of root-primitive trigger efficiencies
        """
        rootprimitives = []
        for entry in self.__trefficiencies:
            rootprimitives.append(entry.GetRootPrimitive())
        return rootprimitives