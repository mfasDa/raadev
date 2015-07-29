#! /usr/bin/env pythpon
#**************************************************************************
#* Copyright(c) 1998-2015, ALICE Experiment at CERN, All rights reserved. *
#*                                                                        *
#* Author: The ALICE Off-line Project.                                    *
#* Contributors are mentioned in the code where appropriate.              *
#*                                                                        *
#* Permission to use, copy, modify and distribute this software and its   *
#* documentation strictly for non-commercial purposes is hereby granted   *
#* without fee, provided that the above copyright notice appears in all   *
#* copies and that both the copyright notice and this permission notice   *
#* appear in the supporting documentation. The authors make no claims     *
#* about the suitability of this software for any purpose. It is          *
#* provided "as is" without express or implied warranty.                  *
#**************************************************************************
"""
Module creating stripped rootfiles for
- particles
- clusters
- tracks
- jets
- MCjets
- Patches in events

:organization: ALICE Collaboration
:copyright: 1998-2015, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""

from ROOT import TFile, TIter, TList
import os,sys,getopt

class StrippedTriggerContainer(object):
    """
    Trigger class structure for stripped format creator
    """
    
    def __init__(self, name):
        """
        Constructor
        """
        self.__name = name
        self.__eventhist = None
        self.__trackContainers = []
        self.__clusterContainers = []
        self.__patchContainers = []  
        self.__jetContainers = []
        self.__MCJetContainers = []
        self.__RecJetContainers = []
        
    def SetEventHist(self, eventhist):
        """
        Set the event histogram
        
        :param eventhist: Event hist
        :type eventhist: TH1
        """
        self.__eventhist = eventhist
        
    def AddTrackContainer(self, cont):
        """
        Add Track THnSparse to the trigger class
        
        :param cont: Track hist
        :type cont: THnSparse
        """
        self.__trackContainers.append(cont)
        
    def AddClusterContainer(self, cont):
        """
        Add Cluster THnSparse to the trigger class
        
        :param cont: Cluster hist
        :type cont: THnSparse
        """
        self.__clusterContainers.append(cont)
        
    def AddPatchContainer(self, cont):
        """
        Add Trigger patch THnSparse to the trigger class
        
        :param cont: Trigger patch hist
        :type cont: THnSparse
        """
        self.__patchContainers = cont
        
    def AddMCJetContainer(self, cont):
        """
        Add MC-Jet THnSparse to the trigger class
        
        :param cont: MC jet hist
        :type cont: THnSparse
        """
        self.__MCJetContainers.append(cont)
        
    def AddRecJetContainer(self, cont):
        """
        Add Rec-Jet THnSparse to the trigger class
        
        :param cont: Rec jet hist
        :type cont: THnSparse
        """
        self.__RecJetContainers.append(cont)
        
    def GetName(self):
        """
        Get the name of the trigger class
        
        :return: name of the trigger class
        :rtype: str
        """
        return self.__name
        
    def GetEventHist(self):
        """
        Get the event histogram
        
        :return: Event hist
        :rtype: TH1
        """
        return self.__eventhist
    
    def GetTrackContainers(self):
        """
        Get the track THnSparse
        
        :return: Track THnSparse
        :rtype: THnSparse
        """
        return self.__trackContainers
    
    def GetClusterContainers(self):
        """
        Get the cluster THnSparse
        
        :return: Cluster THnSparse
        :rtype: THnSparse
        """
        return self.__clusterContainers
    
    def GetPatchContainer(self):
        """
        Get the trigger patch THnSparse
        
        :return: Trigger patch THnSparse
        :rtype: THnSparse
        """
        return self.__patchContainers
    
    def GetMCJetContainers(self):
        """
        Get the MC-jet THnSparse
        
        :return: MC jet THnSparse
        :rtype: THnSparse
        """
        return self.__MCJetContainers
    
    def GetRecJetContainers(self):
        """
        Get the Rec-Jet THnSparse
        
        :return: rec jet THnSparse
        :rtype: THnSparse
        """
        return self.__RecJetContainers
    
class StrippedTruthContainer(object):
    """
    MC truth data representation for stripped file creation
    """
    
    def __init__(self):
        """
        Constructor
        """
        self.__particles = None
        self.__events = None
        self.__correlationMatrix = None
        
    def SetParticleHist(self, particlehist):
        """
        Set the particle histogram
        
        :param particlehist: particle histogram
        :type particlehist: THnSparse
        """
        self.__particles = particlehist
        
    def SetEventHist(self, events):
        """
        Set the event histogram
        
        :param events: Event histogram
        :type events: TH1
        """
        self.__events = events
        
    def SetCorrelationMatrix(self, corrmatrix):
        """
        Set the correlation matrix
        
        :param corrmatrix: Correlation matrix
        :type corrmatrix: THnSparse
        """
        self.__correlationMatrix = corrmatrix
        
    def GetEventHist(self):
        """
        Get the event histogram
        
        :return: The event histogram
        :rtype: TH1
        """
        return self.__events
    
    def GetParticleHist(self):
        """
        Get the particle THnSparse
        
        :return: The particle hist
        :rtype: THnSparse
        """
        return self.__particles
    
    def GetCorrelationMatrix(self):
        """
        Get the correlation matrix
        
        :return: The correlation matrix
        :rtype: THnSparse
        """
        return self.__correlationMatrix
        
class StrippedFileCreator(object):
    """
    Creator class for stripped files
    """

    def __init__(self):
        """
        Constructor
        """
        self.__statuslist = []
        self.__triggerclasses = []
        self.__globaltriggers = []
        self.__particles = None
        self.__crosssection = None
        self.__ntrials = None
        
    def WriteGlobalTriggers(self, outputfilename):
        """
        Write global trigger patch histograms
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not len(self.__globaltriggers):
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if trigger.GetName() == "MinBias":
                trigger.GetEventHist().Write("events")
        for cont in self.__globaltriggers:
            cont.Write(cont.GetName())
        outputfile.Close()
        
    def WriteParticles(self, outputfilename):
        """
        Write information at MC truth level
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not self.__particles:
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        self.__particles.GetParticleHist().Write("MCTrueParticles")
        self.__particles.GetEventHist().Write("events")
        outputfile.Close()
        
        
    def WriteTracks(self, outputfilename):
        """
        Write track histograms for each trigger class separated to an
        output file
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not "tracks" in self.__statuslist:
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if not len(trigger.GetTrackContainers()):
                continue
            outputfile.mkdir(trigger.GetName())
            outputfile.cd(trigger.GetName())

            trigger.GetEventHist().Write("events")
            for histo in trigger.GetTrackContainers():
                histo.Write()
        outputfile.Close()
        
    def WriteClusters(self, outputfilename):
        """
        Write cluster histograms for each trigger class separated to an
        output file
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not "clusters" in self.__statuslist:
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if not len(trigger.GetClusterContainers()):
                continue
            outputfile.mkdir(trigger.GetName())
            outputfile.cd(trigger.GetName())

            trigger.GetEventHist().Write("events")
            for histo in trigger.GetClusterContainers():
                histo.Write()
        outputfile.Close()
        
    def WritePatches(self, outputfilename):
        """
        Write patch histograms for each trigger class separated to an
        output file
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not "patches" in self.__statuslist:
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if not len(trigger.GetPatchContainers()):
                continue
            outputfile.mkdir(trigger.GetName())
            outputfile.cd(trigger.GetName())

            trigger.GetEventHist().Write("events")
            for histo in trigger.GetPatchContainers():
                histo.Write()
        outputfile.Close()
        
    def WriteMCJets(self, outputfilename):
        """
        Write MCjet histograms for each trigger class separated to an
        output file
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not "mcjets" in self.__statuslist:
            return 
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if not len(trigger.GetMCJetContainers()):
                continue
            outputfile.mkdir(trigger.GetName())
            outputfile.cd(trigger.GetName())

            trigger.GetEventHist().Write("events")
            for histo in trigger.GetMCJetContainers():
                histo.Write()
        outputfile.Close()
        
    def WriteRecJets(self, outputfilename):
        """
        Write MCjet histograms for each trigger class separated to an
        output file
        
        :param outputfilename: Name of the output file
        :type outputfilename: str
        """
        if not "recjets" in self.__statuslist:
            return
        outputfile = TFile(outputfilename, "RECREATE")
        outputfile.cd()
        if self.__crosssection:
            self.__crosssection.Write("crosssection")
        if self.__ntrials:
            self.__ntrials.Write("ntrials")
        for trigger in self.__triggerclasses:
            if not len(trigger.GetMCJetContainers()):
                continue
            outputfile.mkdir(trigger.GetName())
            outputfile.cd(trigger.GetName())

            trigger.GetEventHist().Write("events")
            for histo in trigger.GetMCJetContainers():
                histo.Write()
        outputfile.Close()

    def ReadFile(self, inputfilename, isPythiaHard):
        """
        Read the rootfile, extract histograms and
        assign them to trigger classes and histogram
        categories used later for the creation of 
        stripped output files
        
        :param inputfilename:
        :type inputfilename:
        :param isPythiaHard: if true then PYTHIA hard related histograms are available
        :type isPythiaHard:
        """
        reader = TFile.Open(inputfilename)
        
        # Find the directory of the task
        taskdirectory = ""
        keyiter = TIter(reader.GetListOfKeys())
        fileentry = keyiter.Next()
        while fileentry and not len(taskdirectory):
            if fileentry.GetName().Contains("PtEMCalTriggerTask"):
                taskdirectory = fileentry.GetName()
            fileentry = keyiter.Next()
        if not taskdirectory:
            print "Did not find task output"
            return
        reader.cd(taskdirectory)
        histlist = TIter(taskdirectory).Next()
        
        # get the pythia hard histograms
        if isPythiaHard:
            self.__crosssection = histlist.Get("")
            self.__ntrials = histlist.Get("")
        
        # find the list with the tasks histograms
        listiter = TIter(histlist)
        listentry = listiter.Next()
        while listentry:
            if isinstance(listentry, TList):
                histlist = listentry
                break
            listentry = listiter.Next()
            
        # create output trigger classes
        for trigger in ["MinBias", "EMCJLow", "EMCJHigh", "EMCGLow", "EMCGHigh"]:
            self.__triggerclasses = StrippedTriggerContainer(trigger)

        # iterate over histograms and assign 
        contentIter = TIter(histlist)
        contentObject = contentIter.Next()
        while contentObject:
            try:
                contentObject.SetDirectory(None)
            except:
                pass
            
            #handle different categories
            if "PatchInfo" in contentObject.GetName():
                isInTriggers = False
                for trigger in self.__triggerclasses:
                    if trigger.GetName() in contentObject.GetName():
                        trigger.AddPatchContainer(contentObject)
                        isInTriggers = True
                        if not "patches" in self.__statuslist:
                            self.__statuslist.append("patches")
                if not isInTriggers:
                    self.__globaltriggers.append(contentObject)
            if contentObject.GetName() == "hMCtrueParticles":
                if not self.__particles:
                    self.__particles = StrippedTruthContainer()
                self.__particles.SetParticleHist(contentObject)
            if "hTrackPtCorrelation" in contentObject.GetName():
                if not self.__particles:
                    self.__particles = StrippedTruthContainer()
                self.__particles.SetCorrelationMatrix(contentObject)
            if "hEventHist" in contentObject.GetName():
                for trigger in self.__triggerclasses:
                    if trigger.GetName() in contentObject.GetName():
                        trigger.SetEventHist(contentObject)
            for myname in ["hTrackHist","hMCTrackHist","hTrackInAcceptanceHist", "hMCTrackInAcceptanceHist"]:
                if myname in contentObject.GetName():
                    for trigger in self.__triggerclasses:
                        if trigger.GetName() in contentObject.GetName():
                            trigger.AddTrackContainer(contentObject)
                            if not "tracks" in self.__statuslist:
                                self.__statuslist.append("tracks")
            if "hMCTrack" in contentObject.GetName() and not "Jet" in contentObject.GetName():
                for trigger in self.__triggerclasses:
                    if trigger.GetName() in contentObject.GetName():
                        trigger.AddTrackContainer(contentObject)
                        if not "tracks" in self.__statuslist:
                            self.__statuslist.append("tracks")
            if "hCluster" in contentObject.GetName():
                for trigger in self.__triggerclasses:
                    if trigger.GetName() in contentObject.GetName():
                        trigger.AddClusterContainer(contentObject)
                        if not "custers" in self.__statuslist:
                            self.__statuslist.append("clusters")
            if "hMCJetHist" in contentObject.GetName or "hParticleJetHist" in contentObject.GetName():
                for trigger in self.__triggerclasses():
                    if trigger.GetName() in contentObject.GetName():
                        trigger.AddMCJetContainer(contentObject)
                        if not "mcjets" in self.__statuslist:
                            self.__statuslist.append("mcjets")
            recjetstrings = ["hRecJetHist", "hTrackJet", "hMCTrackJet"]
            for mystr in recjetstrings:
                if mystr in contentObject.GetName():
                    for trigger in self.__triggerclasses():
                        if trigger.GetName() in contentObject.GetName():
                            trigger.AddMCJetContainer(contentObject)
                            if not "mcjets" in self.__statuslist:
                                self.__statuslist.append("recjets")
        
        # add the event hist to the Spectrum
        if self.__particles:
            for trg in self.__triggerclasses:
                if trg.GetName() == "MinBias":
                    self.__particles.SetEventHist(trg.GetEventHist())
        
        # we are DONE
        reader.Close()
        
def ConvertTrainFile(infilename, isPythiaHard):
    """
    Convert rootfile into stripped format consisting of several root files
    
    ::
    """
    directory = os.path.dirname(os.path.abspath(infilename))
    converter = StrippedFileCreator()
    converter.ReadFile(infilename, isPythiaHard)
    
    converter.WriteGlobalTriggers("%s/Triggers.root" %directory)
    converter.WriteParticles("%s/MCParticles.root" %directory)
    converter.WriteTracks("%s/Tracks.root" %directory)
    converter.WriteClusters("%s/Clusters.root" %directory)
    converter.WriteRecJets("%s/RecJets.root" %directory)
    converter.WriteMCJets("%s/MCJets.root" %directory)

def Usage():
    """
    Print usage text
    """
    print "Usage: ./StrippedFileCreator.py name [option]"
    print ""
    print "Options:"
    print "  -h: Print help"
    print "  -p: File has PYTHIA hard information"
    

if __name__ == "__main__":
    isPythiaHard = False
    if len(sys.argv) < 2:
        Usage()
        sys.exit(1)
    if len(sys.argv) > 2:
        opt,arg = getopt.getopt(sys.argv[2:], "ph")
    if "p" in opt:
        Usage()
        sys.exit(1)
    if "t" in opt:
        isPythiaHard = True
    ConvertTrainFile(sys.argv[1], isPythiaHard)