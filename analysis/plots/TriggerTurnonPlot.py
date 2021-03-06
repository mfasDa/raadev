'''
Created on 18.09.2014

@author: markusfasel
'''

from base.Graphics import SinglePanelPlot,GraphicsObject,Frame
from ROOT import TFile
    
class TriggerTurnonPlot(SinglePanelPlot):
    
    class TriggerDataContainer():
    
        class StyledObject:
        
            def __init__(self, data, style):
                self.__data = data
                self.__style = style
            
            def SetData(self, data):
                self.__data = data
            
            def GetData(self):
                return self.__data
        
            def SetStyle(self, style):
                self.__style = style
            
            def GetStyle(self):
                return self.__style
        
            def MakeGraphicsObject(self):
                return GraphicsObject(self.__data.GetPoints(), self.__style)
    
        def __init__(self):
            self.__data = {}
        
        def AddData(self, name, data, style):
            self.__data[name] = self.StyledObject(data, style)
        
        def SetStyle(self, name, style):
            self.__data[name].SetStyle(style)
        
        def GetGraphicsList(self):
            graphicsList = {}
            for entry in sorted(self.__data.keys()):
                graphicsList[entry] = self.__data[entry].MakeGraphicsObject()
            return graphicsList
            
        def DrawAll(self, frame):
            graphicsList = self.GetGraphicsList()
            for entry in sorted(graphicsList):
                print "Drawing %s" %(entry)
                frame.DrawGraphicsObject(graphicsList[entry], addToLegend = True, title = entry)
                    
        def Write(self, filename):
            outputfile = TFile(filename, "RECREATE")
            outputfile.cd()
            for trigger in sorted(self.__data.keys()):
                self.__data[trigger].GetData().WriteData(trigger)
                outputfile.Close()

    def __init__(self):
        SinglePanelPlot.__init__(self)
        self.__data = self.TriggerDataContainer()
        
    def AddData(self, trigger, turnonCurve, style):
        self.__data.AddData(trigger, turnonCurve, style)
        
    def Create(self):
        self._OpenCanvas("EMCalTurnon", "EMCal Turn-on curve")
        frame = Frame("emcturnon", 0., 100., 0., 3000.)
        frame.SetXtitle("p_{t} (GeV/c)")
        frame.SetYtitle("Trigger enhancement")
        pad = self._GetFramedPad()
        pad.DrawFrame(frame)
        self.__data.DrawAll(pad)
        pad.CreateLegend(0.55, 0.67, 0.89, 0.89)
            
    def GetData(self):
        return self.__data
    
    def WriteData(self, filename):
        self.__data.Write(filename)