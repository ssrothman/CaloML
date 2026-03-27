#ifndef CALOML_DATAFORMATS_HGCWAFERINFO_H
#define CALOML_DATAFORMATS_HGCWAFERINFO_H

#include <vector>

namespace CaloML{
    struct HGCWaferInfo{
        unsigned waferID;
        std::vector<unsigned> TCindices;
    };
};

#endif
