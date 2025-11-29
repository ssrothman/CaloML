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
#include "SimCalorimetry/HcalSimAlgos/interface/HcalSimParameterMap.h"

class CalibratedHcalSimHitsProducer : public edm::stream::EDProducer<> {
public:
    explicit CalibratedHcalSimHitsProducer(const edm::ParameterSet& params) :
        src_(consumes<edm::View<PCaloHit>>(params.getParameter<edm::InputTag>("src"))),
        fSimParameterMap(params.getParameter<edm::ParameterSet>("HcalSimParameters")) {

        produces<std::vector<PCaloHit>>();
    }
    
    void beginRun(const edm::Run& iRun, const edm::EventSetup& iSetup) override {

    }

    double calibate(const PCaloHit& hit){
        HcalDetId iDetId(hit.id());

        double samplingFactor = 1;
        if(iDetId.subdet() == HcalBarrel) {
          samplingFactor = fSimParameterMap.hbParameters().samplingFactor(iDetId);
        } else if(iDetId.subdet() == HcalEndcap) {
            samplingFactor = fSimParameterMap.heParameters().samplingFactor(iDetId);
        } else if(iDetId.subdet() == HcalOuter) {
            samplingFactor = fSimParameterMap.hoParameters().samplingFactor(iDetId);
        } else if(iDetId.subdet() == HcalForward) {
            // I don't understand this. Copied logic from https://github.com/cms-sw/cmssw/blob/CMSSW_15_0_6/SimCalorimetry/HcalSimAlgos/src/HcalSimParameterMap.cc#L49-L53
            // No parameters because HF has only a global sampling factor?
            if (iDetId.depth() == 1 || iDetId.depth() == 3){
                samplingFactor = fSimParameterMap.hfParameters1().samplingFactor();
            } else {
                samplingFactor = fSimParameterMap.hfParameters2().samplingFactor();
            }
        } else {
            throw cms::Exception("CalibratedHcalSimHitsProducer") << "Unknown subdetector for HcalDetId: " << iDetId.subdet();
        }

        return hit.energy() * samplingFactor;
    }

    void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override{
        auto result = std::make_unique<std::vector<PCaloHit>>();
        edm::Handle<edm::View<PCaloHit>> hits;
        iEvent.getByToken(src_, hits);

        for (const auto& hit : *hits){
            double newE = calibate(hit);
            
            PCaloHit calibratedHit(
                hit.id(),
                newE,
                hit.time(),
                hit.geantTrackId(),
                hit.energyEM()/hit.energy(),
                hit.depth()
            );
            calibratedHit.setEventId(hit.eventId());
            result->push_back(calibratedHit);
        }

        iEvent.put(std::move(result));
    }

private:
    edm::EDGetToken src_;

    HcalSimParameterMap fSimParameterMap;
};

DEFINE_FWK_MODULE(CalibratedHcalSimHitsProducer);
