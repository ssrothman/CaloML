#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"
#include "Geometry/HcalCommonData/interface/HcalHitRelabeller.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/HcalCommonData/interface/HcalDDDRecConstants.h"
#include "Geometry/Records/interface/HcalRecNumberingRecord.h"
#include "DataFormats/Common/interface/View.h"

class RelabelledHcalSimHitsProducer : public edm::stream::EDProducer<> {
public:
    explicit RelabelledHcalSimHitsProducer(const edm::ParameterSet& params) :
        src_(consumes<edm::View<PCaloHit>>(params.getParameter<edm::InputTag>("src"))),
        hdrcToken_(esConsumes<edm::Transition::BeginRun>()) {

        produces<std::vector<PCaloHit>>();
    }
    
    void beginRun(const edm::Run& iRun, const edm::EventSetup& iSetup) override {
        pHRNDC_ = iSetup.getHandle(hdrcToken_);
    }

    void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override{

        auto result = std::make_unique<std::vector<PCaloHit>>();
        edm::Handle<edm::View<PCaloHit>> hits;
        iEvent.getByToken(src_, hits);

        for (const auto& hit : *hits){
            DetId oldId(hit.id());
            DetId newId = HcalHitRelabeller::relabel(oldId, pHRNDC_.product());

            PCaloHit relabelledHit(
                newId.rawId(),
                hit.energy(),
                hit.time(),
                hit.geantTrackId(),
                hit.energyEM()/hit.energy(),
                hit.depth()
            );
            relabelledHit.setEventId(hit.eventId());
            result->push_back(relabelledHit);
        }

        iEvent.put(std::move(result));
    }

private:
    edm::EDGetToken src_;

    edm::ESGetToken<HcalDDDRecConstants, HcalRecNumberingRecord> hdrcToken_;
    edm::ESHandle<HcalDDDRecConstants> pHRNDC_;
};

DEFINE_FWK_MODULE(RelabelledHcalSimHitsProducer);
