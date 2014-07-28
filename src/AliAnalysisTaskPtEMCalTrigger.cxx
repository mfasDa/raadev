#include <cstring>
#include <iostream>
#include <memory>
#include <vector>
#include <string>

#include <TDirectory.h>
#include <TH1.h>
#include <THashList.h>
#include <TKey.h>
#include <TList.h>
#include <TObjArray.h>
#include <TString.h>

#include "AliESDEvent.h"
#include "AliESDInputHandler.h"
#include "AliESDtrackCuts.h"
#include "AliESDtrack.h"
#include "AliESDVertex.h"

#include "AliEMCalHistoContainer.h"
#include "AliAnalysisTaskPtEMCalTrigger.h"

ClassImp(AliAnalysisTaskPtEMCalTrigger)

AliAnalysisTaskPtEMCalTrigger::AliAnalysisTaskPtEMCalTrigger():
        AliAnalysisTaskSE(),
        fHistos(NULL),
        fTrackSelection(NULL)
{
}

AliAnalysisTaskPtEMCalTrigger::AliAnalysisTaskPtEMCalTrigger(const char *name):
        AliAnalysisTaskSE(name),
        fResults(NULL),
        fHistos(NULL)
{
        DefineOutput(1, TList::Class());

        // Set default cuts
        fVertexZRange.SetLimits(-10, 10);
        fEtaRange.SetLimits(-0.8, 0.8);

}

AliAnalysisTaskPtEMCalTrigger::~AliAnalysisTaskPtEMCalTrigger(){
        //if(fTrackSelection) delete fTrackSelection;
        if(fHistos) delete fHistos;
}

void AliAnalysisTaskPtEMCalTrigger::UserCreateOutputObjects(){
        fResults = new TList;

        fHistos = new AliEMCalHistoContainer("PtEMCalTriggerHistograms");

        TArrayD ptbinning, zvertexBinning;
        CreateDefaultPtBinning(ptbinning);
        CreateDefaultZVertexBinning(zvertexBinning);
        std::map<std::string, std::string> triggerCombinations;
        // Define names and titles for different triggers in the histogram container
        triggerCombinations.insert(std::pair<std::string,std::string>("MinBias", "min. bias events"));
        triggerCombinations.insert(std::pair<std::string,std::string>("EMCJLow", "jet-triggered events (low threshold)"));
        triggerCombinations.insert(std::pair<std::string,std::string>("EMCJHigh", "jet-triggered events (high threshold)"));
        triggerCombinations.insert(std::pair<std::string,std::string>("EMCGLow", "jet-triggered events (low threshold)"));
        triggerCombinations.insert(std::pair<std::string,std::string>("EMCGHigh", "jet-triggered events (high threshold)"));
        triggerCombinations.insert(std::pair<std::string,std::string>("NoEMCal", "non-EMCal-triggered events (low threshold)"));
        for(std::map<std::string,std::string>::iterator it = triggerCombinations.begin(); it != triggerCombinations.end(); ++it){
                const std::string name = it->first, &title = it->second;
                // Event counter
                fHistos->CreateTH1(Form("hEvents%s", name.c_str()), Form("Event counter for %s", title.c_str()), 2, -0.5, 1.5);
                // Vertex position
                fHistos->CreateTH1(Form("hZVertex%s", name.c_str()), Form("Distribution of the z-vertex position in %s", title.c_str()), zvertexBinning);
                // Histograms for events without pileup rejection and without cuts
                fHistos->CreateTH2(Form("hPt%s_nopr_nocut", name.c_str()), Form("Pt distribution in %s without pileup rejection without track cuts", title.c_str()), zvertexBinning, ptbinning);
                // Histograms for events without pileup rejection and with stand
                fHistos->CreateTH2(Form("hPt%s_nopr_stdcut", name.c_str()), Form("Pt distribution in %s without pileup rejection with standard track cuts", title.c_str()), zvertexBinning, ptbinning);
                // Histograms for events without pileup rejection and without cuts
                fHistos->CreateTH2(Form("hPt%s_wpr_nocut", name.c_str()), Form("Pt distribution in %s with pileup rejection without track cuts", title.c_str()), zvertexBinning, ptbinning);
                // Histograms for events without pileup rejection and without cuts
                fHistos->CreateTH2(Form("hPt%s_wpr_stdcut", name.c_str()), Form("Pt distribution in %s with pileup rejection with standard track cuts", title.c_str()), zvertexBinning, ptbinning);
                // Histograms for events without pileup rejection and without cuts
                fHistos->CreateTH2(Form("hPt%s_failpr_nocut", name.c_str()), Form("Pt distribution in %s which fail the pileup rejection without track cuts", title.c_str()), zvertexBinning, ptbinning);
                // Histograms for events without pileup rejection and without cuts
                fHistos->CreateTH2(Form("hPt%s_failpr_stdcut", name.c_str()), Form("Pt distribution in %s which fail the pileup rejection with standard track cuts", title.c_str()), zvertexBinning, ptbinning);
        }
        fResults->Add(fHistos->GetListOfHistograms());
        if(fTrackSelection) fResults->Add(fTrackSelection);

        PostData(1, fResults);
}

