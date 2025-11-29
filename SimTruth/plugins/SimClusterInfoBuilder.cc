#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"
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

class SimClusterInfoBuilder : public edm::stream::EDProducer<> {
public:
    explicit SimClusterInfoBuilder(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    void beginRun(const edm::Run&, const edm::EventSetup&) override;

private:
    edm::EDGetToken simtracks_token_;
    edm::EDGetToken simtrackinfos_token_;;
    edm::EDGetToken simclusters_token_;

    int verbose_;
};


SimClusterInfoBuilder::SimClusterInfoBuilder(const edm::ParameterSet& conf)
    : simtracks_token_(consumes<std::vector<SimTrack>>(conf.getParameter<edm::InputTag>("simtracks"))),
      simtrackinfos_token_(consumes<std::vector<CaloML::SimTrackInfo>>(conf.getParameter<edm::InputTag>("simtrackInfos"))),
      simclusters_token_(consumes<std::vector<SimCluster>>(conf.getParameter<edm::InputTag>("simclusters"))),
      verbose_(conf.getParameter<int>("verbose")) 
{
    produces<std::vector<CaloML::MergedSimClusterInfo>>();
}

void SimClusterInfoBuilder::beginRun(const edm::Run&, const edm::EventSetup& es) {
    //noop
}

void SimClusterInfoBuilder::produce(edm::Event& evt, const edm::EventSetup& es) {
    //get the simtracks
    edm::Handle<std::vector<SimTrack>> simtracks_h;
    evt.getByToken(simtracks_token_, simtracks_h);
    const auto& simtracks = *simtracks_h;

    //get the simtrackinfos
    edm::Handle<std::vector<CaloML::SimTrackInfo>> simtrackinfos_h;
    evt.getByToken(simtrackinfos_token_, simtrackinfos_h);
    const auto& simtrackinfos = *simtrackinfos_h;
    
    //get the simclusters
    edm::Handle<std::vector<SimCluster>> simclusters_h;
    evt.getByToken(simclusters_token_, simclusters_h);
    const auto& simclusters = *simclusters_h;

    auto result = std::make_unique<std::vector<CaloML::MergedSimClusterInfo>>();

    // key: geantTrackId, value: index in simtracks
    std::unordered_map<uint32_t, uint32_t> geantToIndexMap;
    for(size_t i = 0; i < simtracks.size(); ++i){
        geantToIndexMap[simtracks[i].trackId()] = i;
    }

    for (const auto& cluster : simclusters) {
        uint32_t g4id = cluster.g4Tracks()[0].trackId();
        uint32_t trackIdx = geantToIndexMap[g4id];

        const auto& trackInfo = simtrackinfos[trackIdx];
        
        CaloML::MergedSimClusterInfo info;

        info.pdgids.emplace_back(cluster.pdgId());
        info.energies.emplace_back(cluster.energy());
        info.simTrackInfos.emplace_back(trackInfo);

        result->push_back(info);
    }

    evt.put(std::move(result));
}

DEFINE_FWK_MODULE(SimClusterInfoBuilder);
