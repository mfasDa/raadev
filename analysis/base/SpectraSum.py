"""
Created on 30.09.2014

Module providing functionality to sum up spectra from different input spectra
A spectrum can be every type that provides an add function (like ROOT THn's)

@author: markusfasel
"""

from copy import deepcopy

class SummingException(Exception):
    """
    Error handling for spectrum summing
    """
    
    def __init__(self, message):
        """
        Constructor
        """
        self.__message = message
    
    def __str__(self):
        """
        Get string representation of the exception
        """
        return self.__message

class SpectraSum(object):
    """
    Class summing up different spectra
    """

    def __init__(self):
        """
        constructor
        """
        self.__summed = None
                
    def AddSpectrum(self, spectrum):
        """
        Add spectrum. If it is the first spectrum, initialise the sum with a deep copy of this. Otherwise add the the spectrum to the sum
        """
        if not self.__summed:
            try:
                self.__summed = deepcopy(spectrum)
            except:
                raise SummingException("Copy of the initial object failed")
        else:
            try:
                self.__summed.Add(spectrum)
            except Exception as e:
                raise SummingException("Exception occurred in adding spectrum: %s" %(str(e)))
        if not self.__summed:
            raise SummingException("Nullpointer to the summed object")
            
    def GetSummedSpectrum(self):
        """
        Access to the summed-up spectrum
        """
        return self.__summed
        