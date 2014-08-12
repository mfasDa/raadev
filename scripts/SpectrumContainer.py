#! /usr/bin/python

from Helper import NormaliseBinWidth

class DataContainer:
    
    class SpectumCut(self, dimension, min, max):
        """
        Helper structure storing a  cut definition for a given dimension
        """
        def __init__(self):
            self.__dimension = dimension
            self.__min = min
            self.__max = max
            
        def SetDimension(self, dimension):
            self.__dimension = dimension
            
        def GetDimension(self):
            return self.__dimension
        
        def SetLimits(self, min, max):
            self.__min = min
            self.__max = max
            
        def SetMinimum(self, min):
            self.__min = min
            
        def SetMaximum(self, max):
            self.__max = max
            
        def GetMinimum(self):
            return self.__min
        
        def GetMaximum(self):
            return self.__max
    
    
    class DataException(exception):
        """
        Exception handling incomplete data
        """
        def __init__(self, object):
            self.__object = object
            
        def __str__(self):
            return "Container %s missing" 
    
    
    def __init__(self, eventHist = None, trackHist = None):
        """
        Construct spectrum container
        """
        self.__events = None
        self.__spectrum = None
        if trackHist:
            self.__spectrum = SpectrumContainer(trackHist)
        self.__cutList = []
        self.__usePileupRejected = True
        self.__vertexrange = {}
        
    def SetEventHist(self, eventHist):
        """
        Set the event hist
        """
        self.__eventHist = eventHist
        
    def SetTrackHist(self, trackhist):
        """
        Set the track hist
        """
        self.__trackHist = SpectrumContainer(trackhist)
        
    def AddCut(self, dimension, min, max):
        """
        Add cut for a given dimension
        """
        for cut in self.__cutList:
            if cut.GetDimension() == dimension:
                #cut needs to be changed
                cut.SetLimits(min, max)
                
    def SetVertexRange(self, min, max):
        """
        Apply vertex selection both to the event counter and the track hist
        """
        self.__vertexrange["min"] = min
        self.__vertexrange["max"] = max
        self.AddCut(3, min, max)
        
    def SetPileupRejection(self, on):
        if on == True:
            self.__usePileupRejected = True
        else:
            self.__usePileupRejected = False
            
    def SelectTrackCuts(self, cutID):
        """
        Select a set of track cuts
        """
        self.AddCut(5, cutID, cutID)
            
    def MakeProjection(self, dim, histname = None, xtitle = None, ytitle = None):
        """
        Make event-normalised projection to 1D
        """
        if not self.__trackHist:
            raise DataException("TrackHist")
        if not self.__eventHist:
            raise DataException("EventHist")
        # Apply cuts
        for cut in self.__cutList:
            self.__trackHist.ApplyCut(cut.GetDimension(), cut.GetMinimum(), cut.GetMaximum())
        if not histname:
            histname = "%s/" %(self.__trackHist.GetData().GetName())
        if not xtitle:
            xtitle = ""
        if not ytitle:
            ytitle = ""
        projected = self.__trackHist.ProjectToDimension(dim, histname, xtitle, ytitle)
        projected.Sumw2()
        if self.__doNormBW:
            NormaliseBinWidth(projected)
        # Normalise by number of events
        eventCounter = None
        if len(self.__vertexrange):
            binMin = self.__eventHist.GetYaxis().FindBin(self.__vertexrange["min"])
            binMax = self.__eventHist.GetYaxis().FindBin(self.__vertexrange["max"])
            eventcounter = self.__eventHist.ProjectionX("eventCounter", binMin, binMax)
        else:
            eventcounter = self.__eventHist.ProjectionX("eventcounter")
        pileupbin = 1
        if self.__usePileupRejected:
            pileupbin = 2
        nevents = eventcounter.GetBinContent(pileupbin)
        projected.Scale(1./nevents)
        return projected
                
            
class SpectrumContainer:
    """
    Container class for combined spectrum
    """
    
    class DimensionException(exception):
        """
        Exception class handling user requests to dimensions which do not exist
        """
        
        def __init__(self, dim, max):
            """
            Constructor, initialising max. and requested dimension
            """
            self.__dim = dim
            self.__max = max
        
        def __str__(self):
            """
            Make string representation of the range exception
            """
            return "Dimension outside range: max %d, requested %d" %(self.__max, self.__dim)
 
    class RangeException(exception):
        """
        Exception class handling user request which are out of range
        """
        
        def __init__(self, dim, value, min, max):
            """
            Constructor, initialising basic information about the range exception
            """
            self.__dimension = dim
            self.__value = value
            self.__minimum = min
            self.__maximum = max
            
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
        
    def ApplyCut(self, dim, min, max):
        """
        Apply restrictions in one axis
        """
        axis = None
        if isinstance(dim, int):
            axis = self.__FindAxisByNumber(dim)
        elif isinstance(dim,str):
            axis = FindAxisByName(dim)
        if dim >= self.__hsparse.GetNdimensions():
            raise DimensionException(dim, self.__hsparse.GetNdimensions())
        cutaxis = self.__hsparse.GetAxis(idim)
        if not self.__IsInRange(min, cutaxis):
            raise RangeException(dim, min, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        if not IsInRange(max, cutaxis):
            raise RangeException(max, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        binmin = cutaxis.FindBin(min)
        binmax = cutaxis.FindBin(max)
        cutaxis.SetRange(binMin, binMax)
        
    def Reset(self):
        """
        Remove all cuts
        """
        for iaxis in range(0,self._hsparse.GetNdimensions()):
            self.__hsparse.GetAxis(iaxis).SetRange()
            
    def ProjectToDimension(self, dimension, histname, xtitle = "", ytitle = ""):
        """
        Make 1D projection of the multi-dimensional histogram
        """
        if dimension >= self.__hsparse.GetNdimesions():
            raise DimensionException(self.__hsparse.GetNdimensions(), dimension)
        result = self.__hsparse.Projection(dimension)
        result.SetName(histname)
        if len(xtitle):
            result.GetXaxis().SetTitle(xtitle)
        if len(ytitle):
            result.GetYaxis().SetTitle(ytitle)
        return ytitle
    
    def __IsInRange(self, value, axis):
        """
        Check whether value is in the range
        """
        if value < axis.GetMinimum() or value > axis.GetMaximum():
            return False
        return True