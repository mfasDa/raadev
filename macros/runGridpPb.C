#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

TString g_aliroot_version;
TString g_root_version;
TString g_sample;
TString g_plugin_mode;
TString g_train_dir;
TArrayI g_runlist;
TString g_grid_workdir;

AliAnalysisAlien *CreateGridHandler(){
        //
        // Setup main settings of the Alien plugin
        //
        AliAnalysisAlien *plugin = new AliAnalysisAlien();
        plugin->SetRunMode(g_plugin_mode.Data());
        if(!g_plugin_mode.CompareTo("Terminate"))
                plugin->SetMergeViaJDL(kFALSE);
        else
                plugin->SetMergeViaJDL(kTRUE);
        plugin->SetOverwriteMode();
        plugin->SetNtestFiles(1);

        plugin->SetAPIVersion("V1.1x");
        plugin->SetROOTVersion(g_root_version.Data());
        plugin->SetAliROOTVersion(g_aliroot_version.Data());

        plugin->SetOutputToRunNo();
        plugin->AddIncludePath("-I. .I$ALIEN_ROOT/api/lib -I$ROOTSYS/lib -I$ROOTSYS/include -I$ALICE_ROOT/include -I$ALICE_ROOT/ANALYSIS");

        std::vector<std::string> additionalLibs;
        additionalLibs.push_back("Gui");
        additionalLibs.push_back("Minuit");
        additionalLibs.push_back("Proof");
        additionalLibs.push_back("XMLParser");
        additionalLibs.push_back("CDB");
        additionalLibs.push_back("RAWDatabase");
        additionalLibs.push_back("RAWDatarec");
        additionalLibs.push_back("STEER");
        additionalLibs.push_back("ANALYSIS");
        additionalLibs.push_back("ANALYSISalice");
        additionalLibs.push_back("ANALYSIScalib");
        additionalLibs.push_back("TENDER");
        additionalLibs.push_back("STAT");
        additionalLibs.push_back("CORRFW");
        additionalLibs.push_back("PWGUDbase");
        additionalLibs.push_back("TPCbase");
        additionalLibs.push_back("TPCrec");
        additionalLibs.push_back("TPCcalib");
        additionalLibs.push_back("TRDbase");
        additionalLibs.push_back("TRDrec");
        additionalLibs.push_back("ITSbase");
        additionalLibs.push_back("ITSrec");
        additionalLibs.push_back("HMPIDbase");
        additionalLibs.push_back("PWGPP");
        additionalLibs.push_back("RAATrigger.par");
        char buffer[1024];
        std::string libstring;
        int entries(0);
        for(std::vector<std::string>::iterator it = additionalLibs.begin(); it != additionalLibs.end(); ++it){
                if(strstr(it->c_str(), ".par"))
                        strcpy(buffer, it->c_str());
                else
                        sprintf(buffer, "lib%s.so", it->c_str());
                libstring += buffer;
                if(entries < additionalLibs.size() -1) libstring += " ";
                entries++;
        }
        std::cout << "Libraries: " << libstring << std::endl;
        plugin->SetAdditionalLibs(libstring.c_str());

        plugin->SetDefaultOutputs(kFALSE);
        plugin->SetOutputFiles("AnalysisResults.root"); 
        plugin->SetExecutableCommand("aliroot -b -q");
        plugin->SetTTL(30000);
        plugin->SetInputFormat("xml-single");
        plugin->SetPrice(1);      
        plugin->SetSplitMode("se");
        return plugin;
}

void SplitConfigEntry(const std::string &input, TString &key, TString &value){
        //
        // Decode key and value of a config entry
        //
        std::istringstream stream(input, istringstream::in);
        std::string tmp;
        stream >> tmp;
        key = tmp.c_str();
        stream >> tmp;
        value = tmp.c_str();
}

