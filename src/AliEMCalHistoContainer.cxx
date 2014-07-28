#include <cstring>
#include <vector>
#include <TArrayD.h>
#include <TAxis.h>
#include <TH1D.h>
#include <TH2D.h>
#include <THnSparse.h>
#include <THashList.h>
#include <TObjArray.h>
#include <TObjString.h>
#include <TString.h>

#include "AliLog.h"

#include "AliEMCalHistoContainer.h"

ClassImp(AliEMCalHistoContainer)

AliEMCalHistoContainer::AliEMCalHistoContainer():
        TNamed(),
        fHistos(NULL)
{
}

AliEMCalHistoContainer::AliEMCalHistoContainer(const char *name):
        TNamed(name, Form("Histogram container %s", name)),
        fHistos(NULL)
{
        fHistos = new THashList();
        fHistos->SetName(Form("List of histograms of container %s", name));
        fHistos->SetOwner();
}

AliEMCalHistoContainer::~AliEMCalHistoContainer(){
        if(fHistos) delete fHistos;
}

void AliEMCalHistoContainer::CreateHistoGroup(const char *groupname, const char *parent) throw(HistoContainerContentException) {
        THashList *parentgroup = FindGroup(parent);
        if(!parentgroup) throw HistoContainerContentException(parent, HistoContainerContentException::kGroupException);
        THashList *childgroup = new THashList();
        childgroup->SetName(groupname);
        parentgroup->Add(childgroup);
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, int nbins, double xmin, double xmax) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH1D(name, title, nbins, xmin, xmax));
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, int nbins, double *xbins) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH1D(name, title, nbins, xbins));
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, TArrayD &xbins) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH1D(name, title, xbins.GetSize()-1, xbins.GetArray()));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, 
                int nbinsx, double xmin, double xmax, int nbinsy, double ymin, double ymax) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH2D(name, title, nbinsx, xmin, xmax, nbinsy, ymin, ymax));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, 
                int nbinsx, double *xbins, int nbinsy, double *ybins) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH2D(name, title, nbinsx, xbins, nbinsy, ybins));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, TArrayD &xbins, TArrayD &ybins) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new TH2D(name, title, xbins.GetSize() - 1, xbins.GetArray(), ybins.GetSize() - 1, ybins.GetArray()));
}

void AliEMCalHistoContainer::CreateTHnSparse(const char *name, const char *title, 
                int ndim, int *nbins, double *min, double *max) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        fHistos->Add(new THnSparseD(name, title, ndim, nbins, min, max));
}

void AliEMCalHistoContainer::CreateTHnSparse(const char *name, const char *title, int ndim, TAxis **axes) throw(HistoContainerContentException){
        if(FindObject(name))
                throw HistoContainerContentException(name, HistoContainerContentException::kHistDuplicationException);
        TArrayD xmin(ndim), xmax(ndim);
        TArrayI nbins(ndim);
        std::vector<TArrayD> binEdges;
        for(int idim = 0; idim < ndim; ++idim){
                TAxis &myaxis = *(axes[idim]);
                nbins[idim] = myaxis.GetNbins();
                xmin[idim] = myaxis.GetXmin();
                xmax[idim] = myaxis.GetXmax();
                TArrayD binning(nbins[idim] + 1);
                for(int ib = 0; ib < nbins[idim]; ++ib)
                        binning[ib] = myaxis.GetBinLowEdge(ib);
                binning[nbins[idim]] = myaxis.GetBinUpEdge(nbins[idim]-1);
                binEdges[idim] = binning;
        }
        THnSparseD *hsparse = new THnSparseD(name, title, ndim, nbins.GetArray(), xmin.GetArray(), xmax.GetArray());
        for(int id = 0; id < ndim; ++id){
                TArrayD binning = binEdges[id];
                hsparse->SetBinEdges(id, binning.GetArray());
                if(strlen(axes[id]->GetTitle())){
                        hsparse->GetAxis(id)->SetTitle(axes[id]->GetTitle());
                }
        }
        fHistos->Add(hsparse);
}

void AliEMCalHistoContainer::SetObject(TObject * const o) throw(HistoContainerContentException){
        if(FindObject(o->GetName()))
               throw HistoContainerContentException(o->GetName(), HistoContainerContentException::kHistDuplicationException);
        if(!(dynamic_cast<THnBase *>(o) || dynamic_cast<TH1 *>(o)))
               throw HistoContainerContentException(o->GetName(), HistoContainerContentException::kTypeException); 
        fHistos->Add(o);
}

void AliEMCalHistoContainer::FillTH1(const char *hname, double x, double weight) throw(HistoContainerContentException){
        TH1 *hist = dynamic_cast<TH1 *>(FindObject(hname));
        if(!hist)
                throw HistoContainerContentException(hname, HistoContainerContentException::kHistNotFoundException);
        hist->Fill(x, weight);
}

void AliEMCalHistoContainer::FillTH2(const char *hname, double x, double y, double weight) throw(HistoContainerContentException){
        TH2 *hist = dynamic_cast<TH2 *>(FindObject(hname));
        if(!hist)
                throw HistoContainerContentException(hname, HistoContainerContentException::kHistNotFoundException);
        hist->Fill(x, y, weight);
}

void AliEMCalHistoContainer::FillTH2(const char *hname, double *point, double weight) throw(HistoContainerContentException){
        TH2 *hist = dynamic_cast<TH2 *>(FindObject(hname));
        if(!hist)
                throw HistoContainerContentException(hname, HistoContainerContentException::kHistNotFoundException);
        hist->Fill(point[0], point[1], weight);
}

void AliEMCalHistoContainer::FillTHnSparse(const char *name, double *x, double weight) throw(HistoContainerContentException){
        THnSparseD *hist = dynamic_cast<THnSparseD *>(FindObject(name));
        if(!hist)
                throw HistoContainerContentException(name, HistoContainerContentException::kHistNotFoundException);
        hist->Fill(x, weight);
}

TObject *AliEMCalHistoContainer::FindObject(const char *name) const {
        return fHistos->FindObject(name);
}



THashList *AliEMCalHistoContainer::FindGroup(const char *dirname){
        if(!strcmp(dirname, "/")) return fHistos;
        std::vector<std::string> tokens;
        TokenizeFilename(dirname, "/", tokens);
        THashList *currentdir(fHistos);
        for(std::vector<std::string>::iterator it = tokens.begin(); it != tokens.end(); ++it){
                currentdir = dynamic_cast<THashList *>(currentdir->FindObject(it->c_str()));
                if(!currentdir) break;
        }
        return currentdir;
}

void AliEMCalHistoContainer::TokenizeFilename(const char *name, const char *delim, std::vector<std::string> &listoftokens){
        TString s(name);
        TObjArray *arr = s.Tokenize(delim);
        TObjString *ostr(NULL);
        TIter toks(arr);
        while((ostr = dynamic_cast<TObjString *>(toks()))){
                listoftokens.push_back(std::string(ostr->String().Data()));
        }
        delete arr;
}

const char *AliEMCalHistoContainer::basename(const char *path){
        TString s(path);
        int index = s.Last('/');
        return TString(s(0, index)).Data();
}

const char *AliEMCalHistoContainer::filename(const char *path){
        TString s(path);
        int index = s.Last('/');
        return TString(s(index+1, s.Length() - (index+1))).Data();
}

