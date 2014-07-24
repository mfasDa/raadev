#include "AliCutValueRange.h"

ClassImp(AliCutValueRange)

template<typename t>
AliCutValueRange<t>::AliCutValueRange():
        fNegate(false)
{
        fHasLimit[0] = fHasLimit[1] = false;
}

template<typename t>
AliCutValueRange<t>::AliCutValueRange(t min, t max):
        fNegate(false)
{
        fLimits[0] = min;
        fLimits[1] = max;
        fHasLimit[0] = fHasLimit[1] = true;
}

template<typename t>
AliCutValueRange<t>::AliCutValueRange(t limit, bool isUpper):
        fNegate(false)
{
        if(isUpper){
                fLimits[1] = t;
                fHasLimits[0] = false;
                fHasLimits[1] = true;
        } else {
                fLimits[0] = t;
                fHasLimit[0] = true;
                fHasLimit[1] = false;
        }
}

template<typename t>
AliCutValueRange<t>::IsInRange(t value) const {
        bool result = true;
        if(fHasLimit[0] && fHasLimit[1]){
                // Double-sided limited
                result = fNegate ? (t < fLimits[0] || t > fLimits[1]) : (t > fLimits[0] && t < fLimits[1]);
        } else if(fHasLimit[1]) {
                // only upper bound
                result = fNegate ? (t > fLimit[1]) : (t < fLimit[1]);
        } else if(fHasLimit[0]){
                // only lower bound
                result = fNegate ? (t < fLimit[0]) : (t > fLimit[0]);
        }
        return result;
}