void DecodeRunlist(const TString &val){
        //
        // Tokenize run list
        //
        TObjArray *runstrings = val.Tokenize(",");
        TObjString *os;
        TString runstr;
        TIter runIter(runstrings);
        g_runlist.Set(runstrings->GetEntries());
        int nruns(0);
        while((os = dynamic_cast<TObjString *>(runIter()))){
                runstr = os->String();
                g_runlist[nruns++] = runstr.Atoi();
        }
        delete runstrings;
}

bool IsMC(const TString &val){
        // 
        // Determine whether sample is MC or Data
        //
        if(!val.CompareTo("MC")) return true;
        return false;
}

bool FindDataSample(const TMap &lookup, TObjArray &sampleinfis){
        //
        // Find Data sample in the list of samples
        //
        TObjArray *entry = dynamic_cast<TObjArray *>(lookup.GetValue(g_sample.Data()));
        if(!entry){
                printf("Sample %s not found in the list of samples", g_sample.Data());
                return false;
        }
        // Copy to output container
        sampleinfis.SetOwner(kFALSE);
        for(int ival = 0; ival < 4; ival++) sampleinfis.AddAt(entry->At(ival), ival);
        return true;
}

bool GetData(TObjArray &in, TString &out, int pos){
        //
        // Helper function reading data string
        //
        TObjString *entry = dynamic_cast<TObjString *>(in.At(pos));
        if(!entry){
                printf("Entry at pos %d not a string\n", pos);
                return false;
        }
        out = entry->String();
        return true;
}

void AddSample(TMap &lookup,
                const char *key, const char* datadir, const char * pattern, const char *sampletype, const char *dataformat){
        //
        // Add sample entry to the lookup table
        //
        TObjArray *infos = new TObjArray(); 
        infos->AddAt(new TObjString(datadir), 0);
        infos->AddAt(new TObjString(pattern), 1);
        infos->AddAt(new TObjString(sampletype), 2);
        infos->AddAt(new TObjString(dataformat), 3);
        lookup.Add(new TObjString(key), infos);
}

void Generate_Sample_Lookup(TMap &lookup){
        // 
        // Create Lookup table for each period
        // Vector contains 
        //   - path
        //   - pattern
        //   - MC/Data 
        //   - ESD/AOD
        //
        AddSample(lookup, "LHC13b.pass2", "/alice/data/2013/LHC13b", "pass2/*/AliESDs.root", "Data", "ESD");
        AddSample(lookup, "LHC13b.pass3", "/alice/data/2013/LHC13b", "pass3/*/AliESDs.root", "Data", "ESD");
        AddSample(lookup, "LHC13b.pass2.AOD", "/alice/data/2013/LHC13b", "pass2/AOD/*/AliAOD.root", "Data", "AOD"); 
        AddSample(lookup, "LHC13b.pass3.AOD", "/alice/data/2013/LHC13b", "pass3/AOD/*/AliAOD.root", "Data", "AOD"); 
        AddSample(lookup, "LHC13b.pass2.AOD126", "/alice/data/2013/LHC13b", "*/pass2/AOD126/*/AliAOD.root", "Data", "AOD"); 
        AddSample(lookup, "LHC13c.pass1", "/alice/data/2013/LHC13c/", "pass1/*/AliESDs.root", "Data", "ESD");
        AddSample(lookup, "LHC13c.pass2", "/alice/data/2013/LHC13c/", "pass2/*/AliESDs.root", "Data", "ESD");
        AddSample(lookup, "LHC13c.pass1.AOD", "/alice/data/2013/LHC13c/", "*/pass1/AOD/*/AliAOD.root", "Data", "AOD");
        AddSample(lookup, "LHC13c.pass2.AOD", "/alice/data/2013/LHC13c/", "*/pass2/AOD/*/AliAOD.root", "Data", "AOD");
        AddSample(lookup, "LHC13c.pass1.AOD126", "/alice/data/2013/LHC13c/", "*/pass1/AOD126/*/AliAOD.root", "Data", "AOD");
        AddSample(lookup, "LHC13b2", "/alice/sim/2013/LHC13b2", "*/*/AliESDs.root", "MC", "ESD");
        AddSample(lookup, "LHC13b2.AOD", "/alice/sim/2013/LHC13b2", "*/AliAOD.root", "MC", "AOD");
        AddSample(lookup, "LHC13b2plus", "/alice/sim/2013/LHC13b2_plus", "*/*/AliESDs.root", "MC", "ESD");
        AddSample(lookup, "LHC13b2plus.AOD", "/alice/sim/2013/LHC13b2_plus", "*/AliAOD.root", "MC", "AOD");
        AddSample(lookup, "LHC13b3", "/alice/sim/2013/LHC13b3", "*/*/AliESDs.root", "MC", "ESD");
	      AddSample(lookup, "LHC13b3.AOD", "/alice/sim/2013/LHC13b3", "*/AliAOD.root", "MC", "AOD");
	      AddSample(lookup, "LHC13d.pass1", "/alice/data/2013/LHC13d/", "pass1/*/AliESDs.root", "Data", "ESD");
	      AddSample(lookup, "LHC13e.pass1", "/alice/data/2013/LHC13e/", "pass1/*/AliESDs.root", "Data", "ESD");
	      AddSample(lookup, "LHC13f.pass1", "/alice/data/2013/LHC13f/", "pass1/*/AliESDs.root", "Data", "ESD");
        printf("Lookup table with sample information generated\n");
}

