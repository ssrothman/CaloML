#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"
#include "DataFormats/CaloRecHit/interface/CaloRecHit.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
#include "DataFormats/HcalRecHit/interface/HORecHit.h"
#include "DataFormats/HGCRecHit/interface/HGCRecHit.h" 
#include "DataFormats/L1THGCal/interface/HGCalTriggerCell.h"

#include "SimDataFormats/CaloTest/interface/HGCalTestNumbering.h"
#include "Geometry/HcalCommonData/interface/HcalHitRelabeller.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/L1THGCal/interface/HGCalTriggerCell.h"
#include "DataFormats/L1THGCal/interface/HGCalMulticluster.h"
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToMany.h"
#include "SimDataFormats/CaloAnalysis/interface/CaloParticleFwd.h"
#include "SimDataFormats/CaloAnalysis/interface/CaloParticle.h"
#include "DataFormats/ForwardDetId/interface/HGCalTriggerDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCEEDetId.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerGeometryBase.h"
#include "L1Trigger/L1THGCalUtilities/interface/HGCalTriggerNtupleBase.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerTools.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "SimDataFormats/CaloAnalysis/interface/SimCluster.h"
#include "SimDataFormats/Track/interface/SimTrack.h"
#include "SimDataFormats/Vertex/interface/SimVertex.h"

#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "CommonTools/BaseParticlePropagator/interface/RawParticle.h"
#include "CommonTools/BaseParticlePropagator/interface/BaseParticlePropagator.h"
#include "CaloML/SimTruth/interface/util.h"

#include "CaloML/DataFormats/interface/HitTruthInfo.h"

#include <numeric>
#include <unordered_map>
#include <algorithm>

template <typename T>
class HitTruthBuilderT : public edm::stream::EDProducer<> {
    public:
        explicit HitTruthBuilderT(const edm::ParameterSet&);
        
        void produce(edm::Event&, const edm::EventSetup&) override;
        void beginRun(const edm::Run&, const edm::EventSetup&) override;
    
    private:
        edm::EDGetToken simclusters_token_;
        std::vector<edm::EDGetToken> rechits_tokens_;
        
        int verbose_;
};

template <typename T>
HitTruthBuilderT<T>::HitTruthBuilderT(const edm::ParameterSet& conf)
    : simclusters_token_(consumes<edm::View<SimCluster>>(conf.getParameter<edm::InputTag>("simclusters"))),
    verbose_(conf.getParameter<int>("verbose")) 
{
    for (const auto& tag : conf.getParameter<std::vector<edm::InputTag>>("rechits")) {
        rechits_tokens_.push_back(consumes<edm::View<T>>(tag));
    }
    produces<std::vector<CaloML::HitTruthInfo>>();
}

template <typename T>
void HitTruthBuilderT<T>::beginRun(const edm::Run&, const edm::EventSetup& es) {
    // No special actions needed at begin run for this module
}

template <typename T>
inline uint32_t getDetIdFromHit(const T& hit) {
    return hit.detid();
}

template <>
inline uint32_t getDetIdFromHit<reco::PFRecHit>(const reco::PFRecHit& hit) {
    return hit.detId();
}

template <>
inline uint32_t getDetIdFromHit<l1t::HGCalTriggerCell>(const l1t::HGCalTriggerCell& hit) {
    return hit.detId();
}

template <>
inline uint32_t getDetIdFromHit<PCaloHit>(const PCaloHit& hit) {
    return hit.id();
}