void AliAnalysisTaskPtEMCalTrigger::UserExec(Option_t* /*option*/){

        // Common checks: Have SPD vertex and primary vertex from tracks, and both need to have at least one contributor
        AliESDEvent *esd = static_cast<AliESDEvent *>(fInputEvent);
        const AliESDVertex *vtxTracks = esd->GetPrimaryVertex(),
                     *vtxSPD = esd->GetPrimaryVertexSPD();
        if(!(vtxTracks && vtxSPD)) return;
        if(vtxTracks->GetNContributors() < 1 || vtxSPD->GetNContributors() < 1) return;

        std::vector<std::string> triggerstrings;
        if(fInputHandler->IsEventSelected() & AliVEvent::kEMC7){
                // EMCal-triggered event, distinguish types
                TString trgstr(fInputEvent->GetFiredTriggerClasses());
                if(trgstr.Contains("EJ1")) triggerstrings.push_back("EMCJHigh");
                if(trgstr.Contains("EJ1")) triggerstrings.push_back("EMCJLow");
                if(trgstr.Contains("EG1")) triggerstrings.push_back("EMCGHigh");
                if(trgstr.Contains("EG2")) triggerstrings.push_back("EMCGLow");
        }

        // apply event selection: Combine the Pileup cut from SPD with the other pA Vertex selection cuts.
        bool isPileupEvent = esd->IsPileupFromSPD();
        isPileupEvent = isPileupEvent || (TMath::Abs(vtxTracks->GetZ() - vtxSPD->GetZ()) > 0.5);
        double covSPD[6]; vtxSPD->GetCovarianceMatrix(covSPD); 
        isPileupEvent = isPileupEvent || (TString(vtxSPD->GetTitle()).Contains("vertexer:Z") && TMath::Sqrt(covSPD[5]) > 0.25);

        // Fill the zVertex of the event
        const double &zv = vtxTracks->GetZ();
        fHistos->FillTH1("hZVertexMinBias", zv);
        char histname[1024];      // for string operations
        if(!triggerstrings.size())
                // Non-EMCal-triggered
                fHistos->FillTH1("hZVertexNoEMCal", zv);
        else{
                // EMCal-triggered events
                for(std::vector<std::string>::iterator it = triggerstrings.begin(); it != triggerstrings.end(); ++it){
                        sprintf(histname, "hZVertex%s", it->c_str());
                        fHistos->FillTH1(histname, zv);
                }
        }

        // Reject events which have a vertex outside the limits
        if(!fVertexZRange.IsInRange(vtxTracks->GetZ())){ 
                PostData(1, fResults);
                return;
        }

        // simple event counter: with/without pileup rejection
        fHistos->FillTH1("hEventsMinBias", 0);
        if(!triggerstrings.size()) fHistos->FillTH1("hEventsNoEMCal", 0);
        else{
                for(std::vector<std::string>::iterator it = triggerstrings.begin(); it != triggerstrings.end(); ++it){
                        sprintf(histname, "hEvents%s", it->c_str());
                        fHistos->FillTH1(histname,0);
                }
        }
        if(!isPileupEvent){ 
                fHistos->FillTH1("hEventsMinBias", 1);
                if(!triggerstrings.size()) fHistos->FillTH1("hEventsNoEMCal", 1);
                else{
                        for(std::vector<std::string>::iterator it = triggerstrings.begin(); it != triggerstrings.end(); ++it){
                                sprintf(histname, "hEvents%s", it->c_str());
                                fHistos->FillTH1(histname, 1);
                        }
                }
        }

        AliESDtrack *track(NULL);
        // Loop over all tracks
        for(int itrk = 0; itrk < fInputEvent->GetNumberOfTracks(); ++itrk){
                track = dynamic_cast<AliESDtrack *>(fInputEvent->GetTrack(itrk));
                // first fill without pielup cut
                if(fEtaRange.IsInRange(track->Eta())) continue;
                const double &pt = track->Pt();
                fHistos->FillTH2("hPtMinBias_nopr_nocut", zv, pt);
                if(!isPileupEvent)
                        fHistos->FillTH2("hPtMinBias_wpr_nocut", zv, pt);
                else
                        fHistos->FillTH2("hPtMinBias_failpr_nocut", zv, pt);
                if(!triggerstrings.size()){
                        fHistos->FillTH2("hPtNoEMCal_nopr_nocut", zv, pt);
                        if(!isPileupEvent)
                                fHistos->FillTH2("hPtNoEMCal_wpr_nocut", zv, pt);
                        else
                                fHistos->FillTH2("hPtNoEMCal_failpr_nocut", zv, pt);
                } else {
                        for(std::vector<std::string>::iterator it = triggerstrings.begin(); it != triggerstrings.end(); ++it){
                                sprintf(histname, "hPt%s_nopr_nocut", it->c_str());
                                fHistos->FillTH2(histname, zv, pt);
                                if(!isPileupEvent){
                                        sprintf(histname, "hPt%s_wpr_nocut", it->c_str());
                                        fHistos->FillTH2(histname, zv, pt);
                                } else {
                                        sprintf(histname, "hPt%s_failpr_nocut", it->c_str());
                                        fHistos->FillTH2(histname, zv, pt);
                                }
                        }
                }
        }

        // Now apply track selection cuts
        if(fTrackSelection){
                std::auto_ptr<TObjArray> acceptedTracks(fTrackSelection->GetAcceptedTracks(esd));
                TIter trackIter(acceptedTracks.get());
                while((track = dynamic_cast<AliESDtrack *>(trackIter()))){
                        if(!fEtaRange.IsInRange(track->Eta())) continue;
                        const double &pt = track->Pt();
                        fHistos->FillTH2("hPtMinBias_nopr_stdcut", zv, pt);
                        if(!isPileupEvent)
                                fHistos->FillTH2("hPtMinBias_wpr_stdcut", zv, pt);
                        else
                                fHistos->FillTH2("hPtMinBias_failpr_stdcut", zv, pt);
                        if(!triggerstrings.size()){
                                fHistos->FillTH2("hPtNoEMCal_nopr_stdcut", zv, pt);
                                if(!isPileupEvent){
                                        fHistos->FillTH2("hPtNoEMCal_wpr_stdcut", zv, pt);
                                } else {
                                        fHistos->FillTH2("hPtNoEMCal_failpr_stdcut", zv, pt);
                                }
                        } else {
                                for(std::vector<std::string>::iterator it = triggerstrings.begin(); it != triggerstrings.end(); ++it){
                                        sprintf(histname, "hPt%s_nopr_stdcut", it->c_str());
                                        fHistos->FillTH2(histname, zv, pt);
                                        if(!isPileupEvent){
                                                sprintf(histname, "hPt%s_wpr_stdcut", it->c_str());
                                                fHistos->FillTH2(histname, zv, pt);
                                        } else {
                                                sprintf(histname, "hPt%s_failpr_stdcut", it->c_str());
                                                fHistos->FillTH2(histname, zv, pt);
                                        }
                                }
                        }
                }
        }
        PostData(1, fResults);
}

