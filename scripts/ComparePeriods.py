#! /usr/bin/env python
import sys
from copy import deepcopy
from getopt import getopt,GetoptError
from ROOT import TCanvas,TFile,TH1F,TLegend,TPaveText
from ROOT import gROOT,kRed,kBlue,kBlack
from Helper import FileReaderException,HistNotFoundException,Style,NormaliseBinWidth

gObjects = list()

class ComparisonPlot:
    """
    Comparison plot of spectra from 2 periods
    """
    def __init__(self, spectruma, spectrumb):
        """
        Constructor, basic initialisation for the plot
        """
        # Data
        self.__spectrumA = spectruma
        self.__spectrumB = spectrumb
        self.__ratio = Ratio(self.__spectrumA, self.__spectrumB)
        self.__options = None
        
        # Graphics objects
        self.__comparisonPlot = None
        self.__axisspec = None
        self.__axisrat = None
        self.__legend = None
        self.__label = None
        
        # Titles and ranges (changable)
        self.__xtitle = self.__spectrumA.GetHistogram().GetXaxis().GetTitle()
        self.__ytitle = self.__spectrumA.GetHistogram().GetYaxis().GetTitle()
        self.__xrange = [self.__spectrumA.GetHistogram().GetXaxis().GetXmin(), self.__spectrumA.GetHistogram().GetXaxis().GetXmax()]
        self.__yrange = [min(self.__spectrumA.GetHistogram().GetMinimum(), self.__spectrumB.GetHistogram().GetMinimum()), \
                          max(self.__spectrumA.GetHistogram().GetMaximum(), self.__spectrumB.GetHistogram().GetMaximum())]
        self.__ratioyrange = [self.__ratio.GetRatioHist().GetMinimum(), self.__ratio.GetRatioHist().GetMaximum()]
        
    def SetXTitle(self, title):
        """
        Set title of the x-coordinate
        """
        self.__xtitle = title
        
    def SetYTitle(self, title):
        """
        Set title of the y-coordinate
        """
        self.__ytitle = title
        
    def SetXRange(self, xmin, xmax):
        """ 
        Set the plotting range in x-direction
        """
        self.__xrange[0] = xmin
        self.__xrange[1] = xmax
        
    def SetYRange(self, ymin, ymax):
        """
        Set the plotting range of the spectrum panel in y-direction
        """
        self.__yrange[0] = ymin
        self.__yrange[1] = ymax
        
    def SetYRangeRatio(self, ymin, ymax):
        """
        Set the plotting range of the spectrum panel in y-direction
        """
        self.__ratioyrange[0] = ymin
        self.__ratioyrange[1] = ymax
        
    def SetLabel(self, label):
        """
        Label left side of the plot
        label needs to be set from outside
        """
        self.__label = label
    
    def MakePlot(self):
        """
        Produce comparison plot
        Left panel: 2 spectra
        Right panel: ratio of the spectra
        """
        self.__comparisonPlot = TCanvas("comparisonPlot", "Comparison Periods", 1000, 400)
        self.__comparisonPlot.Divide(2,1)
        
        padspec = self.__comparisonPlot.cd(1)
        padspec.SetGrid(False, False)
        padspec.SetLogy()
        padspec.SetLogx()
        self.__legend = self.__CreateLegend(0.15, 0.15, 0.35, 0.25)
        self.__axisspec = TH1F("axisspec", ";%s;%s" %(self.__xtitle, self.__ytitle), 1000, self.__xrange[0], self.__xrange[1])
        self.__axisspec.SetStats(False)
        self.__axisspec.GetYaxis().SetRangeUser(self.__yrange[0], self.__yrange[1])
        self.__axisspec.Draw("axis")
        self.__spectrumA.Draw()
        self.__spectrumB.Draw()
        self.__AddToLegend(self.__spectrumA)
        self.__AddToLegend(self.__spectrumB)
        self.__legend.Draw()
        
        if self.__label:
            self.__label.Draw()
        
        padratio = self.__comparisonPlot.cd(2)
        padratio.SetGrid(False, False)
        padratio.SetLogx()
        self.__axisrat = TH1F("axirat", ";%s;%s" %(self.__xtitle, self.__ratio.GetRatioTitle()), 1000, self.__xrange[0], self.__xrange[1])
        self.__axisrat.SetStats(False)
        self.__axisrat.GetYaxis().SetRangeUser(self.__ratioyrange[0], self.__ratioyrange[1])
        self.__axisrat.Draw("axis")
        self.__ratio.Draw()
        self.__comparisonPlot.cd()
    
    def __CreateLegend(self, xmin, ymin, xmax, ymax):
        """
        Create a new legend within range defined by coordinates
        """
        leg = TLegend(xmin, ymin, xmax, ymax)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        return leg
    
    def __AddToLegend(self, spectrum):
        """
        Add spectrum object to legend
        """
        self.__legend.AddEntry(spectrum.GetHistogram(), spectrum.GetTitle(), "lep")
    
