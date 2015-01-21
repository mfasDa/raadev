void LoadLibsFastjet(){
        gSystem->Load("libCGAL");
        gSystem->Load("libfastjet");
        gSystem->Load("libsiscone");
        gSystem->Load("libsiscone_spherical");
        gSystem->Load("libfastjetplugins");
        gSystem->Load("libfastjettools");
        gSystem->Load("libfastjetcontribfragile");
}
