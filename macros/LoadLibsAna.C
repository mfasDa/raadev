void LoadLibsAna(){
        // Load common libraries
        gSystem->Load("libCore.so");  
        gSystem->Load("libTree.so");
        gSystem->Load("libGeom.so");
        gSystem->Load("libVMC.so");
        gSystem->Load("libPhysics.so");
        gSystem->Load("libMinuit.so"); 
        gSystem->Load("libGui.so");
        gSystem->Load("libXMLParser.so");
        gSystem->Load("libSTAT.so");
        gSystem->Load("libSTEERBase.so");
        gSystem->Load("libESD.so");
        gSystem->Load("libCDB.so");
        gSystem->Load("libAOD.so");
        gSystem->Load("libANALYSIS.so");
        gSystem->Load("libANALYSISalice.so");
        gSystem->Load("libProof.so");
        gSystem->Load("libRAWDatabase.so");
        gSystem->Load("libRAWDatarec.so");
        gSystem->Load("libSTEER.so");
        gSystem->Load("libTOFbase.so");
        gSystem->Load("libTRDbase.so");
        gSystem->Load("libVZERObase.so");
        gSystem->Load("libVZEROrec.so");
        gSystem->Load("libTENDER.so");
        gSystem->Load("libPWGUDbase.so");
        gSystem->Load("libTPCbase.so");
        gSystem->Load("libTPCrec.so");
        gSystem->Load("libTPCcalib.so");
        gSystem->Load("libTRDrec.so");
        gSystem->Load("libITSbase.so");
        gSystem->Load("libITSrec.so");
        gSystem->Load("libHMPIDbase.so");
        gSystem->Load("libPWGPP.so");
        //lib necessary for dielectron
        gSystem->Load("libCORRFW.so");

        // Use AliRoot includes to compile our task
        gROOT->ProcessLine(".include $ALICE_ROOT/include");
}
