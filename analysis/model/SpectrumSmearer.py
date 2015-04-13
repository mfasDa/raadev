'''
Created on Apr 13, 2015

@author: markus
'''
from copy import deepcopy
import random

class SpectrumSmearer(object):
    '''
    Simple smearing utility
    '''

    def __init__(self, spectrum):
        '''
        Constructor
        '''
        self.__inputspectrum = spectrum
        self.__niterations  = 1000
        self.__smearmodel = None
        
    def SetNumberOfIterations(self, niter):
        """
        Set the number of iterations
        """
        self.__niterations = niter
        
    def SetSmearModel(self, model):
        """
        Set the model used for the smearing
        """
        self.__smearmodel = model
        
    def RunSmearing(self):
        """
        Run smearing of the input spectrum
            - randomly generate values within the bin, and generate a gaussian response
              using the smear model for the width
            - Fill target bin with weight sigma(bin)/ntiterations
        """
        random.seed()
        smearedspectrum = deepcopy(self.__inputspectrum)
        for jbin in range(1,smearedspectrum.GetXaxis().GetNbins()+1):
            smearedspectrum.SetBinContent(jbin, 0)
            smearedspectrum.SetBinError(jbin, 0)
        smearedspectrum.SetName("%sSmeared" %(self.__inputspectrum))
        
        # run actual smearing
        for ibin in range(1, self.__spectrum.GetXaxis().GetNbins()+1):
            weight = self.__inputspectrum.GetBinContent(ibin)/self.__niterations
            for itrial in range(0, self.__niterations):
                binval = random.uniform(self.__inputspectrum.GetXaxis().GetBinLowEdge(ibin), self.__inputspectrum.GetXaxis().GetBinUpEdge(ibin))
                # get the response
                generated = random.gauss(binval, self.__smearmodel.Eval(binval))
                binInSpectrum = smearedspectrum.GetXaxis().FindBin(generated)
                if binInSpectrum < 1 or binInSpectrum >= smearedspectrum.GetXaxis().GetNbins():
                    continue
                smearedspectrum.Fill(generated, weight)
        return smearedspectrum