template <typename T>
void HitTruthBuilderT<T>::produce(edm::Event& evt, const edm::EventSetup& es) {
    // Get the simclusters
    edm::Handle<edm::View<SimCluster>> simclusters_h;
    evt.getByToken(simclusters_token_, simclusters_h);
    const auto& simclusters = *simclusters_h;   

    // Get the rechits
    std::vector<edm::Handle<edm::View<T>>> rechits_h;
    for (const auto& token : rechits_tokens_) {
        edm::Handle<edm::View<T>> handle;
        evt.getByToken(token, handle);
        rechits_h.push_back(handle);
    }

    auto result = std::make_unique<std::vector<CaloML::HitTruthInfo>>();

    //map of detid->vector of (simcluster index, simenergy) values
    std::unordered_map<uint32_t, std::vector<std::pair<int, float>>> hitToSimClusterMap;
    //map of detid->total simenergy
    std::unordered_map<uint32_t, float> hitToSimEnergyMap;

    for (size_t scIdx = 0; scIdx < simclusters.size(); ++scIdx) {
        const auto& simcluster = simclusters[scIdx];
        for (const auto& hitAndE : simcluster.hits_and_energies()) {
            uint32_t detid = hitAndE.first;
            float E = hitAndE.second;
            hitToSimClusterMap[detid].emplace_back(scIdx, E);
            hitToSimEnergyMap[detid] += E;
        }
    }

    // Now build HitTruth objects for each rechit
    for (const auto& rechitsHandle : rechits_h) {
        for (const auto& rechit : *rechitsHandle) {
            uint32_t detid = getDetIdFromHit(rechit);
            
            CaloML::HitTruthInfo hitTruth;
            hitTruth.simclusters.clear();
            hitTruth.fracs.clear();
            hitTruth.simenergy = 0;

            auto it = hitToSimClusterMap.find(detid);
            if (it != hitToSimClusterMap.end()) {
                hitTruth.simenergy = hitToSimEnergyMap[detid];
                for (const auto& scInfo : it->second) {
                    hitTruth.simclusters.push_back(scInfo.first);
                    hitTruth.fracs.push_back(scInfo.second / hitTruth.simenergy);
                }
            }

            // sort by fraction descending
            std::vector<size_t> indices(hitTruth.simclusters.size());
            std::iota(indices.begin(), indices.end(), 0);
            std::sort(indices.begin(), indices.end(), [&](size_t a, size_t b) {
                return hitTruth.fracs[a] > hitTruth.fracs[b];
            });
            std::vector<unsigned> sortedSimclusters;
            std::vector<float> sortedFracs;
            for (size_t idx : indices) {
                sortedSimclusters.push_back(hitTruth.simclusters[idx]);
                sortedFracs.push_back(hitTruth.fracs[idx]);
            }
            hitTruth.simclusters = std::move(sortedSimclusters);
            hitTruth.fracs = std::move(sortedFracs);

            result->push_back(hitTruth);
        }
    }

    evt.put(std::move(result));
}

typedef HitTruthBuilderT<PCaloHit> PCaloHitTruthBuilder;
typedef HitTruthBuilderT<CaloRecHit> CaloRecHitTruthBuilder;
typedef HitTruthBuilderT<reco::PFRecHit> PFRecHitTruthBuilder;

typedef HitTruthBuilderT<EcalRecHit> EcalRecHitTruthBuilder;
typedef HitTruthBuilderT<HBHERecHit> HBHERecHitTruthBuilder;
typedef HitTruthBuilderT<HORecHit> HORecHitTruthBuilder;
typedef HitTruthBuilderT<HFRecHit> HFRecHitTruthBuilder;

typedef HitTruthBuilderT<l1t::HGCalTriggerCell> HGCalTriggerCellTruthBuilder;
typedef HitTruthBuilderT<HGCRecHit> HGCalRecHitTruthBuilder;

DEFINE_FWK_MODULE(PCaloHitTruthBuilder);
DEFINE_FWK_MODULE(CaloRecHitTruthBuilder);
DEFINE_FWK_MODULE(PFRecHitTruthBuilder);

DEFINE_FWK_MODULE(EcalRecHitTruthBuilder);
DEFINE_FWK_MODULE(HBHERecHitTruthBuilder);
DEFINE_FWK_MODULE(HORecHitTruthBuilder);
DEFINE_FWK_MODULE(HFRecHitTruthBuilder);

DEFINE_FWK_MODULE(HGCalTriggerCellTruthBuilder);
DEFINE_FWK_MODULE(HGCalRecHitTruthBuilder);


