void AddTaskPtEMCalTrigger(){
        AliAnalysisTaskPtEMCalTrigger *pttriggertask = new AliAnalysisTaskPtEMCalTrigger("ptemcaltriggertask");
        pttriggertask->SelectCollisionCandidates(AliVEvent::kINT7 | AliVEvent::kEMC7);                          // Select both INT7 or EMC7 triggered events
}
