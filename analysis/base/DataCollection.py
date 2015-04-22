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
Utility classes for datapoints and converters to ROOT graphics objects

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""

from ROOT import TGraph, TGraphAsymmErrors
import math

class Datapoint(object):
    """
    Representation of data for a single point
    """
    
    def __init__(self, x, y, dx):
        """
        Constructor
        
        :param x: x-coordinate
        :type x: float
        :param y: y-coordinate
        :type y: float
        :param dx: uncertainty in y-direction
        :type dx: float
        """
        self.__x = x
        self.__y = y
        self.__dx = dx
        self.__upperErrors = {}
        self.__lowerErrors = {}
        
    def AddErrorSource(self, name, lower, upper):
        """
        Add error to the datapoint
        
        :param name: name of the error source
        :type name: str
        :param lower: lower value of the uncertainty in y-direction
        :type lower: float
        :param upper: upper value of the uncertainty in y-direction
        :type upper: float
        """
        self.__upperErrors[name] = upper
        self.__lowerErrors[name] = lower
        
    def GetX(self):
        """
        Access to x-value of the data point
        
        :return: x-coordinate
        :rtype: float
        """
        return self.__x
        
    def GetY(self):
        """
        Access to y-value of the data point

        :return: y-coordinate
        :rtype: float
        """
        return self.__y
     
    def GetLowerErrorForSource(self, name):
        """
        Access to lower error for a given error source
        
        :param name: name of the error source
        :type name: str
        :return: lower error for the source
        :rtype: float
        """
        if name == "total":
            return self.GetTotalLowerError()
        if not name in self.__lowerErrors.keys():
            return 0
        return self.__lowerErrors[name]
    
    def GetUpperErrorForSource(self, name):
        """
        Access to upper error for a given error source
        
        :param name: name of the error source
        :type name: str
        :return: upper error for the source
        :rtype: float
        """
        if name == "total":
            return self.GetTotalUpperError()
        if not name in self.__upperErrors.keys():
            return 0
        return self.__upperErrors[name]
    
    def GetUpperLimitForSource(self, source):
        """
        Access to upper limit under a given error source
        
        :param source: name of the error source
        :type source: str
        :return: upper limit
        :rtype: float
        """
        return self.__y + self.GetUpperErrorForSource(source)
    
    def GetLowerLimitForSource(self, source):
        """
        Access to lower limit under a given error source
        
        :param source: name of the error source
        :type source: str
        :return: lower limit
        :rtype: float
        """
        return self.__y - self.GetLowerErrorForSource(source)

    def GetRelativeLowerError(self, source):
        """
        Get the lower uncertainty relative to the y value
        
        :param source: name of the error source
        :type source: str
        :return: relative lower error
        :rtype: float
        """
        return self.GetLowerErrorForSource(source)/self.__y
    
    def GetRelativeUpperError(self, source):
        """
        Get the lower uncertainty relative to the y value
        
        :param source: name of the error source
        :type source: str
        :return: relative upper error
        :rtype: float
        """
        return self.GetUpperErrorForSource(source)/self.__y
             
    def GetDX(self):
        """
        Access to uncertainty in x direction
        
        :return: uncertainty in x-direction
        :rtype: float
        """
        return self.__dx
        
    def GetTotalLowerError(self):
        """
        calculate total error as quadratic sum of the single components
        
        :return: total lower limit
        :rtype: float
        """
        sumofsquares = 0
        for error in self.__lowerErrors.values():
            sumofsquares += math.pow(error, 2)
        return math.sqrt(sumofsquares)

    def GetTotalUpperError(self):
        """
        calculate total error as quadratic sum of the single components
        
        :return: total upper limit
        :rtype: float
        """
        sumofsquares = 0
        for error in self.__lowerErrors.values():
            sumofsquares += math.pow(error, 2)
        return math.sqrt(sumofsquares)
     
    def __eq__(self, other):
        return self.__x == other.__x
        
    def __lt__(self, other):
        return self.__x < other.__x
        
    def __le__(self, other):
        return self.__x <= other.__x
        
    def __gt__(self, other):
        return self.__x > other.__x
        
    def __ge__(self, other):
        return self.__x >= other.__x
        
    def __ne__(self, other):
        return self.__x != other.x
    
    def __str__(self):
        """
        Create string representation of the point
        
        :return: string representation
        :rtype: str
        """
        result = "%f +- %f GeV/c: %e" %(self.__x, self.__dx, self.__y)
        for source in self.__lowerErrors.keys():
            result += " + %e - %e (%s)" %(self.__upperErrors[source], self.__lowerErrors[source], source)
        if len(self.__lowerErrors):
            result += " [+ %e -%e (total)]" %(self.GetTotalUpperError(), self.GetTotalLowerError())
        return result

    def Print(self):
        """
        Print point representation
        """
        print str(self)

class DataCollection(object):
    """
    Collection of data points
    """

    def __init__(self, name):
        """
        Constructor
        
        :param name: name of the data collection
        :type name: str
        """
        self.__name = name
        self._pointlist = []
        
    def AddDataPoint(self, point):
        """
        Add a new data point to the data collection
        
        :param point: point to be added
        :type point: DataPoint
        """
        self._pointlist.append(point)
        
    def AddDataXY(self, x, y):
        """
        Add data point (without error) to the data collection
        
        :param x: x-coordinate
        :type x: float
        :param y: y-coordinate
        :type y: float
        """
        self._pointlist.append(Datapoint(x, y, 0.))
        
    def AddDataWithErrors(self, x, y, dx, dy):
        """
        Add data point with symmetrical error to the data collection
        """
        point = Datapoint(x,y,dx),
        point.AddErrorSource("error", dy, dy)
        self._pointlist.append(point)
        
    def GetPointList(self):
        """
        Get list of data points
        
        :return: list of data points
        :rtype: list
        """
        return self._pointlist
    
    def MakeErrorGraphForSource(self, source):
        """
        Create a graph for a given error source
        
        :param source: name of the error source
        :type source: str
        :return: Graph for the error source
        :rtype: TGraphAsymmErrors
        """
        result = TGraphAsymmErrors()
        counter = 0 
        for point in sorted(self._pointlist):
            result.SetPoint(counter, point.GetX(), point.GetY())
            result.SetPointError(counter, point.GetDX(), point.GetDX(), point.GetLowerErrorForSource(source), point.GetUpperErrorForSource(source))
            counter += 1
        return result
    
    def MakeLimitCurve(self, source, direction):
        """
        Make curve with upper limit for a given error source in a certain direction
        
        :param source: name of the error source
        :type source: str
        :param direction: upper or lower
        :type direction: str
        :return: Graph with limits
        :rtype: TGraph
        """
        result = TGraph()
        counter = 0
        for point in self._pointlist:
            error = 0
            if direction == "upper":
                error = point.GetUpperErrorForSource(source)
            elif direction == "lower":
                error = -1. * point.GetLowerErrorForSource(source)
            elif direction == "cental":
                error = 0
            result.SetPoint(counter, point.GetX(), point.GetY() + error)
            counter += 1
        return result

    def Print(self):
        """
        Print the data collection
        """
        print "Data collection :s" %(self.__name)
        print "====================================================================="
        for point in sorted(self._pointlist):
            point.Print()
