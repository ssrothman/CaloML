#ifndef CALOML_DATAFORMATS_SIMTRACKINFO_H_
#define CALOML_DATAFORMATS_SIMTRACKINFO_H_

#include <vector>
#include "DataFormats/Math/interface/LorentzVector.h"

namespace CaloML {
    struct SimTrackInfo {
        math::XYZTLorentzVectorD vtx;
        math::XYZTLorentzVectorD caloImpact;        
        math::XYZTLorentzVectorD momentumAtCalo;
    };
};

#endif // CALOML_DATAFORMATS_SIMTRACKINFO_H_