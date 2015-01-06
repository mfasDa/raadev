'''
Created on Jan 5, 2015

Handling of jet-dependenet histograms in the analysis framework

@author: markus
'''

from base.SpectrumContainer import SpectrumContainer
from base.Helper import NormaliseBinWidth

class JetPtBin():
    
    def __init__(self, jetpt):
        self.__jetpt = jetpt
        self.__spectrum = None
        self.__spectrumTrue = None
        
    def SetRecSpectrum(self, spec):
        self.__spectrum = SpectrumContainer(spec)
        
    def SetMCKineSpectrum(self, spec):
        self.__spectrumTrue = SpectrumContainer(spec)
         
    def GetJetPt(self):
        return self.__jetpt
    
    def GetRecSpectrum(self):
        return self.__spectrum
    
    def GetMCKineSpectrum(self):
        return self.__spectrumTrue
    
    def SetVertexRange(self, vtxmin, vtxmax):
        if self.__spectrum:
            self.__spectrum.ApplyCut(4, vtxmin, vtxmax)
        if self.__spectrumTrue:
            self.__spectrumTrue.ApplyCut(4, vtxmin, vtxmax)
    
    def SetMinJetPt(self, minpt):
        if self.__spectrum:
            self.__spectrum.ApplyCut(1, minpt, 1000.)
        if self.__spectrumTrue:
            self.__spectrumTrue.ApplyCut(1, minpt, 1000.)
    
    def SetEtaRange(self, etamin, etamax):
        if self.__spectrum:
            self.__spectrum.ApplyCut(2, etamin, etamax)
        if self.__spectrumTrue:
            self.__spectrumTrue.ApplyCut(2, etamin, etamax)
            
    def SetPhiRange(self, phimin, phimax):
        if self.__spectrum:
            self.__spectrum.ApplyCut(3, phimin, phimax)
        if self.__spectrumTrue:
            self.__spectrumTrue.ApplyCut(3, phimin, phimax)
    
    def SetSeenInMinBias(self):
        if self.__spectrum:
            self.__spectrum.ApplyCut(5, 1, 1)
        if self.__spectrumTrue:
            self.__spectrumTrue.ApplyCut(5, 1, 1)
            
    def GetProjectedRecSpectrum(self, dim, name, doNormBW = False):
        projected = self.__spectrum.ProjectToDimension(dim, name, "", "")
        if doNormBW:
            NormaliseBinWidth(projected)
        return projected
        
    def GetProjectedMCKineSpectrum(self, dim, name, doNormBW = False):
        projected = self.__spectrumTrue.ProjectToDimension(dim, name, "", "")
        if doNormBW:
            NormaliseBinWidth(projected)
        return projected
        
class JetContainer(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__jetpts =  []
        self.__vertexrange = {"min":None, "max":None}
        self.__eventhist = None
        
    def SetEventHist(self, hist):
        self.__eventhist = hist
        
    def AddJetPt(self, jetpt):
        existing = self.FindJetPt(jetpt)
        if not existing:
            self.__jetpts.append(JetPtBin(jetpt))
        
    def SetJetPtHist(self, jetpt, spec, isTrueKine):
        existing = self.FindJetPt(jetpt)
        if not existing:
            existing = JetPtBin(jetpt)
        if isTrueKine:
            existing.SetMCKineSpectrum(spec)
        else:
            existing.SetRecSpectrum(spec)
            
    def FindJetPt(self, jetpt):
        found =  None 
        for entry in self.__jetpts:
            if entry.GetJetPt() == jetpt:
                found = entry
                break
        return found

    def SetVertexRange(self, vtxmin, vtxmax):
        self.__vertexrange["min"] = vtxmin
        self.__vertexrange["max"] = vtxmax
        for entry in self.__jetpts:
            entry.SetVertexRange(vtxmin, vtxmax)
        
    def SetEtaRange(self, etamin, etamax):
        for entry in self.__jetpts:
            entry.SetEtaRange(etamin, etamax)
            
    def SetPhiRange(self, phimin, phimax):
        for entry in self.__jetpts:
            entry.SetPhiRange(phimin, phimax)
            
    def SetRequestSeenInMinBias(self):
        for entry in self.__jetpts:
            entry.SetRequestSeenInMinBias()
            
    def GetEventCount(self):
        pass
            
    def MakeProjectionRec(self, jetpt, dimension, name, doNorm = False):
        existing = self.FindJetPt(jetpt)
        if not existing:
            return None
        projected = existing.GetProjectedRecSpectrum(dimension, name, doNorm)
        if projected and doNorm:
            projected.Scale(1./self.GetEventCount())
        return projected