void AliAnalysisTaskPtEMCalTrigger::CreateDefaultPtBinning(TArrayD &binning){
        std::vector<double> mybinning;
        std::map<double,double> definitions;
        definitions.insert(std::pair<double,double>(2.5, 0.1));
        definitions.insert(std::pair<double,double>(7., 0.25));
        definitions.insert(std::pair<double,double>(15., 0.5));
        definitions.insert(std::pair<double,double>(25., 1.));
        definitions.insert(std::pair<double,double>(40., 2.5));
        definitions.insert(std::pair<double,double>(60., 5.));
        definitions.insert(std::pair<double,double>(100., 5.));
        double currentval = 0;
        for(std::map<double,double>::iterator id = definitions.begin(); id != definitions.end(); ++id){
                double limit = id->first, binwidth = id->second;
                while(currentval <= limit){
                        currentval += binwidth;
                        mybinning.push_back(currentval);
                }
        }
        binning.Set(mybinning.size());
        int ib = 0;
        for(std::vector<double>::iterator it = mybinning.begin(); it != mybinning.end(); ++it)
                binning[ib++] = *it;
}

void AliAnalysisTaskPtEMCalTrigger::CreateDefaultZVertexBinning(TArrayD &binning){
        std::vector<double> mybinning;
        double currentval = -40;
        mybinning.push_back(currentval);
        while(currentval <= 40.){
                currentval += 0.1;
                mybinning.push_back(currentval);
        }
        binning.Set(mybinning.size());
        int ib = 0;
        for(std::vector<double>::iterator it = mybinning.begin(); it != mybinning.end(); ++it)
                binning[ib++] = *it;
}
