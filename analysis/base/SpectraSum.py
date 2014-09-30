"""
Created on 30.09.2014

Module providing functionality to sum up spectra from different input spectra
A spectrum can be every type that provides an add function (like ROOT THn's)

@author: markusfasel
"""

from copy import deepcopy

class SpectraSum(object):
    """
    Class summing up different spectra
    """

    def __init__(self, name):
        """
        constructor
        """
        self.__summed = None
        self.__name = name
        
    def AddSpectrum(self, spectrum):
        """
        Add spectrum. If it is the first spectrum, initialise the sum with a deep copy of this. Otherwise add the the spectrum to the sum
        """
        if not self.__summed:
            self.__summed = deepcopy(spectrum)
            self.__summed.SetName(self.__name)
        else:
            self.__summed.Add(spectrum)
            
    def GetSummedSpectrum(self):
        """
        Access to the summed-up spectrum
        """
        return self.__summed
        