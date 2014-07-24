#ifndef ALIANALYSISTASKPTEMCALTRIGGER_H_
#define ALIANALYSISTASKPTEMCALTRIGGER_H_

#include "AliAnalysisTaskPt.h"
#include "AliCutValueRange.h"

class TArrayD;
class AliEMCalHistoContainer;
class AliESDtrackCuts;

class AliAnalysisTaskPtEMCalTrigger : public AliAnalysisTaskSE {
        public:
                enum EEMCalTriggerType_t{
                        kEMCalJetLow = 0,
                        kEMCalJetHigh = 1,
                        kEMCalGammaLow = 2,
                        kEMCalGammaHigh = 3
                };
                AliAnalysisTaskPtEMCalTrigger();
                AliAnalysisTaskPtEMCalTrigger(const char *name);
                ~AliAnalysisTaskPtEMCalTrigger();

                void UserCreateOutputObjects();
                void UserExec(Option_t* /*option*/);
                void Terminate() {}

                void SetTrackCuts(AliESDtrackCuts *trackCuts) { fTrackSelection = trackCuts; }
                void SetEtaRange(double etamin, double etamax) { fEtaRange.SetLimits(etamin, etamax); }
                void SetVertexZRange(double zmin, double zmax) { fVertexZRange.SetLimits(zmin, zmax); }

        private:
                AliAnalysisTaskPtEMCalTrigger(const AliAnalysisTaskPtEMCalTrigger &);
                AliAnalysisTaskPtEMCalTrigger &operator=(const AliAnalysisTaskPtEMCalTrigger &);
                void CreateDefaultPtBinning(TArrayD &binning);
                void CreateDefaultZVertexBinning(TArrayD &binning);

                AliEMCalHistoContainer        *fHistos;               //! Histogram container for the task
                AliESDtrackCuts               *fTrackSelection;

                // Cuts
                AliCutValueRange<double>      fEtaRange;              // Eta Selection Range
                AliCutValueRange<double>      fVertexZRange;          // Z-Vertex selection range

                ClassDef(AliAnalysisTaskPtEMCalTrigger, 1)
};
#endif