void ConfigParser(const char *configname){
        //
        // Parse configuration
        //
        std::ifstream in(configname);
        std::string config;
        TString key, value;
        while(getline(in, config)){
                SplitConfigEntry(config, key, value);
                key.ToLower();
                if(!key.CompareTo("aliroot")){
                        // Aliroot version
                        g_aliroot_version = value;
                        continue;
                }
                if(!key.CompareTo("root")){
                        // root version
                        g_root_version = value;
                        continue;
                }
                if(!key.CompareTo("sample")){
                        // sample name
                        g_sample = value; 
                        continue;
                }
                if(!key.CompareTo("runlist")){
                        // Runlist
                        DecodeRunlist(value); 
                        continue;
                }
                if(!key.CompareTo("mode")){
                        g_plugin_mode = value;
                        continue;
                }
                if(!key.CompareTo("traindir")){
                        g_train_dir = value;
                        continue;
                }
                if(!key.CompareTo("workdir")){
                        g_grid_workdir = value;
                }
                printf("Unknown key: %s\n", key.Data());
        }
}

bool MakeSample(AliAnalysisAlien *plugin, TMap &lookup){
        //
        // Fill Sample information (Data dir, pattern, run list) to the Alien plugin
        //
        TObjArray infos;
        bool found = FindDataSample(lookup, infos);
        if(!found){
                printf("sample %s not found\n", g_sample.Data());
                return false;
        }
        TString datadir, pattern, type;
        GetData(infos, datadir, 0);
        GetData(infos, pattern, 1);
        GetData(infos, type, 2);
        plugin->SetGridDataDir(datadir.Data());
        plugin->SetDataPattern(pattern.Data());
        if(!IsMC(type)) plugin->SetRunPrefix("000");
        // Add runs to the sample
        for(int irun = 0; irun < g_runlist.GetSize(); irun++){
                plugin->AddRunNumber(g_runlist[irun]);
        }
        return true;
}

