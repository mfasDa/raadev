#! /usr/bin/env python

from Helper import NormaliseBinWidth
from copy import deepcopy

class MergeException(Exception):
    """
    Error handling for the merge processes
    """
    
    def __init__(self, message):
        """
        Constructor
        """
        self.__message = message
        
    def __str__(self):
        """
        Make exception a string object
        """
        return self.__message

class DataSet:
    """
    Data set for a given trigger class. A data set contains a set of cluster containers and an set of track containers
    """
    
    class ContentException(Exception):
        
        def __init__(self, searchkey, container):
            self.__searchkey = searchkey
            self.__container = container
            
        def __str__(self):
            return "%s already present in container %s" %(self.__searchkey, self.__container)
    
    def __init__(self):
        """
        Constructor
        """
        self.__trackContainers = {}
        self.__clusterContainers = {}
        
    def AddTrackContainer(self, name, data):
        """
        Add a new track container to the dataset
        """
        if name in self.__trackContainers.keys():
            raise DataSet.ContentException(name, "TrackContainer")
        self.__trackContainers[name] = data
        
    def AddClusterContainer(self, name, data):
        """
        Add a new cluster container to the dataset
        """
        if name in self.__clusterContainers.keys():
            raise DataSet.ContentException(name, "ClusterContainer")
        self.__clusterContainers[name] = data
        
    def FindTrackContainer(self, name):
        """
        Find a track container within the dataset
        """
        if not name in self.__trackContainers.keys():
            return None
        return self.__trackContainers[name]

    def FindClusterContainer(self, name):
        """
        Find a cluster container within the dataset
        """
        if not name in self.__clusterContainers:
            return None
        return self.__trackContainers[name]
    
    def GetListOfTrackContainers(self):
        """
        Get a list of track container names
        """
        return self.__trackContainers.keys()
    
    def GetListOfClusterContainers(self):
        """
        Get a list of cluster container names
        """
        return self.__clusterContainers.keys()
    
    def Add(self, other):
        """
        Add other data set to this one
        """
        if not type(other) is DataSet:
            raise MergeException("Incompatible types: this(Dataset), other(%s)" %(str(type(other))))
        nfailure = 0
        for cont in self.GetListOfTrackContainers():
            othercont = other.FindTrackContainer(cont)
            if othercont:
                self.__trackContainers[cont].Add(othercont)
            else:
                nfailure += 1
        for cont in self.GetListOfClusterContainers():
            othercont = other.FindClusterContainer(cont)
            if othercont:
                self.__clusterContainers[cont].Add(othercont)
            else:
                nfailure += 1
        if nfailure:
            raise MergeException("Several containers have not been found inside the other datase")
        
    def Scale(self, scalefactor):
        """
        Scale all track or cluster containers with the underlying scale factor
        """
        for cont in self.__trackContainers.values():
            cont.Scale(scalefactor)
        for cont in self.__clusterContainers.values():
            cont.Scale(scalefactor)
    
