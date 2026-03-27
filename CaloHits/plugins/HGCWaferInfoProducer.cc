#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

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

#include "CaloML/DataFormats/interface/HGCWaferInfo.h"

class HGCWaferInfoProducer : public edm::stream::EDProducer<> {
public:
    explicit HGCWaferInfoProducer(const edm::ParameterSet&);

    void produce(edm::Event&, const edm::EventSetup&) override;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    // beginRun() to get geometry and initialize trigger tools
    void beginRun(const edm::Run& run, const edm::EventSetup& es) override;

private:
    edm::EDGetToken TCs_token_;

    int verbose_;

    const edm::ESGetToken<HGCalTriggerGeometryBase, CaloGeometryRecord> geomToken_;
    HGCalTriggerTools triggerTools_;
};

HGCWaferInfoProducer::HGCWaferInfoProducer(const edm::ParameterSet& conf) :
    TCs_token_(consumes<edm::View<l1t::HGCalTriggerCell>>(conf.getParameter<edm::InputTag>("TCs"))),
    verbose_(conf.getParameter<int>("verbose")),
    geomToken_(edm::stream::EDProducer<>::esConsumes<edm::Transition::BeginRun>())
{
    produces<std::vector<CaloML::HGCWaferInfo>>();
}

void HGCWaferInfoProducer::beginRun(const edm::Run& run, const edm::EventSetup& es) {
    triggerTools_.eventSetup(es, geomToken_);
}

void HGCWaferInfoProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("TCs", edm::InputTag(""));
    desc.add<int>("verbose", 0);
    descriptions.add("hgcWaferInfoProducer", desc);
}

void HGCWaferInfoProducer::produce(edm::Event& evt, const edm::EventSetup& es) {
    edm::Handle<edm::View<l1t::HGCalTriggerCell>> TCs_h;
    evt.getByToken(TCs_token_, TCs_h);
    const auto& TCs = *TCs_h;

    std::unordered_map<unsigned, std::vector<unsigned>> wafer_to_TCs;
    for (unsigned i = 0; i < TCs.size(); ++i) {
        const auto& tc = TCs[i];
        unsigned waferID = triggerTools_.getTriggerGeometry()->getModuleFromTriggerCell(tc.detId());
        wafer_to_TCs[waferID].push_back(i);
        if (verbose_)
            printf("TC %d (detId %d) belongs to waferID %d\n", i, tc.detId(), waferID);
    }

    if (verbose_)
        printf("\n");

    auto waferInfos = std::make_unique<std::vector<CaloML::HGCWaferInfo>>();
    for (const auto& kvpair : wafer_to_TCs) {
        CaloML::HGCWaferInfo info;
        info.waferID = kvpair.first;
        info.TCindices = kvpair.second;
        waferInfos->push_back(info);
        if (verbose_)
            printf("Built wafer with %lu TCs\n", info.TCindices.size());
    }

    evt.put(std::move(waferInfos));
}

DEFINE_FWK_MODULE(HGCWaferInfoProducer);