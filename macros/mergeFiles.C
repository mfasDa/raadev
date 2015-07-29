#if not defined __CINT__ || defined __MAKECINT__
#include <TFileMerger.h>
#include <TObjArray.h>
#include <TObjString.h>
#include <TString.h>
#endif

void mergeFiles(const char *outputfile, const char * filelist){
	TObjArray *files = TString(filelist).Tokenize(" ");
	TFileMerger merger;
	merger.OutputFile(outputfile);
	TIter fileiter(files);
	TObjString *inputfile(NULL);
	while((inputfile = dynamic_cast<TObjString *>(fileiter()))){
		merger.AddFile(inputfile->String().Data());
	}
	merger.Merge();
}
