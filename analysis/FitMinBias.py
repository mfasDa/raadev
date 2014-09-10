#! /usr/bin/env python

from ROOT import TGraphErrors, TCanvas, TF1, TLegend, TMath, TPaveText, kRed, kBlue, kBlack, kGreen
from copy import deepcopy
from Helper import ReadHistList, HistToGraph
from Graphics import Style, Frame
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

class MultipleFitPlot:
    
    def __init__(self):
        self.__data = {}
        self.__ratios = {}
        self.__reference = None
        
        self.__canvas = None
        self.__legend = None
        self.__Frames = {}
        self.__gRatios = {}
        
    def SetData(self, mycomp, fitmin, isReference):
        self.__data[fitmin] = mycomp
        if isReference:
            self.__reference = fitmin
            
    def RatiosToReference(self):
        for param in self.__data.keys():
            if param == self.__reference:
                continue
            self.__CalculateRatio(self.__data[param].GetRawParameterisation(), self.__data[self.__reference].GetRawParameterisation(), param)
    
    def Create(self):
        self.__canvas = TCanvas("comparisonFitRange", "Comparison of the fit ranges", 1000, 600)
        self.__canvas.Divide(2,1)

        self.__legend = TLegend(0.15, 0.15, 0.55, 0.35)
        self.__legend.SetBorderSize(0)
        self.__legend.SetFillStyle(0)
        self.__legend.SetTextFont(42)
        
        specpad = self.__canvas.cd(1)
        specpad.SetGrid(False, False)
        specpad.SetLogx(True)
        specpad.SetLogy(True)
        
        self.__Frames["specframe"] = Frame("specframe", 0, 100, 1e-10, 100)
        self.__Frames["specframe"].SetXtitle("p_{t} (GeV/c)")
        self.__Frames["specframe"].SetYtitle("1/N_{event} 1/(#Delta p_{t}) dN/dp_{t} ((GeV/c)^{-2})")
        self.__Frames["specframe"].Draw()
        
        for param in sorted(self.__data.keys()):
            self.__data[param].DrawBinnedParameterisation()
            self.__data[param].AddToLegend(self.__legend, "Param", "%.1f GeV/c - 50 GeV/c" %(param))
            
        self.__legend.Draw()      
        
        self.RatiosToReference()
        
        rpad = self.__canvas.cd(2)
        rpad.SetGrid(False, False)
        self.__Frames["rframe"] = Frame("rframe", 0, 100, 0.5, 1.5)
        self.__Frames["rframe"].SetXtitle("p_{t} (GeV/c)")
        self.__Frames["rframe"].SetYtitle("Ratio to %.1f GeV/c - 50 GeV/c" %(self.__reference))
        self.__Frames["rframe"].Draw()
        for ratio in sorted(self.__ratios.keys()):
            self.__DrawRatioGraph(ratio, self.__data[ratio].GetStyle("Param"), self.__data[ratio].GetXrange())
        self.__canvas.cd()

    def SaveAs(self, filenamebase):
        """
        Save plot as image file
        """
        types = ["eps", "pdf", "jpeg", "gif", "png"]
        for t in types:
            self.__canvas.SaveAs("%s.%s" %(filenamebase, t))
        
    def __DrawRatioGraph(self, param, style, range = None):
        xmin = None
        xmax = None
        if range:
            xmin = range["min"]
            xmax = range["max"]
        self.__gRatios[param] = HistToGraph(self.__ratios[param], xmin, xmax)
        self.__gRatios[param].SetMarkerColor(style.GetColor())
        self.__gRatios[param].SetMarkerStyle(style.GetMarker())
        self.__gRatios[param].SetLineColor(style.GetColor())
        self.__gRatios[param].Draw("epsame")
          
    def __CalculateRatio(self, num, den, tag):
        self.__ratios[tag] = deepcopy(num)
        self.__ratios[tag].Divide(den)

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
            
    def GetStyle(self, type):
        if not type in self.__styles.keys():
            return None
        return self.__styles[type]
            
    def SetRange(self, min = None, max = None):
        self.__xrange["min"] = min
        self.__xrange["max"] = max
        
    def GetXrange(self):
        return self.__xrange
    
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
    
    def GetRawSpectrum(self):
        return self.__data
    
    def GetRawParameterisation(self):
        return self.__parameterised
            
    def DrawSpectra(self):
        self.DrawSpectrum()
        self.DrawBinnedParameterisation()
        
    def DrawSpectrum(self):
        if not self.__graphs["Data"]:
            self.__graphs["Data"] = self.__ConvertToGraph(self.__data)
        self.__DrawStyle(self.__graphs["Data"], self.__styles["Data"])
    
    def DrawBinnedParameterisation(self):
        if not self.__graphs["Param"]:
            self.__graphs["Param"] = self.__ConvertToGraph(self.__parameterised)
        self.__DrawStyle(self.__graphs["Param"], self.__styles["Param"])   

    def AddToLegend(self, legend, what, title = None):
        object = None
        message = title
        if what == "Data":
            object = self.__graphs["Data"]
            if not message:
                message = "Data"
        elif what == "Param":
            object = self.__graphs["Param"]
            if not message:
                message = "Param"
        elif what =="Ratio":
            object = self.__graphs["Ratio"]
            if not message:
                message = "Ratio Data/Param"
        if object:
            legend.AddEntry(object, message, "lep")
    
    def DrawRatio(self):
        self.__graphs["Ratio"] = self.__ConvertToGraph(self.__ratio)
        self.__DrawStyle(self.__graphs["Ratio"], self.__styles["Ratio"])
    
    def FillLegend(self, legend):
        self.AddToLegend(legend, "Data")
        self.AddToLegend(legend, "Param")
                        
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
        return HistToGraph(hist, self.__xrange["min"], self.__xrange["max"])

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

def CheckFitRanges(filename):
    data = ReadSpectra(filename)
    mbspectrum = MakeNormalisedSpectrum(data["MinBias"], "MinBias")

    plot = MultipleFitPlot()
    styles = {10:Style(kBlue,24),15:Style(kBlack,25),20:Style(kRed,26),25:Style(kGreen,27)}
    for imin in range(10, 30, 5):
        comparison = DataFitComparison(mbspectrum, ParameteriseMinBiasSpectrum(mbspectrum, {"min": imin, "max": 50.}))
        comparison.SetRange(2., 100.)
        comparison.SetStyle("Param",styles[imin])
        isRef = False
        if imin == 15:
            isRef = True
        plot.SetData(comparison,imin,isRef)
    plot.Create()
    return plot