#ifndef ALIEMCALHISTOCONTAINER_H
#define ALIEMCALHISTOCONTAINER_H
/* Copyright(c) 1998-1999, ALICE Experiment at CERN, All rights reserved. *
 * See cxx source for full Copyright notice                               */

// Author: Markus Fasel

#include <cstring>
#include <exception>
#include <string>
#include <sstream>
#include <TNamed.h>

class TArrayD;
class TAxis;
class TList;
class THashList;

class HistoContainerContentException : public std::exception {
        public:
                enum ExceptionType_t {
                        kHistNotFoundException = 0,
                        kTypeException = 1,
                        kHistDuplicationException = 2,
                        kGroupException = 3
                };

                HistoContainerContentException(const char *histname, const char *hgroup, ExceptionType_t etype):
                        fHistname(),
                        fGroup(),
                        fExceptionType(etype)
                {
                        if(histname) fHistname = histname;
                        if(hgroup) fGroup = hgroup;
                }
                virtual ~HistoContainerContentException() throw() {}

                const char *what() const throw() {
                        std::stringstream msgbuilder;
                        switch(fExceptionType) {
                                case kHistNotFoundException:
                                        msgbuilder << "Histogram " << fHistname << " not found in";
                                        if(strlen(fGroup.c_str())) msgbuilder << " group " << fGroup;
                                        else msgbuilder << " the list of histograms.";
                                        break;
                                case kTypeException:
                                        msgbuilder << "Object " << fHistname << " is of wrong type.";
                                        break;
                                case kHistDuplicationException:
                                        msgbuilder << "Histogram " << fHistname << " already exists in";
                                        if(strlen(fGroup.c_str())) msgbuilder << " group " << fGroup;
                                        else msgbuilder << " the list of histograms.";
                                        break;
                                case kGroupException:
                                        msgbuilder << "Group " << fGroup << " not found.";
                                        break;
                        };
                        return msgbuilder.str().c_str();
                }
                
                const char * GetErrorHistogramName() const { return fHistname.c_str(); }
                ExceptionType_t GetExceptionType() const { return fExceptionType; }

        private:
                std::string           fHistname;
                std::string           fGroup;
                ExceptionType_t       fExceptionType;

};

class AliEMCalHistoContainer : public TNamed{
        public:
                AliEMCalHistoContainer();
                AliEMCalHistoContainer(const char *name);
                ~AliEMCalHistoContainer();
                void ReleaseOwner() { fIsOwner = kFALSE; };

                void CreateHistoGroup(const char *groupname, const char *parent = "/") throw(HistoContainerContentException);

                void CreateTH1(const char *name, const char *title, int nbins, double xmin, double xmax) throw(HistoContainerContentException);
                void CreateTH1(const char *name, const char *title, int nbins, double *xbins) throw(HistoContainerContentException);
                void CreateTH1(const char *name, const char *title, TArrayD &xbins) throw(HistoContainerContentException);
                void CreateTH2(const char *name, const char *title, int nbinsx, double xmin, double xmax, int nbinsy, double ymin, double ymax) throw(HistoContainerContentException);
                void CreateTH2(const char *name, const char *title, int nbinsx, double *xbins, int nbinsy, double *ybins) throw(HistoContainerContentException);
                void CreateTH2(const char *name, const char *title, TArrayD &xbins, TArrayD &ybins) throw(HistoContainerContentException);
                void CreateTHnSparse(const char *name, const char *title, int ndim, int *nbins, double *min, double *max) throw(HistoContainerContentException);
                void CreateTHnSparse(const char *name, const char *title, int ndim, TAxis **axes) throw(HistoContainerContentException);
                void SetObject(TObject * const o, const char *group = "/") throw(HistoContainerContentException);
                void FillTH1(const char *hname, double x, double weight = 1.) throw(HistoContainerContentException);
                void FillTH2(const char *hname, double x, double y, double weight = 1.) throw(HistoContainerContentException);
                void FillTH2(const char *hname, double *point, double weight = 1.) throw(HistoContainerContentException);
                void FillTHnSparse(const char *name, double *x, double weight = 1.) throw(HistoContainerContentException);

                THashList *GetListOfHistograms() { return fHistos; }
                TObject *FindObject(const char *name) const;

        private:
                AliEMCalHistoContainer(const AliEMCalHistoContainer &);
                AliEMCalHistoContainer &operator=(const AliEMCalHistoContainer &);
                THashList *FindGroup(const char *dirname);
                void TokenizeFilename(const char *name, const char *delim, std::vector<std::string> &listoftokens);
                const char *basename(const char *path);
                const char *histname(const char *path);
                
                THashList *fHistos;                   // List of histograms                              
                bool fIsOwner;                        // Set the ownership

                ClassDef(AliEMCalHistoContainer, 1)   // Container for histograms
};
#endif
