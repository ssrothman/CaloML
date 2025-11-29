#ifndef CALOML_DATAFORMATS_CLUSTERINFO_H_
#define CALOML_DATAFORMATS_CLUSTERINFO_H_

#include <vector>

#include "CaloML/DataFormats/interface/SimTrackInfo.h"

namespace CaloML {
    struct MergedSimClusterInfo {
        std::vector<int> pdgids;
        std::vector<float> energies;
        std::vector<SimTrackInfo> simTrackInfos;
    };
};

#endif