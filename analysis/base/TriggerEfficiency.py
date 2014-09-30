'''
Created on 29.09.2014

@author: markusfasel
'''

class TriggerEfficiency:
    """
    Class calculating the trigger efficiency from a given min. bias container and a given triggered container
    """

    def __init__(self, triggername, minbiascontainer, triggeredcontainer):
        """
        Constructor
        """
        self.__triggername = triggername
        self.__minbiascontainer = minbiascontainer
        self.__triggeredcontainer = triggeredcontainer
        self.__triggerefficiency = None
        self.__CalculateTriggerEfficiency()
        
    def __MakeNormalisedSpectrum(self, container, name):
        container.SetVertexRange(-10., 10.)
        container.SetPileupRejection(True)
        container.SelectTrackCuts(1)
        container.RequestSeenInMinBias()
        return container.MakeProjection(0, "ptSpectrum%s" %(name), "p_{#rm{t}} (GeV/c)", "1/N_{event} 1/(#Delta p_{#rm t}) dN/dp_{#rm{t}} ((GeV/c)^{-2}", doNorm = False)
        
    def __CalculateTriggerEfficiency(self):
        minbiasspectrum = self.__MakeNormalisedSpectrum(self.__minbiascontainer, "minbias")
        self.__triggerefficiency = self.__MakeNormalisedSpectrum(self.__triggeredcontainer, self.__triggername)
        self.__triggerefficiency.Divide(self.__triggerefficiency, minbiasspectrum, 1., 1., "b")
        self.__triggerefficiency.SetName("triggerEff%s" %(self.__triggername))
        
    def GetEfficiencyCurve(self):
        return self.__triggerefficiency
        