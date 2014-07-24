#include <cstring>
#include <TArrayD.h>
#include <TAxis.h>
#include <TH1D.h>
#include <TH2D.h>
#include <THnSparse.h>
#include <THashList.h>

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
        fHistos = new THashList(Form("List of histograms of container %s", name));
        fHistos->SetOwner();
}

AliEMCalHistoContainer::~AliEMCalHistoContainer(){
        if(fHistos) delete fHistos;
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, int nbins, double xmin, double xmax){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH1D(name, title, nbins, xmin, xmax));
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, int nbins, double *xbins){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH1D(name, title, nbins, xbins));
}

void AliEMCalHistoContainer::CreateTH1(const char *name, const char *title, TArrayD &xbins){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH1D(name, title, xbins.GetSize()-1, xbins.GetArray()));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, int nbinsx, double xmin, double xmax, int nbinsy, double ymin, double ymax){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH2D(name, title, nbinsx, xmin, xmax, nbinsy, ymin, ymax));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, int nbinsx, double *xbins, int nbinsy, double *ybins){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH2D(name, title, nbinsx, xbins, nbinsy, ybins));
}

void AliEMCalHistoContainer::CreateTH2(const char *name, const char *title, TArrayD &xbins, TArrayD &ybins){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new TH2D(name, title, xbins.GetSize() - 1, xbins.GetArray(), ybins.GetSize() - 1, ybins.GetArray()));
}

void AliEMCalHistoContainer::CreateTHnSparse(const char *name, const char *title, int ndim, int *nbins, double *min, double *max){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        fHistos->Add(new THnSparseD(name, title, ndim, nbins, min, max));
}

void AliEMCalHistoContainer::CreateTHnSparse(const char *name, const char *title, int ndim, TAxis **axes){
        if(FindObject(name))
                AliFatal(Form("Object with name %s already exists in the list of histograms", name));
        TArrayD xmin(ndim), xmax(ndim), *binning(NULL);
        TArrayI nbins(ndim);
        TList binEdges; binEdges.SetOwner();
        for(int idim = 0; idim < ndim; ++idim){
                TAxes &myaxis = *(axes[idim])
                nbins[idim] = myaxis.GetNbins();
                xmin[idim] = myaxis.GetXmin();
                xmax[idim] = myaxis.GetXmax();
                binning = new TArrayD(nbins[idim] + 1);
                for(int ib = 0; ib < nbins[idim]; ++ib)
                        (*binning)[ib] = myaxis.GetBinLowEdge(ib);
                (*binning)[nbins[idim]] = myaxis.GetBinUpEdge(nbins[idim]-1);
                binEdges.AddAt(binning, idim);
        }
        THnSparseD *hsparse = new THnSparseD(name, title, ndim, nbins.GetArray(), xmin.GetArray(), xmax.GetArray());
        for(int id = 0; id < ndim; ++id){
                binning = static_cast<TArrayD *>(binEdges.At(id));
                hsparse->SetBinEdges(id, binning->GetArray());
                if(strlen(axes[id]->GetTitle())){
                        hsparse->GetAxis(id)->SetTitle(axes[id]->GetTitle())
                }
        }
        fHistos->Add(hsparse);
}

void AliEMCalHistoContainer::SetObject(TObject * const o){
        if(FindObject(name))
               AliFatal(Form("Object with name %s already exists in the list of histograms", o->GetName()));
        if(!(dynamic_cast<THnBase *>(o) || dynamic_cast<>()))
               AliFatal(Form("Object with name %s is not a histogram", o->GetName())); 
        fHistos->Add(o);
}

void AliEMCalHistoContainer::FillTH1(const char *hname, double x, double weight = 1.){
        TH1 *hist = dynamic_cast<TH1 *>(FindObject(hname));
        if(!hist)
                AliFatal(Form("Histogram with name %s does not exist in the container", hname));
        hist->Fill(x, weight);
}

void AliEMCalHistoContainer::FillTH2(const char *hname, double x, double y, double weight = 1.){
        TH2 *hist = dynamic_cast<TH2 *>(FindObject(hname));
        if(!hist)
                AliFatal(Form("Histogram with name %s does not exist in the container", hname));
        hist->Fill(x, y, weight);
}

void AliEMCalHistoContainer::FillTH2(const char *hname, double *point, double weight = 1.){
        TH2 *hist = dynamic_cast<TH2 *>(FindObject(hname));
        if(!hist)
                AliFatal(Form("Histogram with name %s does not exist in the container", hname));
        hist->Fill(point[0], point[1], weight);
}

void AliEMCalHistoContainer::FillTHnSparse(const char *name, double *x, double weight = 1.){
        THnSparseD *hist = dynamic_cast<THnSparseD *>(FindObject(hname));
        if(!hist)
                AliFatal(Form("Histogram with name %s does not exist in the container", hname));
        hist->Fill(x, weight);
}

TObject *AliEMCalHistoContainer::FindObject(const char *name){
        return fHistos->FindObject(name);
}

