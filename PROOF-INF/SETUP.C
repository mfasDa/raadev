Int_t SETUP()
{
   if (gSystem->Getenv("ROOTPROOFLITE")) {
      Printf("RAATrigger-SETUP: PROOF-Lite node (session has %s workers)",
                                   gSystem->Getenv("ROOTPROOFLITE"));
   } else if (gSystem->Getenv("ROOTPROOFCLIENT")) {
      Printf("RAATrigger-SETUP: PROOF client");
   } else {
      Printf("RAATrigger-SETUP: standard PROOF node");
   }
   if (gSystem->Load("libRAATrigger") == -1)
      return -1;
   return 0;
}