class Spectrum:
    """
    Helper class combining data of a graphics with a title and style information
    """
    def __init__(self, histogram, title, style = None):
        self.__histogram = histogram
        self.__title = title
        if style:
            self.SetStyle(style)
        else:
            self.SetStyle(Style(kBlack, 20))
        
    def GetHistogram(self):
        """
        Return Data of the spectrum
        """
        return self.__histogram
    
    def GetTitle(self):
        """
        Return title of the spectrum
        """
        return self.__title
    
    def SetHistogram(self, histogram):
        """
        Change the data of the spectrum
        """
        self.__histogram = histogram
        
    def SetTitle(self, title):
        """
        Change title of the spectrum
        """
        self.__title = title
    
    def SetStyle(self, style):
        """
        change style of the histogram
        """
        self.__histogram.SetMarkerColor(style.GetColor())
        self.__histogram.SetLineColor(style.GetColor())
        self.__histogram.SetMarkerStyle(style.GetMarker())
    
    def Draw(self):
        """
        Draw spectrum to a given Canvas
        """
        self.__histogram.Draw("epsame")

class Ratio:
    """
    Helper class creating ratio plots
    """
    def __init__(self, specnum, specden, useBinomial = False, style = None):
        self.__ratio = Spectrum(self.__calculateRatio(specnum, specden, useBinomial), "%s/%s" %(specnum.GetTitle(), specden.GetTitle()), style)
    
    def GetRatio(self):
        """
        Get the ratio result
        """
        return self.__ratio
    
    def GetRatioHist(self):
        """
        Return ratio underlying data
        """
        return self.__ratio.GetHistogram()
    
    def GetRatioTitle(self):
        """
        Return title of the ratio
        """
        return self.__ratio.GetTitle()
    
    def SetRatioTitle(self, title):
        """
        Change title of the ratio
        """
        self.__ratio.SetTitle(title)
    
    def SetStyle(self, style):
        """
        Change plotting style of the ratio hist
        """
        self.__ratio.SetStyle(style) 
        
    def Draw(self):
        """
        Draw ratio on a given canvas
        """
        self.__ratio.Draw()
        
    def __calculateRatio(self, specnum, specden, useBinomial = False):
        """ 
        Perform ratio calculation
        """
        result = deepcopy(specnum.GetHistogram())
        optstring = ""
        if useBinomial:
            optstring = "b"
        result.Divide(result, specden.GetHistogram(), 1., 1., optstring)
        return result
    
def ReadHistograms(filename, options):
        """
        Read histogram with input spectrum from file.
        """
        infile = TFile.Open(filename)
        if not infile or infile.IsZombie():
                raise FileReaderException(filename)
        myresultlist = infile.Get("results")
        histlist = myresultlist.FindObject("List of histograms of container PtEMCalTriggerHistograms")

        resultlist = dict()
        histos = {"EventCounter":"hEvents%s" %(options["trigger"]),\
                        "Spectrum":"hPt%s_%s_%s" %(options["trigger"], options["pileuprejection"], options["cuts"])}
        for key,hname in histos.iteritems():
                hist = histlist.FindObject(hname)
                if not hist:
                        raise HistNotFoundException(hname)
                else:
                        hist.SetDirectory(gROOT)
                        resultlist[key] = hist
        return resultlist
    
