#! /usr/bin/env python

from ROOT import TCanvas,TF1,TFile,TLegend,TPaveText
from ROOT import kRed, kBlack, kBlue, kGreen, gROOT
from Helper import Style,Frame

class TurnonCurveContainer:
    
    def __init__(self):
        self.__data = {}
        self.__triggers = ["EMCJHigh","EMCJLow","EMCGHigh","EMCGLow"]
    
    def CreateFromFile(self, filename):
        rootfile = TFile.Open(filename)
        gROOT.cd()
        for trg in self.__triggers:
            self.__data[trg] = rootfile.Get("turnonCurve%s" %(trg)) 
        rootfile.Close()
        
    def GetCurveForTrigger(self, trigger):
        if not trigger in self.__triggers:
            return None
        return self.__data[trigger]
    
    def GetListOfTriggers(self):
        return self.__triggers
    
    def DrawTrigger(self, trigger):
        if trigger in self.__triggers:
            self.__data[trigger].Draw("epsame")
            
    def AddTriggerToLegend(self, trigger, legend, title = None):
        mytitle = trigger
        if title:
            mytitle = title
        if trigger in self.__triggers:
            legend.AddEntry(self.__data[trigger], mytitle, "lep")
        else:
            print "Trigger %s not found" %(trigger)
            
    def SetStyleForAll(self, style):
        for trigger in self.__triggers:
            self.SetTriggerStyle(trigger, style)
    
    def SetTriggerStyle(self, trigger, style):
        if trigger in self.__triggers:
            self.__data[trigger].SetMarkerColor(style.GetColor())
            self.__data[trigger].SetMarkerStyle(style.GetMarker())
            self.__data[trigger].SetLineColor(style.GetColor())
    
    def ExtractEnhancementFactorForTrigger(self, trigger):
        if not trigger in self.__triggers:
            return 0
        model = TF1("plateau", "pol0", 0, 100)
        self.__data[trigger].Fit("plateau", "N", "", 50., 90.)
        result = [model.GetParameter(0), model.GetParError(0)]
        return result
        
class DataPeriod:
    def __init__(self, name):
        self.__data = {}
        self.__name = name
        
    def LoadData(self, filename, fitmin):
        self.__data[fitmin] = TurnonCurveContainer()
        self.__data[fitmin].CreateFromFile(filename)
        
    def SetPeriodStyle(self, style):
        for en in self.__data.keys():
            self.__data[en].SetStyleForAll(style)
    
    def SetFitminStyle(self, fitmin, style):
        if fitmin in self.__data.keys():
            self.__data[fitmin].SetStyleForAll(style)
            
    def GetFitMinima(self):
        return self.__data.keys()
            
    def GetListOfTriggers(self):
        return self.__data[self.__data.keys()[0]].GetListOfTriggers()
    
    def CalculateEnhancementFactor(self, fitmin, trigger):
        if fitmin in self.__data.keys():
            return self.__data[fitmin].ExtractEnhancementFactorForTrigger(trigger)
        return None
            
    def DrawCurve(self, fitmin, trigger):
        if fitmin in self.__data.keys():
            self.__data[fitmin].DrawTrigger(trigger)
    
    def AddCurveToLegend(self, fitmin, trigger, legend, title = None):
        if fitmin in self.__data.keys():
            self.__data[fitmin].AddTriggerToLegend(trigger, legend, title)

class FourPanelPlot:
    
    class FramedPad:
        def __init__(self, pad):
            self.__pad = pad
            self.__Frame = None
            self.__legend = None
            self.__labels = []
            
        def DrawFrame(self, frame):
            self.__frame = frame
            self.__frame.Draw()
            
        def DefineLegend(self, xmin, ymin, xmax, ymax):
            self.__legend = TLegend(xmin, ymin, xmax, ymax)
            self.__legend.SetBorderSize(0)
            self.__legend.SetFillStyle(0)
            self.__legend.SetTextFont(42)
            
        def GetLegend(self):
            return self.__legend
        
        def DrawLegend(self):
            if self.__legend:
                self.__legend.Draw()
        
        def DrawLabel(self, xmin, ymin, xmax, ymax, text):
            label = TPaveText(xmin, ymin, xmax, ymax, "NDC")
            label.SetBorderSize(0)
            label.SetFillStyle(0)
            label.SetTextFont(42)
            label.AddText(text)
            label.Draw()
            self.__labels.append(label)
    
    def __init__(self):
        self._canvas = None
        self._framedPads = {1:None, 2:None, 3:None, 4:None}
        
    def _OpenCanvas(self, canvasname, canvastitle):
        self._canvas = TCanvas(canvasname, canvastitle, 1000, 800)
        self._canvas.Divide(2,2)
        
    def _OpenPad(self, id):
        if id >= 1 and id <= 4:
            pad = self._canvas.cd(id)
            pad.SetGrid(False, False)
            self._framedPads[id] = self.FramedPad(pad)
            return self._framedPads[id]
        return None
    
    def SaveAs(self, filenamebase):
        types = ["eps", "pdf", "jpeg", "gif", "png"]
        for t in types:
            self._canvas.SaveAs("%s.%s" %(filenamebase, t))

