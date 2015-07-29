'''
Created on Jan 8, 2015

@author: markus
'''

from base.struct.DataContainers import TrackContainer, ClusterContainer
from base.struct.EventHistogram import EventHistogramOld, EventHistogramNew
from base.struct.ParticleTHnSparse import CreatePartcileTHnSparse
from copy import deepcopy

class DataContainerFactory(object):
    '''
    classdocs
    '''


    def __init__(self, dataformat):
        '''
        Constructor
        '''
        self.__dataformat = dataformat
        
    def SetDataFormat(self, df):
        self.__dataformat = df
       
    def CreateTrackContainer(self, eventhist, trackhist):
        return TrackContainer(self.MakeEventHist(eventhist), trackhist, self.__dataformat)
    
    def CreateClusterContainer(self, eventhist, clusterhist):
        return ClusterContainer(self.MakeEventHist(eventhist), clusterhist, self.__dataformat)
    
    def CreateParticleContainer(self, particlehist):
        return CreatePartcileTHnSparse(particlehist, True if self.__dataformat == "new" else False)
    
    def MakeEventHist(self, eventhist):
        if self.__dataformat == "new":
            return EventHistogramNew(deepcopy(eventhist))
        else:
            return EventHistogramOld(deepcopy(eventhist))