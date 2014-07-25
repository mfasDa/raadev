include $(ROOTSYS)/etc/Makefile.arch


# add include paths from other par files
ifneq ($(ESD_INCLUDE),)
	ALICEINC += -I../$(ESD_INCLUDE)
	ifneq ($(STEERBase_INCLUDE),)
		ALICEINC += -I../$(STEERBase_INCLUDE)
	endif				
	ifneq ($(AOD_INCLUDE),)
		ALICEINC += -I../$(AOD_INCLUDE)
	endif
	ifneq ($(ANALYSIS_INCLUDE),)
		ALICEINC += -I../$(ANALYSIS_INCLUDE)
	endif
	ifneq ($(ANALYSISalice_INCLUDE),)
		ALICEINC += -I../$(ANALYSISalice_INCLUDE)
	endif
else
	ifneq ($(ALICE_ROOT),)
		ALICEINC += -I$(ALICE_ROOT)/include -I$(ALICE_ROOT)/STEER -I$(ALICE_ROOT)/ANALYSIS 
		ALICELIB += -L$(ALICE_ROOT)/lib/tgt_$(ALICE_TARGET) -lSTEERBase -lESD -lAOD -lANALYSIS -lANALYSISalice 
	else
	endif
endif

CXXFLAGS     += $(ALICEINC) -g
PACKAGE = RAATrigger
include lib$(PACKAGE).pkg

SRCS := $(SRCS) G__$(PACKAGE).cxx
OBJS := $(SRCS_ELECTRON:.cxx=.o)
PARFILE = $(PACKAGE).par

default-target: lib$(PACKAGE).so

lib$(PACKAGE).so: $(OBJS)
	@echo "Linking" $@ ...
ifeq ($(ARCH),macosx)
	@$(LD) -bundle -undefined $(UNDEFOPT) $(LDFLAGS) $^ -o $@
endif
ifeq ($(ARCH),macosx64)
	@$(LD) $(SOFLAGS)lib$(PACKAGE).so $(LDFLAGS) $(ALICELIB) $^ -o $@
else
	@$(LD) $(SOFLAGS) $(LDFLAGS) $^ -o $@
endif
	@chmod a+x $@
	@echo "done"

%.o:    %.cxx %.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	@rm -f $(OBJS) *.so G__$(PACKAGE).*

G__$(PACKAGE).cxx: $(HDRS) $(DHDR)
	@echo "Generating dictionary ..."
	rootcint -f $@ -c $(CINTFLAGS) $(ALICEINC) $^

G__$(PACKAGE).h: ;

# Creating a PAR file
$(PARFILE): $(patsubst %,$(PACKAGE)/%,$(filter-out G__%, $(HDRS) $(SRCS) $(DHDR) Makefile Makefile.arch libRAATrigger.pkg src/RAATriggerLinkDef.h PROOF-INF))
	@echo "Creating archive" $@ ...
#	@cat libPWG3hfe.pkg | sed -e 's/hfe\///g' >> $(PACKAGE)/libPWG3hfe.pkg
#	@mv $(PACKAGE)/hfe/* $(PACKAGE)/
#	@rm -rf $(PACKAGE)/hfe
	@tar cfzh $@ $(PACKAGE)
	@rm -rf $(PACKAGE)/PROOF-INF
	@rm -rf $(PACKAGE)/libPWG3hfe.pkg
	@rm -rf $(PACKAGE)/PWG3hfeLinkDef.h
	@rm -rf $(PACKAGE)/Makefile
	@rm -rf $(PACKAGE)/Makefile.arch
	@rm -rf $(PACKAGE)
	@echo "done"

$(PACKAGE)/Makefile: Makefile #.$(PACKAGE)
	@echo Copying $< to $@ with transformations
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	@sed 's/include \$$(ROOTSYS)\/test\/Makefile.arch/include Makefile.arch/' < $^ > $@

$(PACKAGE)/Makefile.arch: $(ROOTSYS)/test/Makefile.arch
	@echo Copying $< to $@
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	@cp -a $^ $@

$(PACKAGE)/PROOF-INF: PROOF-INF
	@echo Copying $< to $@
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	@cp -a $^ $@

$(PACKAGE)/%: %
	@echo Copying $< to $@
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	@cp -a $< $@
