#ifndef CALOML_CALOHITS_CALOTRUTHINFO_H
#define CALOML_CALOHITS_CALOTRUTHINFO_H 

#include <vector>

//JBOD struct to hold truth info for a calorimeter rechit

namespace CaloML {
    struct HitTruthInfo{
        std::vector<unsigned> simclusters;
        std::vector<float> fracs;
        float simenergy;
    };
};

#endif