#! /usr/bin/python
#
# Helper tools for spectrum plotting
#
#    Author: Markus Fasel
#

class FileReaderException(Exception):
        """
        Exception class handling root files which are
        either not found or not readable.
        """

        def __init__(self, filename):
                """
                Constructor, assigning the name of the file which 
                failed to be read.
                """
                self.filename = filename

        def __str__(self):
                """
                Create string representation of the error message
                """
                return "Could not open file %s" %(self.filename)

class HistNotFoundException(Exception):
        """
        Exception class handles the case that a histogram
        is not found in the file / list
        """

        def __init__(self, histname):
                """
                Constructor, assigning the name of the histogram
                which was not found.
                """
                self.histname = histname

        def __str__(self):
                """
                Create string representation of the error message
                """
                return "Histogram %s not found" %(self.histname)

class Style:
        """ 
        Class for plot styles (currently only color and marker)
        """
        def __init__(self, color, marker):
                self.__color = color
                self.__marker = marker

        def SetColor(self, color):
                self.__color = color

        def SetMarker(self, marker):
                self.__marker = marker

        def GetColor(self):
                return self.__color

        def GetMarker(self):
                return self.__marker

def NormaliseBinWidth(hist):
        """
        Normalise each bin by its width
        """
        for mybin in range(1,hist.GetXaxis().GetNbins()):
                bw = hist.GetXaxis().GetBinWidth(mybin)
                hist.SetBinContent(mybin, hist.GetBinContent(mybin)/bw)
                hist.SetBinError(mybin, hist.GetBinError(mybin)/bw)
