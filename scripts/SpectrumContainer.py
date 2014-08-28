#! /usr/bin/env python

from Helper import NormaliseBinWidth

class DataContainer:
    
    class SpectrumCut:
        """
        Helper structure storing a  cut definition for a given dimension
        """
        def __init__(self, dimension, min, max):
            """
            Constructor
            """
            self.__dimension = dimension
            self.__min = min
            self.__max = max
            
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
        
        def SetLimits(self, min, max):
            """
            Set the cut range
            """
            self.__min = min
            self.__max = max
            
        def SetMinimum(self, min):
            """
            Set the minimum of the range
            """
            self.__min = min
            
        def SetMaximum(self, max):
            """
            Set the maximum of the range
            """
            self.__max = max
            
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
        def __init__(self, object):
            """
            constructor
            """
            self.__object = object
            
        def __str__(self):
            """
            Produce error string
            """
            return "Container %s missing" 
    
    
    def __init__(self, eventHist = None, trackHist = None):
        """
        Construct spectrum container
        """
        self.__events = eventHist
        self.__spectrum = None
        if trackHist:
            self.__spectrum = SpectrumContainer(trackHist)
        self.__cutList = []
        self.__usePileupRejected = True
        self.__vertexrange = {}
        self.__doNormBW = True
        
    def SetEventHist(self, eventHist):
        """
        Set the event hist
        """
        self.__events = eventHist
        
    def SetTrackHist(self, trackhist):
        """
        Set the track hist
        """
        self.__spectrum = SpectrumContainer(trackhist)
        
    def AddCut(self, dimension, min, max):
        """
        Add cut for a given dimension
        """
        cutFound = False
        for cut in self.__cutList:
            if cut.GetDimension() == dimension:
                #cut needs to be changed
                cut.SetLimits(min, max)
                cutFound = True
                break
        if not cutFound:
            self.__cutList.append(DataContainer.SpectrumCut(dimension, min, max))
        
                
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
            self.AddCut(4, 1., 1.)
        else:
            self.__usePileupRejected = False
            
    def SelectTrackCuts(self, cutID):
        """
        Select a set of track cuts
        """
        self.AddCut(5, cutID, cutID)
        
    def GetEventCount(self):
        """
        Get the number of selected events
        """
        if len(self.__vertexrange):
            binMin = self.__events.GetYaxis().FindBin(self.__vertexrange["min"])
            binMax = self.__events.GetYaxis().FindBin(self.__vertexrange["max"])
            eventcounter = self.__events.ProjectionX("eventCounter", binMin, binMax)
        else:
            eventcounter = self.__events.ProjectionX("eventcounter")
        pileupbin = 1
        if self.__usePileupRejected:
            pileupbin = 2
        return eventcounter.GetBinContent(pileupbin)
            
    def MakeProjection(self, dim, histname = None, xtitle = None, ytitle = None, doNorm = True):
        """
        Make event-normalised projection to 1D
        """
        if not self.__spectrum:
            raise DataException("TrackHist")
        if not self.__events:
            raise DataException("EventHist")
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
            
class SpectrumContainer:
    """
    Container class for combined spectrum
    """
    
    class DimensionException(Exception):
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
 
    class RangeException(Exception):
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
        kVerySmall = 1e-7
        cutaxis = None
        if isinstance(dim, int):
            cutaxis = self.__FindAxisByNumber(dim)
        elif isinstance(dim,str):
            cutaxis = FindAxisByName(dim)
        if not self.__IsInRange(min, cutaxis):
            raise RangeException(dim, min, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        if not self.__IsInRange(max, cutaxis):
            raise RangeException(max, cutaxis.GetMinimum(), cutaxis.GetMaximum())
        binmin = cutaxis.FindBin(min + kVerySmall)
        binmax = cutaxis.FindBin(max - kVerySmall)
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
            raise DimensionException(self.__hsparse.GetNdimensions(), dimension)
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
            raise DimensionException(dim, self.__hsparse.GetNdimensions())
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
        
