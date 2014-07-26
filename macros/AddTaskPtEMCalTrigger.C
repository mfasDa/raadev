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
        mgr->AddTask(pttriggertask);

        AliAnalysisDataContainer *cinput = mgr->GetCommonInputContainer();
        AliAnalysisDataContainer *coutput = mgr->CreateContainer("results", TList::Class(),    AliAnalysisManager::kOutputContainer, "AnalysisResults.root");
   
        //Connect input/output
        mgr->ConnectInput(task, 0, cinput);
        mgr->ConnectOutput(task, 1, coutput);
           
        return task;
}
