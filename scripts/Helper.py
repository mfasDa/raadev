#! /usr/bin/env python
#
# Helper tools for spectrum plotting
#
#    Author: Markus Fasel
#

from ROOT import TFile, TH1F, TGraphErrors, gDirectory
from copy import deepcopy

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
            

def NormaliseBinWidth(hist):
        """
        Normalise each bin by its width
        """
        for mybin in range(1,hist.GetXaxis().GetNbins()):
                bw = hist.GetXaxis().GetBinWidth(mybin)
                hist.SetBinContent(mybin, hist.GetBinContent(mybin)/bw)
                hist.SetBinError(mybin, hist.GetBinError(mybin)/bw)

def ReadHistList(filename, directory = None):
    """
    Read the list of histograms from a given rootfile
    optionally the list can be wihtin a directory (i.e. when analysing lego train output)
    """
    inputfile = TFile.Open(filename)
    if not inputfile or inputfile.IsZombie():
        raise FileReaderException(filename)
    mydirectory = None
    path = filename
    if directory:
        path += "#%s" %(directory)
        if not inputfile.cd("PtEMCalTriggerTask"):
            inputfile.Close()
            raise FileReaderException(path)
        else:
            mydirectory = gDirectory
    else:
        mydirectory = inputfile
        path += "#"
    rlist = mydirectory.Get("results")
    hlist = rlist.FindObject("histosPtEMCalTriggerHistograms")
    inputfile.Close()
    if not hlist:
        raise FileReaderException("%s/histosPtEMCalTriggerHistograms" %(path))
    return hlist
    
def MakeRatio(num, den, isBinomial = False):
    """
    Calculate ratio between 2 histograms
    Option indicates whether we use binomial error calculation or gaussian error calculation
    """
    result = deepcopy(num)
    option = ""
    if isBinomial:
        option = "B"
    result.Divide(num, den, 1., 1., option)
    return result

def HistToGraph(hist, xmin = None, xmax = None):
    output = TGraphErrors()
    npoints = 0
    for bin in range(1, hist.GetXaxis().GetNbins()+1):
        if xmin and hist.GetXaxis().GetBinLowEdge(bin) < xmin:
            continue
        if xmax and hist.GetXaxis().GetBinLowEdge(bin) > xmax:
            break
        output.SetPoint(npoints, hist.GetXaxis().GetBinCenter(bin), hist.GetBinContent(bin))
        output.SetPointError(npoints, hist.GetXaxis().GetBinWidth(bin)/2., hist.GetBinError(bin))
        npoints = npoints + 1
    return output
