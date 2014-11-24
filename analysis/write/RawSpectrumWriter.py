'''
Created on 14.11.2014

@author: markusfasel
'''
from base.FileHandler import LegoTrainFileReader
from base.SpectrumFitter import MinBiasFitter
from ROOT import TList, TFile, TObject

class RawSpectrumWriter(object):
    
    def __init__(self):
        self.__categories = {"Full":{}, "EMCAL":{}}
        
    def AddTriggerToCategory(self, category, trigger, spectrum):
        self.__categories[category][trigger] = spectrum
        
    def Process(self, filename):
        reader = LegoTrainFileReader(filename)
        results = reader.ReadFile()
        categories = {"Full":"tracksAll", "EMCAL":"tracksWithClusters"}
        
        for trigger in ["MinBias", "EMCJHigh", "EMCJLow", "EMCGHigh", "EMCGLow"]:
            data = results.GetData(trigger)
            for stype,cont in categories.iteritems():
                spectrum = self.MakeNormalisedSpectrum(data.FindTrackContainer(cont), trigger, stype)
                self.AddTriggerToCategory(stype, trigger, spectrum)
                if trigger == "MinBias":
                    self.AddTriggerToCategory(stype, "MinBiasFit", self.FitMinBias(spectrum, stype))
                
    def FitMinBias(self, spectrum, category):
        fitter = MinBiasFitter("mbfitter", spectrum)
        param = fitter.MakeBinnedParameterisationDefault(True)
        param.SetName("FitMinBias%s" %(category)) 
        return param
                
    def MakeNormalisedSpectrum(self, spectrum, trigger, category):
        spectrum.SetVertexRange(-10., 10.)
        spectrum.SetPileupRejection(True)
        spectrum.SelectTrackCuts(1)
        return spectrum.MakeProjection(0, "RawSpectrum%s%s" %(trigger, category))
    
    def WriteToFile(self, outputname):
        outputlists = []
        for categ in self.__categories.keys():
            mylist = TList()
            mylist.SetName(categ)
            for entry in self.__categories[categ].itervalues():
                mylist.Add(entry)
            outputlists.append(mylist)
            
        outputfile = TFile(outputname, "RECREATE")
        outputfile.cd()
        for myobject in outputlists:
            myobject.Write(myobject.GetName(), TObject.kSingleKey)
        outputfile.Close()
        
def Create(filename):
    writer = RawSpectrumWriter()
    writer.Process(filename)
    writer.WriteToFile("normspectra.root")