class DataContainer:
    """
    Data container (event and spectum container)
    """
    
    class SpectrumCut:
        """
        Helper structure storing a  cut definition for a given dimension
        """
        def __init__(self, dimension, minv, maxv):
            """
            Constructor
            """
            self.__dimension = dimension
            self.__min = minv
            self.__max = maxv
            
        def SetDimension(self, dimension):
            """
            Set the dimension where we want to apply the cut
            """
            self.__dimension = dimension
            
        def GetDimension(self):
            """
            Return the value of the cut
            """
            return self.__dimension
        
        def SetLimits(self, minv, maxv):
            """
            Set the cut range
            """
            self.__min = minv
            self.__max = maxv
            
        def SetMinimum(self, minv):
            """
            Set the minimum of the range
            """
            self.__min = minv
            
        def SetMaximum(self, maxv):
            """
            Set the maximum of the range
            """
            self.__max = maxv
            
        def GetMinimum(self):
            """
            Return minimum value
            """
            return self.__min
        
        def GetMaximum(self):
            """
            Return maximum value
            """
            return self.__max
    
    
    class DataException(Exception):
        """
        Exception handling incomplete data
        """
        def __init__(self, raiseobject):
            """
            constructor
            """
            self.__object = raiseobject
            
        def __str__(self):
            """
            Produce error string
            """
            return "Container %s missing" 
    
    
    def __init__(self, eventHist = None, dataHist = None):
        """
        Construct spectrum container
        """
        self.__events = deepcopy(eventHist)
        self.__spectrum = None
        if dataHist:
            self.__spectrum = SpectrumContainer(dataHist)
        self.__cutList = []
        self._usePileupRejected = True
        self._vertexrange = {}
        self.__doNormBW = True
        self._datahistname = "DataHist"
                
    def SetEventHist(self, eventHist):
        """
        Set the event hist
        """
        self.__events = deepcopy(eventHist)
        
    def SetTrackHist(self, trackhist):
        """
        Set the track hist
        """
        self.__spectrum = SpectrumContainer(trackhist)
        
    def GetEventHist(self):
        """
        Access event counter histogram
        """
        return self.__events
    
    def GetSpectrumContainer(self):
        """
        Access underlying spectrum container
        """
        return self.__spectrum
    
    def Add(self, other):
        """
        Add other data container to this data container
        """
        if not type(other) is DataContainer:
            raise MergeException("Incompatible types: this(DataContainer), other(%s)" %(str(type(other))))
        self.__events.Add(other.GetEventHist())
        self.__spectrum.Add(other.GetSpectrumContainer())
        
    def Scale(self, scalefactor):
        """
        Scale the underlying spectrum container with the scale factor
        """
        self.__spectrum.Scale(scalefactor)
        
    def _AddCut(self, dimension, minv, maxv):
        """
        Add cut for a given dimension
        """
        cutFound = False
        for cut in self.__cutList:
            if cut.GetDimension() == dimension:
                #cut needs to be changed
                cut.SetLimits(minv, maxv)
                cutFound = True
                break
        if not cutFound:
            self.__cutList.append(DataContainer.SpectrumCut(dimension, minv, maxv))

    def GetEventCount(self):
        """
        Get the number of selected events
        """
        if len(self._vertexrange):
            binMin = self.__events.GetYaxis().FindBin(self._vertexrange["min"])
            binMax = self.__events.GetYaxis().FindBin(self._vertexrange["max"])
            eventcounter = self.__events.ProjectionX("eventCounter", binMin, binMax)
        else:
            eventcounter = self.__events.ProjectionX("eventcounter")
        pileupbin = 1
        if self._usePileupRejected:
            pileupbin = 2
        return eventcounter.GetBinContent(pileupbin)
            
    def MakeProjection(self, dim, histname = None, xtitle = None, ytitle = None, doNorm = True):
        """
        Make event-normalised projection to 1D
        """
        if not self.__spectrum:
            raise DataContainer.DataException(self._datahistname)
        if not self.__events:
            raise DataContainer.DataException("EventHist")
        # Apply cuts
        for cut in self.__cutList:
            #print "Processing next cut"
            self.__spectrum.ApplyCut(cut.GetDimension(), cut.GetMinimum(), cut.GetMaximum())
        if not histname:
            histname = "%s/" %(self.__spectrum.GetData().GetName())
        if not xtitle:
            xtitle = ""
        if not ytitle:
            ytitle = ""
        projected = self.__spectrum.ProjectToDimension(dim, histname, xtitle, ytitle)
        projected.Sumw2()
        if doNorm:
            NormaliseBinWidth(projected)
            # Normalise by number of events
            projected.Scale(1./self.GetEventCount())
        return projected         
          
    def Reset(self):
        """ 
        Reset underlying spectrum
        """
        self.__spectrum.Reset()
        for clhist in self.__clusters.values():
            clhist.Reset()
            
class TrackContainer(DataContainer):
    """
    Data representation of track specific histograms
    """
    
    def __init__(self, eventHist = None, trackHist = None):
        """
        Constructor, initialising base class and additional data members
        """
        DataContainer.__init__(self, eventHist, trackHist)
        self._datahistname = "TrackHist"
    
    def SetVertexRange(self, minv, maxv):
        """
        Apply vertex selection both to the event counter and the track hist
        """
        self._vertexrange["min"] = minv
        self._vertexrange["max"] = maxv
        self._AddCut(3, minv, maxv)
        
    def SetEtaRange(self, etamin, etamax):
        """
        Select tracks in a given eta range
        """
        self._AddCut(1, etamin, etamax)
        
    def SetPileupRejection(self, on):
        """
        Apply pileup rejection (yes or no)
        """
        if on == True:
            self._usePileupRejected = True
            self._AddCut(4, 1., 1.)
        else:
            self._usePileupRejected = False
            
    def SelectTrackCuts(self, cutID):
        """
        Select a set of track cuts
        """
        self._AddCut(5, cutID, cutID)
    
    def RequestSeenInMinBias(self):
        self._AddCut(6, 1., 1.)
         
class ClusterContainer(DataContainer):
    """
    Data representation of cluster specific histograms
    """
    
    def __init__(self, eventHist = None, clusterHist = None):
        """
        Constructor, initialising base class and additional data members
        """
        DataContainer.__init__(self, eventHist, clusterHist)
        self._datahistname = "ClusterHist"
        
    def SetVertexRange(self, minv, maxv):
        """
        Apply vertex selection both to the event counter and the track hist
        """
        self._vertexrange["min"] = minv
        self._vertexrange["max"] = maxv
        self._AddCut(1, minv, maxv)
        
    def SetPileupRejection(self, on):
        """
        Apply pileup rejection (yes or no)
        """
        if on == True:
            self._usePileupRejected = True
            self._AddCut(2, 1., 1.)
        else:
            self._usePileupRejected = False

            
