#ifndef ALICUTVALUERANGE_H
#define ALICUTVALUERANGE_H

#include <TObject.h>

template<typename t>
class AliCutValueRange : public TObject {
        public:
                AliCutValueRange();
                AliCutValueRange(t min, t max);
                AliCutValueRange(t limit, bool isUpper);
                ~AliCutValueRange();
                 
                void SetLimits(t min, t max){
                        fLimit[0] = min; 
                        fLimit[1] = max;
                        fHasLimits[0] = fHasLimits[1] = true;
                }
                void UnsetLimits(){ fHasLimits[0] = fHasLimits[1] = false; }
                void SetLimit(t value, bool isUpper){
                        int bin = isUpper ? 1 : 0;
                        fLimits[bin] = t;
                        fHasLimit[bin] = true;
                }
                bool UnsetLimit(bool isUpper){
                        int bin = isUpper ? 1 : 0;
                        fHasLimit[bin] = false;
                }
                void Negate() { fNegate = true; } 
                void SetPositive() { fNegate = false; }
                bool IsInRange(t value) const;
        private:
                t       fLimits[2];
                bool    fHasLimit[2];
                bool    fNegate;

                ClassDef(AliCutValueRange, 1)     // Value range for cuts
}
#endif
