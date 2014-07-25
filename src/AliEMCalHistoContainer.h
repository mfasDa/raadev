#ifndef ALIEMCALHISTOCONTAINER_H
#define ALIEMCALHISTOCONTAINER_H

#include <TNamed.h>

class TArrayD;
class TAxis;
class TList;
class THashList;

class AliEMCalHistoContainer : public TNamed{
        public:
                AliEMCalHistoContainer();
                AliEMCalHistoContainer(const char *name);
                ~AliEMCalHistoContainer();

                void CreateTH1(const char *name, const char *title, int nbins, double xmin, double xmax);
                void CreateTH1(const char *name, const char *title, int nbins, double *xbins);
                void CreateTH1(const char *name, const char *title, TArrayD &xbins);
                void CreateTH2(const char *name, const char *title, int nbinsx, double xmin, double xmax, int nbinsy, double ymin, double ymax);
                void CreateTH2(const char *name, const char *title, int nbinsx, double *xbins, int nbinsy, double *ybins);
                void CreateTH2(const char *name, const char *title, TArrayD &xbins, TArrayD &ybins);
                void CreateTHnSparse(const char *name, const char *title, int ndim, int *nbins, double *min, double *max);
                void CreateTHnSparse(const char *name, const char *title, int ndim, TAxis **axes);
                void SetObject(TObject * const o);
                void FillTH1(const char *hname, double x, double weight = 1.);
                void FillTH2(const char *hname, double x, double y, double weight = 1.);
                void FillTH2(const char *hname, double *point, double weight = 1.);
                void FillTHnSparse(const char *name, double *x, double weight = 1.);

                THashList *GetListOfHistograms() { return fHistos; }
                TObject *FindObject(const char *name) const;

        private:
                AliEMCalHistoContainer(const AliEMCalHistoContainer &);
                AliEMCalHistoContainer &operator=(const AliEMCalHistoContainer &);
                
                THashList *fHistos;                   // List of histograms                              

                ClassDef(AliEMCalHistoContainer, 1)   // Container for histograms
};
#endif
