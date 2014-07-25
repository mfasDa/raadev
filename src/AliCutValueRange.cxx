#include "AliCutValueRange.h"

templateClassImp(AliCutValueRange)

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
                fLimits[1] = limit;
                fHasLimit[0] = false;
                fHasLimit[1] = true;
        } else {
                fLimits[0] = limit;
                fHasLimit[0] = true;
                fHasLimit[1] = false;
        }
}

template<typename t>
bool AliCutValueRange<t>::IsInRange(t value) const {
        bool result = true;
        if(fHasLimit[0] && fHasLimit[1]){
                // Double-sided limited
                result = fNegate ? (value < fLimits[0] || value > fLimits[1]) : (value > fLimits[0] && value < fLimits[1]);
        } else if(fHasLimit[1]) {
                // only upper bound
                result = fNegate ? (value > fLimits[1]) : (value < fLimits[1]);
        } else if(fHasLimit[0]){
                // only lower bound
                result = fNegate ? (value < fLimits[0]) : (value > fLimits[0]);
        }
        return result;
}

template class AliCutValueRange<int>;
template class AliCutValueRange<double>;
template class AliCutValueRange<float>;