bool CreateTrainDir(AliAnalysisAlien *plugin, const TMap &lookup){
        //
        // Make train data dir name and JDL, C and sh file names
        //
        TObjArray infos;
        TString grid_base = g_grid_workdir.Length() ? g_grid_workdir : "RAATrigger_pPb";
        bool found = FindDataSample(lookup, infos);
        if(!found){
                printf("sample %s not found\n", g_sample.Data());
                return false;
        }
        TString type; GetData(infos, type, 2);

        // check whether the train dir is already provided or needs to be specified
        if(!g_train_dir.Length()){
                // Query number of train runs before
                const char *gridhome = gGrid->GetHomeDirectory();
                const char gridoutdir[256];
                sprintf(gridoutdir, "%s%s/%s", gridhome, grid_base.Data(), type.Data());
                TGridResult *trainruns = gGrid->Ls(gridoutdir);
                int nruns = trainruns->GetEntries();
                // Get Date and time
                TDatime time;
                g_train_dir = Form("%d_%d%02d%02d_%02d%02d", nruns, time.GetYear(), time.GetMonth(), time.GetDay(), time.GetHour(), time.GetMinute());
        }
        
        plugin->SetGridWorkingDir(Form("%s/%s/%s", grid_base.Data(), type.Data(), g_train_dir.Data()));
        plugin->SetJDLName(Form("RAATrigger_%s_%s.jdl", type.Data(), g_train_dir.Data()));
        plugin->SetExecutable(Form("RAATrigger_%s_%s.sh", type.Data(), g_train_dir.Data()));
        plugin->SetAnalysisMacro(Form("RAATrigger_%s_%s.C", type.Data(), g_train_dir.Data()));
        return true;
}

void SetupUtil(bool isMC, bool isAOD){
        //
        // Setup utility packages
        //
        // 1. CDB connection (ESD only)
        // 2. Physics Selection (ESD only)
        // 3. Centrality Task (ESD only)
        //

        //==== CDB Connection =======
        if(!isAOD){
                gROOT->LoadMacro("$ALICE_ROOT/PWGPP/TPC/macros/AddTaskConfigOCDB.C");
                AddTaskConfigOCDB("raw://");
        }

        //==== Physics Selection ====
        if(!isAOD){
                gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPhysicsSelection.C");
                AliPhysicsSelectionTask* physSelTask = AddTaskPhysicsSelection(isMC);
        }

        //===== ADD CENTRALITY: =====
        //if(!isAOD){
        //        gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskCentrality.C");
        //        AddTaskCentrality();
        //}
}

void SetupPar(char* pararchivename){
        //Load par files, create analysis libraries
        //For testing, if par file already decompressed and modified
        //classes then do not decompress.
 
        TString parpar(Form("%s.par", pararchivename)) ; 
  
        if ( gSystem->AccessPathName(pararchivename) ) {  
                TString processline = Form(".! tar xvzf %s",parpar.Data()) ;
                gROOT->ProcessLine(processline.Data());
        }
  
        TString ocwd = gSystem->WorkingDirectory();
        gSystem->ChangeDirectory(pararchivename);
  
        // check for BUILD.sh and execute
        if (!gSystem->AccessPathName("PROOF-INF/BUILD.sh")) {
                printf("*******************************\n");
                printf("*** Building PAR archive    ***\n");
                cout<<pararchivename<<endl;
                printf("*******************************\n");
    
                if (gSystem->Exec("PROOF-INF/BUILD.sh")) {
                        Error("runProcess","Cannot Build the PAR Archive! - Abort!");
                        return -1;
                }
        }
        // check for SETUP.C and execute
        if (!gSystem->AccessPathName("PROOF-INF/SETUP.C")) {
                printf("*******************************\n");
                printf("*** Setup PAR archive       ***\n");
                cout<<pararchivename<<endl;
                printf("*******************************\n");
                gROOT->Macro("PROOF-INF/SETUP.C");
        }
  
        gSystem->ChangeDirectory(ocwd.Data());
        printf("Current dir: %s\n", ocwd.Data());
}

void SetupHandlers(bool isMC, bool isAOD){
        //
        // Setup Handlers
        //
        TString macrobase = "$ALICE_ROOT/ANALYSIS/macros/train/";
        TString macroname = macrobase;
        if(isAOD)
                macroname += "AddAODHandler.C";
        else
                macroname += "AddESDHandler.C";
        gROOT->Macro(macroname.Data());

        if(isMC && !isAOD){
                // Add MC truth event handler, only in case of ESDs
                gROOT->LoadMacro(Form("%s/AddMCHandler.C", macrobase.Data()));
                AddMCHandler();
        }
}

