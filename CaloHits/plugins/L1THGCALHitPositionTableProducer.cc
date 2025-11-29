#include "CaloML/CaloHits/interface/HitPositionTableProducer.h"
#include "DataFormats/ForwardDetId/interface/HGCalDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCScintillatorDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCSiliconDetId.h"
#include "DataFormats/DetId/interface/DetId.h"

#include "DataFormats/CaloRecHit/interface/CaloRecHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHit.h"

#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/HGCalGeometry/interface/HGCalGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/HGCRecHit/interface/HGCRecHitCollections.h"
#include "RecoLocalCalo/HGCalRecAlgos/interface/RecHitTools.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerTools.h"
#include "DataFormats/L1THGCal/interface/HGCalTriggerCell.h"
#include "DataFormats/ForwardDetId/interface/HGCalTriggerDetId.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerGeometryBase.h"

template <typename T>
class L1THGCalHitPositionTableProducer : public HitPositionTableProducer<edm::View<T>> {
public:
  L1THGCalHitPositionTableProducer(edm::ParameterSet const& params)
      : HitPositionTableProducer<edm::View<T>>(params),
        geomToken_(edm::stream::EDProducer<>::esConsumes<edm::Transition::BeginRun>()) {}

  ~L1THGCalHitPositionTableProducer() override {}

  void beginRun(const edm::Run&, const edm::EventSetup& iSetup) override {
    triggerTools_.eventSetup(iSetup, geomToken_);
  }

  float radiusFromHit(const PCaloHit& hit) {
    return 0.;
  }

  float radiusFromHit(const l1t::HGCalTriggerCell& hit) {
    return 0.;
  }

  GlobalPoint positionFromHit(const l1t::HGCalTriggerCell& hit){
    return hit.position();
  }

  GlobalPoint positionFromHit(const PCaloHit& hit) { 
    DetId detId = hit.id();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromDetId(DetId id) {
    DetId::Detector det = id.det();
    if (det == DetId::HGCalTrigger || det == DetId::HGCalHSc){
        return triggerTools_.getTCPosition(id);
    } else {
        throw cms::Exception("L1THGCALHitPositionTableProducer")
            << "Invalid det " << det;
    }
  }

protected:
  const edm::ESGetToken<HGCalTriggerGeometryBase, CaloGeometryRecord> geomToken_;
  HGCalTriggerTools triggerTools_; 
};

#include "FWCore/Framework/interface/MakerMacros.h"
typedef L1THGCalHitPositionTableProducer<PCaloHit> L1THGCalSimHitPositionTableProducer;
typedef L1THGCalHitPositionTableProducer<l1t::HGCalTriggerCell> L1THGCalRecHitPositionTableProducer;

DEFINE_FWK_MODULE(L1THGCalSimHitPositionTableProducer);
DEFINE_FWK_MODULE(L1THGCalRecHitPositionTableProducer);
