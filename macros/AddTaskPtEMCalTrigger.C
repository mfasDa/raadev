AliAnalysisTask* AddTaskPtEMCalTrigger(){
        AliAnalysisManager *mgr = AliAnalysisManager::GetAnalysisManager();
         
        if (!mgr) {
             ::Error("AddTaskPtEMCalTrigger", "No analysis manager to connect to.");
             return NULL;
        }
         
        if (!mgr->GetInputEventHandler()) {
             ::Error("AddTaskPtEMCalTrigger", "This task requires an input event handler");
             return NULL;
        }
        
        AliAnalysisTaskPtEMCalTrigger *pttriggertask = new AliAnalysisTaskPtEMCalTrigger("ptemcaltriggertask");
        pttriggertask->SelectCollisionCandidates(AliVEvent::kINT7 | AliVEvent::kEMC7);                          // Select both INT7 or EMC7 triggered events
        AliESDtrackCuts *trackCuts = AliESDtrackCuts::GetStandardITSTPCTrackCuts2011(true, 1);
        trackCuts->SetMinNCrossedRowsTPC(120);
        trackCuts->SetMaxDCAToVertexXYPtDep("0.0182+0.0350/pt^1.01");
        pttriggertask->SetTrackCuts(trackCuts);
        mgr->AddTask(pttriggertask);

        AliAnalysisDataContainer *cinput = mgr->GetCommonInputContainer();
        AliAnalysisDataContainer *coutput = mgr->CreateContainer("results", TList::Class(),    AliAnalysisManager::kOutputContainer, "AnalysisResults.root");
   
        //Connect input/output
        mgr->ConnectInput(pttriggertask, 0, cinput);
        mgr->ConnectOutput(pttriggertask, 1, coutput);
           
        return pttriggertask;
}
