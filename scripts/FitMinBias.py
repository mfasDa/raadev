#! /usr/bin/env python

from ROOT import TGraphErrors, TCanvas, TF1, TLegend, TMath, TPaveText, kRed, kBlue, kBlack
from copy import deepcopy
from Helper import Style, Frame, ReadHistList
from SpectrumContainer import DataContainer

class ComparisonPlot:
    def __init__(self, comparison):
        self.__comparison =  comparison
        self.__canvas = None
        self.__Frames = {}
        self.__legend = None
        self.__tag = None
        
    def SetTag(self, tagText):
        self.__tag = TPaveText(0.55, 0.8, 0.89, 0.88, "NDC")
        self.__tag.SetBorderSize(0)
        self.__tag.SetFillStyle(0)
        self.__tag.SetTextFont(42)
        self.__tag.AddText(tagText)
        
    def Create(self):
        self.__canvas = TCanvas("comparison", "Comparison Data/Fit", 1000, 550)
        self.__canvas.Divide(2,1)
        
        self.__legend = TLegend(0.15, 0.15, 0.35, 0.22)
        self.__legend.SetBorderSize(0)
        self.__legend.SetFillStyle(0)
        self.__legend.SetTextFont(42)
        
        spad = self.__canvas.cd(1)
        spad.SetGrid(False, False)
        spad.SetLogy(True)
        spad.SetLogx(True)
        self.__Frames["specframe"] = Frame("specframe", 0, 100, 1e-10, 100)
        self.__Frames["specframe"].SetXtitle("p_{t} (GeV/c)")
        self.__Frames["specframe"].SetYtitle("1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})")
        self.__Frames["specframe"].Draw()
        self.__comparison.DrawSpectra()
        self.__comparison.FillLegend(self.__legend)
        self.__legend.Draw()
        if self.__tag:
            self.__tag.Draw()
        
        rpad = self.__canvas.cd(2)
        spad.SetGrid(False, False)
        self.__Frames["rframe"] = Frame("rframe", 0, 100, 0, 2)
        self.__Frames["rframe"].SetXtitle("p_{t} (GeV/c)")
        self.__Frames["rframe"].SetYtitle("Data/Patam")
        self.__Frames["rframe"].Draw()
        self.__comparison.DrawRatio()
        
        self.__canvas.cd()
        
    def SaveAs(self, filenamebase):
        """
        Save plot as image file
        """
        types = ["eps", "pdf", "jpeg", "gif", "png"]
        for t in types:
            self.__canvas.SaveAs("%s.%s" %(filenamebase, t))


class DataFitComparison:
    
    def __init__(self, data, parameterisation):
        self.__data = data
        self.__parameterised = self.__CreateBinnedParameterisation(parameterisation)
        self.__ratio = self.__CreateRatioDataParam()
        
        self.__xrange = {"min":None, "max":None}
        self.__graphs = {"Data" : None, "Param" : None, "Ratio" : None }
        self.__styles = {"Data" : Style(kRed, 24), "Param" : Style(kBlue, 25), "Ratio" : Style(kBlack, 20) }
        
    def SetStyle(self, type, style):
        if type in self.__styles.keys():
            self.__styles[type] = style
            
    def SetRange(self, min = None, max = None):
        self.__xrange["min"] = min
        self.__xrange["max"] = max
    
    def __CreateBinnedParameterisation(self, param):
        print "Called"
        parameterised = deepcopy(self.__data)
        for mybin in range(1, parameterised.GetXaxis().GetNbins()+1):
            parameterised.SetBinContent(mybin, \
                            self.__GetBinnedParameterisation(param, \
                                            parameterised.GetXaxis().GetBinLowEdge(mybin), \
                                            parameterised.GetXaxis().GetBinUpEdge(mybin)))
            parameterised.SetBinError(mybin, 0)
        return parameterised
            
    def DrawSpectra(self):
        self.__graphs["Data"] = self.__ConvertToGraph(self.__data)
        self.__graphs["Param"] = self.__ConvertToGraph(self.__parameterised)
        self.__DrawStyle(self.__graphs["Data"], self.__styles["Data"])
        self.__DrawStyle(self.__graphs["Param"], self.__styles["Param"])   
    
    def DrawRatio(self):
        self.__graphs["Ratio"] = self.__ConvertToGraph(self.__ratio)
        self.__DrawStyle(self.__graphs["Ratio"], self.__styles["Ratio"])
    
    def FillLegend(self, legend):
        legend.AddEntry(self.__graphs["Data"], "Data", "lep")
        legend.AddEntry(self.__graphs["Param"], "Param", "lep")
                        
    def __DrawStyle(self, data, style):
        data.SetMarkerColor(style.GetColor())
        data.SetLineColor(style.GetColor())
        data.SetMarkerStyle(style.GetMarker())
        data.Draw("epsame")
                
    def __CreateRatioDataParam(self):
        ratio = deepcopy(self.__data)
        ratio.Divide(self.__parameterised)
        return ratio
    
    def __GetBinnedParameterisation(self, mbparam, min, max):
        return mbparam.Integral(min, max)/TMath.Abs(max - min)
    
    def __ConvertToGraph(self, hist):
        output = TGraphErrors()
        npoints = 0
        for bin in range(1, hist.GetXaxis().GetNbins()+1):
            if self.__xrange["min"] and hist.GetXaxis().GetBinLowEdge(bin) < self.__xrange["min"]:
                continue
            if self.__xrange["max"] and hist.GetXaxis().GetBinLowEdge(bin) > self.__xrange["max"]:
                break
            output.SetPoint(npoints, hist.GetXaxis().GetBinCenter(bin), hist.GetBinContent(bin))
            output.SetPointError(npoints, hist.GetXaxis().GetBinWidth(bin)/2., hist.GetBinError(bin))
            npoints = npoints + 1
        return output

def ReadSpectra(filename):
    """
    Read the spectra for different trigger classes from the root file
    Returns a dictionary of triggers - spectrum container
    """
    triggers = ["MinBias", "EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]
    hlist = ReadHistList(filename, "PtEMCalTriggerTask")
    result = {}
    for trg in triggers:
        result[trg] = DataContainer(eventHist = hlist.FindObject("hEventHist%s" %(trg)), trackHist = hlist.FindObject("hTrackHist%s" %(trg)))
    return result

def MakeNormalisedSpectrum(inputdata, name):
    """
    Normalise spectrum by the number of events and by the bin width
    """
    inputdata.SetVertexRange(-10., 10.)
    inputdata.SetPileupRejection(True)
    inputdata.SelectTrackCuts(1)
    return inputdata.MakeProjection(0, "ptSpectrum%s" %(name), "p_{t} (GeV/c)", "1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})")

def ParameteriseMinBiasSpectrum(spectrum, range):
    """
    Parameterise fit function by power law
    """
    fitfunction = TF1("fitfunction", "[0] * TMath::Power(x,[1])", 0., 100.)
    spectrum.Fit("fitfunction", "N", "", range["min"], range["max"])
    return fitfunction

def CompareDataFit(filename, fitmin, fitmax):
    data = ReadSpectra(filename)
    mbspectrum = MakeNormalisedSpectrum(data["MinBias"], "MinBias")
    comparison = DataFitComparison(mbspectrum, ParameteriseMinBiasSpectrum(mbspectrum, {"min": fitmin, "max": fitmax}))
    comparison.SetRange(2., 100.)
    comparisonPlot = ComparisonPlot(comparison)
    comparisonPlot.SetTag("Fit range: %.1f - %.1f Gev/c" %(fitmin, fitmax))
    comparisonPlot.Create()
    return comparisonPlot
