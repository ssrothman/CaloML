#ifndef CALOML_DATAFORMATS_CLUSTERINFO_H_
#define CALOML_DATAFORMATS_CLUSTERINFO_H_

#include <vector>

#include "CaloML/DataFormats/interface/SimTrackInfo.h"

namespace CaloML {
    enum MERGE_REASON {
        NONE = 0,
        IMPACT = 1,
        OVERLAP = 2
    };
    
    struct MergedSimClusterInfo {
        std::vector<int> pdgids;
        std::vector<SimTrackInfo> simTrackInfos;
        std::vector<CaloML::MERGE_REASON> reasons;
    };
};

#endif // CALOML_DATAFORMATS_CLUSTERINFO_H_