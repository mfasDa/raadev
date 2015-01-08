'''
Created on Jan 8, 2015

@author: markus
'''

from copy import copy,deepcopy

class AxisFormat(object):
    
    def __init__(self, formatname):
        self._axes = {}
        self.__formatname = ""
        
    def GetAxes(self):
        return self._axes
    
    def FindAxis(self, axisname):
        result = -1
        if axisname in self._axes.keys():
            result = self._axes[axisname]
        return result
    
    def _Deepcopy(self, other, memo):
        self._axes = deepcopy(other.GetAxes(), memo)
       
    def _Copy(self, other):
        self._axes = copy(other.GetAxes()) 
        

class THnSparseCut(object):
    
    def __init__(self, axisname, minv, maxv):
        self.__axisname = axisname
        self.__minimum = minv
        self.__maximum = maxv
        
    def GetCutname(self):
        return self.__axisname
        
    def GetMinimum(self):
        return self.__minimum
    
    def GetMaximum(self):
        return self.__maximum
    
    def SetMinimum(self, minv):
        self.__minimum = minv
        
    def SetMaximum(self, maxv):
        self.__maximum = maxv

class THnSparseWrapper(object):
    
    def __init__(self, rootthnsparse):
        self._rootthnsparse = rootthnsparse
        self._axisdefinition = None
        self._cutlist = []
        
    def ApplyCut(self, axisname, minv, maxv):
        if not self._axisdefinition or self._axisdefinition.FindAxis(axisname) < 0:
            return
        existing = self.__FindCut(axisname)
        if not existing:
            self._cutlist.append(THnSparseCut(axisname, minv, maxv))
        else:
            existing.SetMinimum(minv)
            existing.SetMaximum(maxv)
        
    def ResetAxis(self, axisname):
        if not len(self._axisdefinition) or self._axisdefinition.FindAxis(axisname) < 0:
            return
        myaxis = self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis(axisname))
        myaxis.SetRange(0, myaxis.GetNbins()+1)
    
    def _PrepareProjection(self):
        for entry in self._cutlist:
            myaxis = self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis(entry.GetCutname()))
            minv = 0 if not entry.GetMinimum() else myaxis.FindBin(entry.GetMinimum())
            maxv = myaxis.GetNbins()+1 if not entry.GetMaximum() else myaxis.FindBin(entry.GetMaximum())
            myaxis.SetRange(minv, maxv)
            
    def _CleanumProjection(self):
        for entry in self._cutlist:
            self.ResetAxis(entry.GetCutname())

    def __FindCut(self, cutname):
        if not len(self._cutlist):
            return None
        result = None
        for entry in self._cutlist:
            if entry.GetCutname() == cutname:
                result = entry
                break
        return result