class SpectrumContainer:
    """
    Container class for combined spectrum
    """
    
    class DimensionException(Exception):
        """
        Exception class handling user requests to dimensions which do not exist
        """
        
        def __init__(self, dim, maxv):
            """
            Constructor, initialising max. and requested dimension
            """
            self.__dim = dim
            self.__max = maxv
        
        def __str__(self):
            """
            Make string representation of the range exception
            """
            return "Dimension outside range: max %d, requested %d" %(self.__max, self.__dim)
 
    class RangeException(Exception):
        """
        Exception class handling user request which are out of range
        """
        
        def __init__(self, dim, value, minv, maxv):
            """
            Constructor, initialising basic information about the range exception
            """
            self.__dimension = dim
            self.__value = value
            self.__minimum = minv
            self.__maximum = maxv
            
        def __str__(self):
            """
            Make string representation of the range exception
            """
            return "Range exceeded for dimension %d: %f not in [%f,%f]" %(self.__dimension, self.__value, self.__minimum, self.__maximum)
           
    def __init__(self, hsparse):
        """
        Constructor, defining underlying THnSparse
        """
        self.__hsparse = hsparse
        
    def GetData(self):
        """
        Access to underlying histogram
        """
        return self.__hsparse
    
    def Add(self, other):
        """
        Implement add method for the spectrum container, adding up the internal content
        """
        if not type(other) is SpectrumContainer:
            raise MergeException("Incompatible types: this(SpectrumContainer), other(%s)" %(str(type(other))))
        self.__hsparse.Add(other.GetData())
        
    def Scale(self, scalefactor):
        """
        Scale the underlying THnSparse with the scale factor
        """
        self.__hsparse.Scale(scalefactor)
        
    def ApplyCut(self, dim, minv, maxv):
        """
        Apply restrictions in one axis
        """
        kVerySmall = 1e-7
        cutaxis = None
        if isinstance(dim, int):
            cutaxis = self.__FindAxisByNumber(dim)
        elif isinstance(dim,str):
            cutaxis = self.__FindAxisByName(dim)
        if not self.__IsInRange(minv, cutaxis):
            raise self.RangeException(dim, minv, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        if not self.__IsInRange(maxv, cutaxis):
            raise self.RangeException(maxv, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        binmin = cutaxis.FindBin(minv + kVerySmall)
        binmax = cutaxis.FindBin(maxv - kVerySmall)
        #print "Setting range in axis %d from %.f [%d] to %.f [%d]" %(dim, min, binmin, max, binmax)
        self.__hsparse.GetAxis(dim).SetRange(binmin, binmax)
        
    def Reset(self):
        """
        Remove all cuts
        """
        for iaxis in range(0,self.__hsparse.GetNdimensions()):
            self.__hsparse.GetAxis(iaxis).SetRange()
            
    def ProjectToDimension(self, dimension, histname, xtitle = "", ytitle = ""):
        """
        Make 1D projection of the multi-dimensional histogram
        """
        if dimension >= self.__hsparse.GetNdimensions():
            raise self.DimensionException(self.__hsparse.GetNdimensions(), dimension)
        result = self.__hsparse.Projection(dimension)
        result.SetName(histname)
        if len(xtitle):
            result.GetXaxis().SetTitle(xtitle)
        if len(ytitle):
            result.GetYaxis().SetTitle(ytitle)
        return result
    
    def __IsInRange(self, value, axis):
        """
        Check whether value is in the range
        """
        if value < axis.GetXmin() or value > axis.GetXmax():
            return False
        return True
    
    def __FindAxisByNumber(self, dim):
        """
        Find axis for a given dimension number
        """
        if dim >= self.__hsparse.GetNdimensions():
            raise self.DimensionException(dim, self.__hsparse.GetNdimensions())
        return self.__hsparse.GetAxis(dim)
    
    def __FindAxisByName(self, name):
        """
        Find axis for a given dimension name
        """
        result = None
        for r in range (0, self.__hsparse.GetNdimensions()):
            axis = self.__hsparse.GetAxis(r)
            if name == axis.GetName():
                result = axis
                break
        return result
    
    def GetDimension(self, axisname):
        """
        Find dimension for a given name
        """
        result = -1
        for r in range (0, self.__hsparse.GetNdimensions()):
            if axisname == self.__hsparse.GetAxis(r).GetName():
                result = r
                break
        return result
        