def MakeLabel(xmin, xmax, ymin, ymax, options):
    """
    Add label with trigger, cuts and pileup
    """
    lab = TPaveText(xmin, xmax, ymin, ymax, "NDC")
    lab.SetBorderSize(0)
    lab.SetFillStyle(0)
    lab.SetTextFont(42)
    lab.SetTextAlign(12)
    lab.AddText("Trigger: %s" %(options["trigger"]))
    lab.AddText("Cuts: %s" %(options["cuts"]))
    lab.AddText("Pileup rejection: %s" %(options["pileuprejection"]))
    return lab
    
def MakeNormalisedSpectrum(histos, options, name):
    """
    Normalise spectrum by the number of events and by the bin width
    """
    eventbin = 2
    if options["pileuprejection"] == "nopr":
        eventbin = 1
    spectrum = histos["Spectrum"].ProjectionY(name)
    spectrum.Sumw2()
    spectrum.Scale(1./histos["EventCounter"].GetBinContent(eventbin))
    NormaliseBinWidth(spectrum)
    return spectrum
    
def ComparePeriods(filea, fileb, arglist):
    
    try:
        opt,arg = getopt(arglist, "e:mns", ["emcal=", "minBias", "nnum=", "ndenom=", "nocut", "stdcut", "nopr", "withpr"])
    except GetoptError as e:
        print str(e)
        sys.exit(1)
     
    emctriggers = ["EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    options = {"trigger":"MinBias", "cuts":"stdcut", "pileuprejection":"wpr"}
    nameA = "numerator"
    nameB = "denominator"
    for o,a in opt:
        if o in ("-e", "--emcal"):
            mytrg = int(a)
            if not mytrg in range(1, 5):
                print "Trigger out of range"
                sys.exit(1)
            else:
                options["trigger"] = emctriggers[mytrg-1]
        elif o in ("-m", "--minbias"):
            options["trigger"] = "MinBias"
        elif o in ("-n", "--nocut"):
            options["cuts"] = "nocut"
        elif o in ("-s", "--stdcut"):
            options["cuts"] = "stdcut"
        elif o == "--nopr":
            options["pileuprejection"] = "nopr"
        elif o == "--withpr":
            options["pileuprejection"] ="wpr"
        elif o == "--nnum":
            nameA = str(a)
        elif o == "--ndenom":
            nameB = str(a)

    # Read spectra
    try:        
        dataA = ReadHistograms(filea, options)
    except FileReaderException as e:
        print str(e)
        sys.exit(1)
    except HistNotFoundException as e:
        print str(e)
        sys.exit(1)
    try:
        dataB = ReadHistograms(fileb, options)
    except FileReaderException as e:
        print str(e)
        sys.exit(1)
    except HistNotFoundException as e:
        print str(e)
        sys.exit(1)
        
    resultplot = ComparisonPlot(Spectrum(MakeNormalisedSpectrum(dataA, options, nameA), nameA, Style(kBlue, 24)), \
                                 Spectrum(MakeNormalisedSpectrum(dataB, options, nameB), nameB, Style(kRed, 25)))
    resultplot.SetXTitle("p_{t} (GeV/c)")
    resultplot.SetYTitle("1/N_{events} 1/#delta p_{T} dN/dp_{t} ((GeV/c)^{-2})")
    resultplot.SetYRange(1e-10, 100)
    resultplot.SetYRangeRatio(0., 3)
    resultplot.SetLabel(MakeLabel(0.5,0.7,0.89,0.85, options))
    resultplot.MakePlot()
    gObjects.append(resultplot)

def runComparison(filea, fileb, argstring):
    """
    Run program in interactive mode (with ipython)
    """
    arglist = argstring.split(" ")
    ComparePeriods(filea, fileb, arglist)

def main():
    """
    Run program in batch mode
    """
    if len(sys.argv < 3):
        print "At least 2 arguments required"
    pass

if __name__ == "__main__":
    main()