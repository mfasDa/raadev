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
		ALICEINC += -I$(ALICE_ROOT)/include 
		ALICELIB += -L$(ALICE_ROOT)/lib/tgt_$(ALICE_TARGET) -lSTEERBase -lESD -lAOD -lANALYSIS -lANALYSISalice 
	else
	endif
endif

CXXFLAGS     += $(ALICEINC) -g
PACKAGE = RAATrigger
include lib$(PACKAGE).pkg

SRCS := $(SRCS) 
OBJS := $(SRCS:.cxx=.o) G__$(PACKAGE).o
PARFILE = $(PACKAGE).par

all: default-target

default-target: lib$(PACKAGE).so

lib$(PACKAGE).so: $(OBJS)
	@echo "Linking" $@ ...
ifeq ($(ARCH),macosx)
	@$(LD) -bundle -undefined $(UNDEFOPT) $(LDFLAGS) $^ -o $@
endif
ifeq ($(ARCH),macosx64)
	$(LD) $(SOFLAGS)lib$(PACKAGE).so $(LDFLAGS) $(EXPLLINKLIBS) $(ALICELIB) $^ -o $@
else
	@$(LD) $(SOFLAGS) $(LDFLAGS) $^ -o $@
endif
	@chmod a+x $@
	@rm src/*.o G__$(PACKAGE).*
	@echo "done"

%.o:    %.cxx %.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	@rm -f $(OBJS) *.so G__$(PACKAGE).*

G__$(PACKAGE).cxx: $(HDRS) $(DHDR)
	@echo "Generating dictionary ..."
	rootcint -f $@ -c $(CINTFLAGS) $(ALICEINC) -I$(ROOTSYS)/include $^

G__$(PACKAGE).h: ;

# Creating a PAR file
$(PARFILE): $(patsubst %,$(PACKAGE)/%,$(filter-out G__%, $(HDRS) $(SRCS) $(DHDR) Makefile Makefile.arch libRAATrigger.pkg src/RAATriggerLinkDef.h PROOF-INF))
	@echo "Creating archive" $@ ...
	@tar cfzh $@ $(PACKAGE)
	@rm -rf $(PACKAGE)
	@echo "done"

$(PACKAGE)/Makefile: Makefile #.$(PACKAGE)
	@echo Copying $< to $@ with transformations
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	@sed 's/include \$$(ROOTSYS)\/test\/Makefile.arch/include Makefile.arch/' < $^ > $@

$(PACKAGE)/Makefile.arch: $(ROOTSYS)/etc/Makefile.arch
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
