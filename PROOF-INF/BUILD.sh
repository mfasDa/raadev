#! /bin/sh
# Build libRAATrigger library.
# Based on tutorial example for libEvent
 
if test ! "x$ROOTPROOFLITE" = "x"; then
   echo "RAATrigger-BUILD: PROOF-Lite node (session has $ROOTPROOFLITE workers)"
elif test ! "x$ROOTPROOFCLIENT" = "x"; then
   echo "RAATrigger-BUILD: PROOF client"
else
   echo "RAATrigger-BUILD: standard PROOF node"
fi
 
if [ "" = "clean" ]; then
   make distclean
   exit 0
fi
 
make
rc=$?
echo "rc=$?"
if [ $? != "0" ] ; then
   exit 1
fi
exit 0
