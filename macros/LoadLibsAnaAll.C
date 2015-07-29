void LoadLibsAnaAll(){
        // Load common libraries
        gSystem->Load("libCore");  
        gSystem->Load("libTree");
        gSystem->Load("libGeom");
        gSystem->Load("libVMC");
        gSystem->Load("libPhysics");
        gSystem->Load("libMinuit"); 
        gSystem->Load("libMinuit2"); 
        gSystem->Load("libGui");
        gSystem->Load("libXMLParser");
        gSystem->Load("libProof");
        gSystem->Load("libSTAT");
        gSystem->Load("libSTEERBase");
        gSystem->Load("libESD");
        gSystem->Load("libCDB");
        gSystem->Load("libAOD");
        gSystem->Load("libOADB");
        gSystem->Load("libANALYSIS");
        gSystem->Load("libANALYSISalice");
        gSystem->Load("libProof");
        gSystem->Load("libRAWDatabase");
        gSystem->Load("libRAWDatarec");
        gSystem->Load("libSTEER");
        gSystem->Load("libTOFbase");
        gSystem->Load("libTRDbase");
        gSystem->Load("libVZERObase");
        gSystem->Load("libVZEROrec");
        gSystem->Load("libTender");
        gSystem->Load("libPWGUDbase");
        gSystem->Load("libTPCbase");
        gSystem->Load("libTPCrec");
        gSystem->Load("libTPCcalib");
        gSystem->Load("libTRDrec");
        gSystem->Load("libITSbase");
        gSystem->Load("libITSrec");
        gSystem->Load("libHMPIDbase");
        gSystem->Load("libPWGPP");
        gSystem->Load("libCORRFW");
        gSystem->Load("libEMCALUtils");
        gSystem->Load("libPHOSUtils");
        gSystem->Load("libPWGCaloTrackCorrBase");
        gSystem->Load("libPWGGACaloTrackCorrelations");
        gSystem->Load("libPWGGACaloTasks");
        gSystem->Load("libEMCALraw");
        gSystem->Load("libEMCALbase");
        gSystem->Load("libEMCALrec");
        gSystem->Load("libTenderSupplies");
        gSystem->Load("libPWGTools");
        gSystem->Load("libPWGEMCAL");
        gSystem->Load("libCGAL");
        gSystem->Load("libfastjet");
        gSystem->Load("libsiscone");
        gSystem->Load("libsiscone_spherical");
        gSystem->Load("libfastjetplugins");
        gSystem->Load("libfastjettools");
        gSystem->Load("libfastjetcontribfragile");
        gSystem->Load("libJETAN");
        gSystem->Load("libFASTJETAN");
        gSystem->Load("libESDfilter");
        gSystem->Load("libPWGGAEMCALTasks");
        gSystem->Load("libPWGJEEMCALJetTasks");

        // Use AliRoot includes to compile our task
        gROOT->ProcessLine(".include $ALICE_ROOT/include");
}