class PeriodComparisonPlot(FourPanelPlot):
    
    def __init__(self):
        FourPanelPlot.__init__(self)
        self.__data = {}
        self.__fit = 15
        
    def AddPeriod(self, name, periodObject):
        self.__data[name] = periodObject
        
    def SetFitMin(self, fitmin):
        self.__fit = fitmin
        
    def Create(self):
        triggers = self.__data[self.__data.keys()[0]].GetListOfTriggers()
        self._OpenCanvas("periodComparisonPlot", "Compare turn-on curve for different periods")
        
        for pad in range(1, 5):
            mypad = self._OpenPad(pad)
            frame = Frame("axis%s" %(triggers[pad-1]), 0., 100., 0., 2000.)
            frame.SetXtitle("p_{t} (GeV/c)")
            frame.SetYtitle("Triggered / Min. bias")
            mypad.DrawFrame(frame)
            mypad.DrawLabel(0.15, 0.82, 0.35, 0.89, "Trigger: %s" %(triggers[pad-1]))
            if pad == 1:
                mypad.DefineLegend(0.5, 0.15, 0.89, 0.35)
            for period in sorted(self.__data.keys()):
                self.__data[period].DrawCurve(self.__fit, triggers[pad-1])
                if pad == 1:
                    self.__data[period].AddCurveToLegend(self.__fit, triggers[pad-1], mypad.GetLegend(), period)
                print "Trigger: %s" %(triggers[pad-1])
                enhancementfactor = self.__data[period].CalculateEnhancementFactor(self.__fit, triggers[pad-1])
                print "%s: %.2f +- %.2f" %(period, enhancementfactor[0], enhancementfactor[1])
            if pad == 1:
                mypad.DrawLegend()
        self._canvas.cd()        

class FitComparisonPlot(FourPanelPlot):
    
    def __init__(self, data):
        FourPanelPlot.__init__(self)
        self.__data = data
        
    def Create(self):
        triggers = self.__data.GetListOfTriggers()
        self._OpenCanvas("fitminComparisonPlot", "Compare turn-on curve for different fit minima")
        
        for pad in range(1, 5):
            mypad = self._OpenPad(pad)
            frame = Frame("axis%s" %(triggers[pad-1]), 0., 100., 0., 2000.)
            frame.SetXtitle("p_{t} (GeV/c)")
            frame.SetYtitle("Triggered / Min. bias")
            mypad.DrawFrame(frame)
            mypad.DrawLabel(0.15, 0.82, 0.35, 0.89, "Trigger: %s" %(triggers[pad-1]))
            if pad == 1:
                mypad.DefineLegend(0.5, 0.15, 0.89, 0.35)
            for fitmin in sorted(self.__data.GetFitMinima()):
                self.__data.DrawCurve(fitmin, triggers[pad-1])
                if pad == 1:
                    self.__data.AddCurveToLegend(fitmin, triggers[pad-1], mypad.GetLegend(), "%i GeV/c" %(fitmin))
                print "Trigger: %s" %(triggers[pad-1])
                enhancementfactor = self.__data.CalculateEnhancementFactor(fitmin, triggers[pad-1])
                print "%s: %.2f +- %.2f" %(fitmin, enhancementfactor[0], enhancementfactor[1])
            if pad == 1:
                mypad.DrawLegend()
        self._canvas.cd()        

def MakePeriodComparisonPlot(periods, styles):
    plot = PeriodComparisonPlot()
    for period in periods.keys():
        myperiod = DataPeriod(period)
        myperiod.LoadData(periods[period], 15)
        myperiod.SetPeriodStyle(styles[period])
        plot.AddPeriod(period, myperiod)
    plot.Create()
    return plot

def MakeFitComparisonPlot(filenames, styles):
    data = DataPeriod("all")
    for min in filenames.keys():
        data.LoadData(filenames[min], min)
        data.SetFitminStyle(min, styles[min])
    plot = FitComparisonPlot(data)
    plot.Create()
    return plot

def MyPeriodComparisonPlot():
    periods = {"LHC13d":"LHC13d/Turnon_fit15.root","LHC13e":"LHC13e/Turnon_fit15.root","merged":"merged/Turnon_fit15.root"}
    styles = {"LHC13d":Style(kRed,24), "LHC13e":Style(kBlue,25), "merged":Style(kBlack,26)}
    return MakePeriodComparisonPlot(periods, styles)

def MyFitComparisonPlot():
    fits={i:"Turnon_fit%d.root" %(i) for i in range(10, 30, 5)}
    colors=[kRed, kBlue, kBlack, kGreen]
    styles={i:Style(colors[(i-10)/5], 24+(i-10)/5) for i in range(10, 30, 5)}
    return MakeFitComparisonPlot(fits, styles)
        