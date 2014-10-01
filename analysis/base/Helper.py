#! /usr/bin/env python
#
# Helper tools for spectrum plotting
#
#    Author: Markus Fasel
#

from ROOT import TFile, TGraphErrors, gDirectory
from copy import deepcopy
from base.MonteCarloFileHandler import MonteCarloFileMerger

def MergePtHardBins(outputfile, basedir, firstbin, lastbin):
    """
    Merge files from different pt-hard bins, weighted by the cross section, into one file
    """
    merger = MonteCarloFileMerger()
    for pthardbin in range(firstbin, lastbin+1):
        merger.AddFile("%s/%02d/AnalysisResults.root" %(basedir, pthardbin), pthardbin)
    merger.MergeAndWrite(outputfile)

def NormaliseBinWidth(hist):
    """
    Normalise each bin by its width
    """
    for mybin in range(1,hist.GetXaxis().GetNbins()):
        bw = hist.GetXaxis().GetBinWidth(mybin)
        hist.SetBinContent(mybin, hist.GetBinContent(mybin)/bw)
        hist.SetBinError(mybin, hist.GetBinError(mybin)/bw)

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
    for mybin in range(1, hist.GetXaxis().GetNbins()+1):
        if xmin and hist.GetXaxis().GetBinLowEdge(mybin) < xmin:
            continue
        if xmax and hist.GetXaxis().GetBinLowEdge(mybin) > xmax:
            break
        output.SetPoint(npoints, hist.GetXaxis().GetBinCenter(mybin), hist.GetBinContent(mybin))
        output.SetPointError(npoints, hist.GetXaxis().GetBinWidth(mybin)/2., hist.GetBinError(mybin))
        npoints = npoints + 1
    return output
