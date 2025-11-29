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


class TriggerCellSimHitsProducer : public edm::stream::EDProducer<> {
public:
    explicit TriggerCellSimHitsProducer(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    void beginRun(const edm::Run&, const edm::EventSetup&) override;
private:
    std::vector<edm::EDGetToken> simhits_tokens_;

    edm::ESGetToken<HGCalTriggerGeometryBase, CaloGeometryRecord> triggerGeomToken_;

    HGCalTriggerTools triggerTools_;
};

TriggerCellSimHitsProducer::TriggerCellSimHitsProducer(const edm::ParameterSet& conf)
    : triggerGeomToken_(esConsumes<HGCalTriggerGeometryBase, CaloGeometryRecord, edm::Transition::BeginRun>())
{
    std::vector<edm::InputTag> simhits_tags = conf.getParameter<std::vector<edm::InputTag>>("simHits");
    for (const auto& tag : simhits_tags) {
        simhits_tokens_.emplace_back(consumes<edm::PCaloHitContainer>(tag));
    }
    produces<std::vector<PCaloHit>>();
}

void TriggerCellSimHitsProducer::beginRun(const edm::Run&, const edm::EventSetup& es) {
    const auto& triggerGeometry = es.getHandle(triggerGeomToken_);
    triggerTools_.setGeometry(triggerGeometry.product());
}

void TriggerCellSimHitsProducer::produce(edm::Event& evt, const edm::EventSetup& es) {
    // Get the sim hits
    std::vector<edm::Handle<edm::PCaloHitContainer>> simhits_handles;
    simhits_handles.resize(simhits_tokens_.size());
    for (size_t i = 0; i < simhits_tokens_.size(); ++i) {
        evt.getByToken(simhits_tokens_[i], simhits_handles[i]);
    }

    std::unordered_map<int, std::unordered_map<int, std::vector<PCaloHit>>> simHitsMap;

    for (const auto& simhit_h : simhits_handles){
        for (const auto& simhit : *simhit_h){
            uint32_t detid = simhit.id();
            uint32_t tcid = triggerTools_.getTriggerGeometry()->getTriggerCellFromCell(detid);
            uint32_t trackId = simhit.geantTrackId();
            simHitsMap[trackId][tcid].push_back(simhit);
        }
    }

    auto output_hits = std::make_unique<std::vector<PCaloHit>>();

    for (const auto& [trackId, tcHits] : simHitsMap) {
        for (const auto& [tcid, hits] : tcHits) {
            if (hits.empty()) continue;

            // Create a new PCaloHit for the trigger cell
            float E=0;
            float E_EM = 0;
            for (const auto& hit : hits) {
                E += hit.energy();
                E_EM += hit.energyEM();
            }
            output_hits->emplace_back(tcid, E, 0.0, trackId, E_EM/E);
        }
    }

    evt.put(std::move(output_hits));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(TriggerCellSimHitsProducer);