void SetupTask(bool isMC, bool isAOD){
        gROOT->LoadMacro("AddTaskPtEMCalTrigger.C");
        AddTaskPtEMCalTrigger();
}

void SetupTrain(const TMap &lookup){
        //
        // Setup train:
        //   Determine whether the trains run on MC or Data 
        //   and ESDs or AODs and Configure Handlers, utils
        //   and HFE task according to this
        //
        bool isMC(false), isAOD(false);
        TObjArray infos;
        bool found = FindDataSample(lookup, infos);
        if(!found) return;
        TString type, mode;
        GetData(infos, type, 2);
        GetData(infos, mode, 3);
        isMC = IsMC(type);
        if(!mode.CompareTo("AOD")) isAOD = true;
      
        SetupHandlers(isMC, isAOD);
        SetupUtil(isMC, isAOD);
        SetupTask(isMC, isAOD);
}

void GenerateMergeConfigs(){
        //
        // Generate configurations for merging 
        // (MergeViaJDL and Terminate)
        //

        // Write config for MergeViaJDL
        std::ofstream outMerge("configMerge.txt");
        outMerge << "aliroot " << g_aliroot_version.Data() << std::endl;
        outMerge << "root " << g_root_version.Data() << std::endl;
        outMerge << "sample " << g_sample.Data() << std::endl;
        outMerge << "mode MergeViaJDL\n";
        outMerge << "traindir " << g_train_dir.Data() << std::endl; 
        outMerge << "runlist ";
        for(int irun = 0; irun < g_runlist.GetSize()-1; irun++) outMerge << g_runlist[irun] << ",";
        outMerge << g_runlist[g_runlist.GetSize()-1] << std::endl;
        outMerge.close();
        // Write config for Terminate
        std::ofstream outTerminate("configTerminate.txt");
        outTerminate << "aliroot " << g_aliroot_version.Data() << std::endl;
        outTerminate << "root " << g_root_version.Data() << std::endl;
        outTerminate << "sample " << g_sample.Data() << std::endl;
        outTerminate << "mode Terminate\n";
        outTerminate << "traindir " << g_train_dir.Data() << std::endl; 
        outTerminate << "runlist ";
        for(int irun = 0; irun < g_runlist.GetSize()-1; irun++) outTerminate << g_runlist[irun] << ",";
        outTerminate << g_runlist[g_runlist.GetSize()-1] << std::endl;
        outTerminate.close();

        printf("Configurations for MergeViaJDL and terminate generated\n");
}

void runGridpPb(const char *config = "config.txt"){
        //
        // run analysis 
        //

        TGrid::Connect("alien://");

        SetupPar("RAATrigger");

        // Create Lookup with sample information
        TMap sampleinfos;
        Generate_Sample_Lookup(sampleinfos);

        ConfigParser(config);

        // Configure alien plugin
        AliAnalysisAlien *plugin = CreateGridHandler();
        if(!CreateTrainDir(plugin, sampleinfos)){
                printf("Cannot setup output directory\n");
                return;
        }
        if(!MakeSample(plugin, sampleinfos)){
                printf("Cannot create data sample\n");
                return;
        }
        if(!g_plugin_mode.CompareTo("full")){
                // full mode, creating config files for the merging stage
                GenerateMergeConfigs();
        }

        AliAnalysisManager *mgr = new AliAnalysisManager("raaanalysis");
        mgr->SetGridHandler(plugin);
        
        SetupTrain(sampleinfos);

        // Run train
        if (!mgr->InitAnalysis()) return;
        mgr->PrintStatus();
        // Start analysis in grid.
        mgr->StartAnalysis("grid");
} 

