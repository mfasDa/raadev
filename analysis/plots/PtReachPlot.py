'''
Created on 17.09.2014

@author: markusfasel
'''

from util.PtReachCalculation import PtReachCalculator
from base.DataCollection import DataCollection, Datapoint
from base.Graphics import SinglePanelPlot, Frame, GraphicsObject

class PtReachData:    
    
    class PtReachDataException(Exception):
        
        def __init__(self):
            pass
        
        def __str__(self):
            return "Pt reach not yet evaluated"
    
    def __init__(self, name, data, isMinBias):
        self.__calculator = PtReachCalculator(name, data, isMinBias, 50)
        self.__data = DataCollection()
        self.__isCreated = False
        
    def CreateData(self):
        events = [500000, 1000000, 20000000, 50000000, 100000000, 200000000, 300000000, 400000000, 500000000, 750000000, 1000000000]
        for nevents in events:
            self.__data.AddDataPoint(Datapoint(nevents, self.__calculator.GetPtReach(nevents)))
        self.__isCreated = True
            
    def MakeGraphics(self):
        if not self.__isCreated:
            raise self.PtReachDataException()
        return self.__data.MakeLimitCurve(None, diretion = "central")
    
class PtReachPlot(SinglePanelPlot):
    
    def __init__(self):
        SinglePanelPlot.__init__(self)
        self.__ptreachdata = {}
        
    def AddData(self, name, data, style):
        self.__ptreachdata[name] ={"data", "Style"}
        
    def Create(self):
        self._OpenCanvas("PtReachPlot", "Pt-reach depending on the number of events")
        
        pad = self._GetFramedPad()
        frame = Frame("framePtReach", 0., 1100000000, 0., 150)
        frame.SetXtitle("Number of events")
        frame.SetYtitle("Max. p_{t} (GeV/c)")
        pad.DrawFrame(frame)
        for key,data in self.__ptreachdata.iteritems():
            graphics = GraphicsObject(data["data"].MakeGraphics, data["style"])
            pad.DrawGraphicsObject(graphics, True, key , "p")
        pad.CreateLegend(0.5, 0.15, 0.35, 0.89)
        pad.DrawLabel(0.5, 0.37, 0.89, 0.46, "At least 50 tracks at p_{t}")
        
            