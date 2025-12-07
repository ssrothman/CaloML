// Small utilities shared by CaloML/SimTruth producers
#ifndef CALOML_SIMTRUTH_UTIL_H
#define CALOML_SIMTRUTH_UTIL_H

#include <vector>
#include <set>
#include <unordered_map>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <numeric>

//#include "FWCore/Framework/interface/Handle.h"
#include "DataFormats/Math/interface/LorentzVector.h"

#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"
#include "SimDataFormats/CaloAnalysis/interface/SimCluster.h"
#include "SimDataFormats/Track/interface/SimTrack.h"

#include "CaloML/DataFormats/interface/SimTrackInfo.h"
#include "CaloML/DataFormats/interface/MergedSimClusterInfo.h"

namespace CaloML {
// Build a map detId -> total energy from a list of PCaloHit containers
inline std::unordered_map<uint32_t,double>
buildTotalEnergies(const std::vector<edm::Handle<edm::PCaloHitContainer>>& simhits_handles) {
    std::unordered_map<uint32_t,double> totalEnergies;
    for (const auto& simhits_h : simhits_handles){
        for (const auto& simhit : *simhits_h){
            totalEnergies[simhit.id()] += simhit.energy();
        }
    }
    return totalEnergies;
}

// Compute merged hit energies for a component of cluster indices
inline std::unordered_map<uint32_t,double>
computeMergedHitEnergiesForComponent(
        const std::vector<SimCluster>& simclusters,
        const std::vector<uint32_t>& component,
        const std::unordered_map<uint32_t,double>& totalEnergies) {

    std::unordered_map<uint32_t,double> mergedHitEnergies;
    for (uint32_t idx : component){
        for (const auto& hit : simclusters[idx].hits_and_fractions()){
            // hit.second are fractions; multiply by total energy map if available
            auto it = totalEnergies.find(hit.first);
            double detEnergy = (it!=totalEnergies.end()) ? it->second : 0.0;
            mergedHitEnergies[hit.first] += hit.second * detEnergy;
        }
    }
    return mergedHitEnergies;
}

// Merge SimTracks collected from all g4Tracks in the component
inline SimTrack mergeTracksFromComponent(const std::vector<SimCluster>& simclusters,
                                         const std::vector<uint32_t>& component) {
    std::vector<SimTrack> tracks;
    for (uint32_t idx: component){
        for (const auto& track : simclusters[idx].g4Tracks()){
            tracks.push_back(track);
        }
    }

    std::sort(tracks.begin(), tracks.end(), [](const SimTrack& a, const SimTrack& b){
        return a.momentum().pt() > b.momentum().pt();
    });

    math::XYZTLorentzVectorD netmomentum = tracks[0].momentum();
    float netcharge = tracks[0].charge();
    int netpdgId = tracks[0].type();
    for(size_t i=1; i<tracks.size(); ++i){
        if (tracks[i].type() != netpdgId && netpdgId != 0){
            int smaller = std::min(netpdgId, tracks[i].type());
            int larger = std::max(netpdgId, tracks[i].type());

            if (larger == 22 && std::abs(smaller) == 11){
                netpdgId = 11;
            } else if (larger == 22 && std::abs(smaller) == 13){
                netpdgId = 13;
            } else if (smaller == -11 && larger == 11){
                netpdgId = 22;
            } else if (smaller == -13 && larger == 13){
                netpdgId = 22;
            } else {
                // ambiguous -> set to 0
                netpdgId = 0;
            }
        }
        netmomentum += tracks[i].momentum();
        netcharge += tracks[i].charge();
    }
    SimTrack mergedTrack(netpdgId, netmomentum);
    return mergedTrack;
}

// Build a SimCluster from merged hit energies and the merged track
inline SimCluster makeMergedSimCluster(const SimTrack& mergedTrack,
                                       const std::unordered_map<uint32_t,double>& mergedHitEnergies,
                                       const std::unordered_map<uint32_t,double>& totalEnergies) {
    SimCluster newcluster(mergedTrack);
    for (const auto& kvpair : mergedHitEnergies){
        double total = 0.0;
        auto it = totalEnergies.find(kvpair.first);
        if (it!=totalEnergies.end()) total = it->second;
        double fraction = (total>0.0) ? (kvpair.second / total) : 0.0;
        newcluster.addRecHitAndFraction(kvpair.first, fraction);
        newcluster.addHitEnergy(kvpair.second);
        newcluster.addSimHit(PCaloHit(float(kvpair.second)));
    }
    return newcluster;
}

inline CaloML::MergedSimClusterInfo mergeSimClusterInfos(
        const std::vector<CaloML::MergedSimClusterInfo>& simclusterinfos,
        const std::vector<uint32_t>& component,
        CaloML::MERGE_REASON reason) {

    CaloML::MergedSimClusterInfo mergedInfo;

    for (uint32_t idx : component){
        const auto& info = simclusterinfos[idx];
        mergedInfo.pdgids.insert(
            mergedInfo.pdgids.end(),
            info.pdgids.begin(),
            info.pdgids.end()
        );
        mergedInfo.simTrackInfos.insert(
            mergedInfo.simTrackInfos.end(),
            info.simTrackInfos.begin(),
            info.simTrackInfos.end()
        );
    }

    //sort descending by energy
    std::vector<size_t> indices(mergedInfo.pdgids.size());
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(),[&mergedInfo](size_t a, size_t b){
        return mergedInfo.simTrackInfos[a].momentumAtCalo.E() > mergedInfo.simTrackInfos[b].momentumAtCalo.E();
    });

    CaloML::MergedSimClusterInfo sortedInfo;
    for(size_t idx : indices){
        sortedInfo.pdgids.push_back(mergedInfo.pdgids[idx]);
        sortedInfo.simTrackInfos.push_back(mergedInfo.simTrackInfos[idx]);
        sortedInfo.reasons.push_back(reason);
    }

    return sortedInfo;
} 

} // namespace CaloML

#endif // CALOML_SIMTRUTH_UTIL_H
