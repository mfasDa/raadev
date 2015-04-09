'''
Created on Apr 9, 2015

@author: markus
'''

from base.struct.THnSparseWrapper import THnSparseWrapper, AxisFormat
from copy import copy, deepcopy

class AxisFormatTriggerPatches(AxisFormat):
    '''
    Axis definition used in the trigger patch THnSparse
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "patches")
        self._axes["energy"] = 0 
        self._axes["energyRough"] = 1
        self._axes["amplitude"] = 2
        self._axes["eta"] = 3
        self._axes["phi"] = 4
        self._axes["isMain"] = 5
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatTriggerPatches()
        newobj._Copy(self)
        return newobj
    
    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatTriggerPatches()
        newobj._Deepcopy(self, memo)
        return newobj

class TriggerPatchTHnSparse(THnSparseWrapper):
    '''
    Representation of Patch THnSparse with axes
    - Offline Energy
    - Rough Energy
    - Amplitude
    - eta 
    - phi
    - isMain
    '''

    def __init__(self, roothist):
        '''
        Constructor
        '''
        THnSparseWrapper.__init__(self, roothist)
        self._axisdefinition = AxisFormatTriggerPatches()
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = TriggerPatchTHnSparse(copy(self._rootthnsparse))
        result.CopyCuts(self, False)
        return result
    
    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = TriggerPatchTHnSparse(deepcopy(self._rootthnsparse))
        result.CopyCuts(self, True)
        return result
        
    def SetEtaCut(self, etamin, etamax):
        '''
        Apply cut in eta
        '''
        self.ApplyCut("eta",etamin,etamax)
    
    def SetPhiCut(self, phimin, phimax):
        '''
        Apply cut in phi
        '''
        self.ApplyCut("phi", phimin, phimax)
        
    def SetMainPatch(self):
        '''
        Request main patches
        '''
        self.ApplyCut("isMain", 1, 1)