#include "CaloML/CaloHits/interface/HitPositionTableProducer.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"

#include "DataFormats/CaloRecHit/interface/CaloRecHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHit.h"

#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/EcalAlgo/interface/EcalPreshowerGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/HGCRecHit/interface/HGCRecHitCollections.h"
#include "RecoLocalCalo/HGCalRecAlgos/interface/RecHitTools.h"
#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalDetId/interface/ESDetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
#include "DataFormats/HcalRecHit/interface/HORecHit.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"

template <typename T>
class CaloHitPositionTableProducer : public HitPositionTableProducer<edm::View<T>> {
public:
  CaloHitPositionTableProducer(edm::ParameterSet const& params)
      : HitPositionTableProducer<edm::View<T>>(params),
        caloGeoToken_(edm::stream::EDProducer<>::esConsumes<edm::Transition::BeginRun>()) { }

  ~CaloHitPositionTableProducer() override {}

  GlobalPoint positionFromHit(const CaloRecHit& hit) { 
    DetId detId = hit.detid();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const PCaloHit& hit) { 
    DetId detId = hit.id();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const reco::PFRecHit& hit) { 
    DetId detId = hit.detId();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const EcalRecHit& hit) { 
    DetId detId = hit.detid();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const HBHERecHit& hit) { 
    DetId detId = hit.detid();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const HFRecHit& hit) { 
    DetId detId = hit.detid();
    return positionFromDetId(detId); 
  }

  GlobalPoint positionFromHit(const HORecHit& hit) { 
    DetId detId = hit.detid();
    return positionFromDetId(detId); 
  }

  float radiusFromHit(const CaloRecHit& hit) {
    return radiusFromDetId(hit.detid()); 
  }

  float radiusFromHit(const PCaloHit& hit) {
    return radiusFromDetId(hit.id()); 
  }

  float radiusFromHit(const reco::PFRecHit& hit) {
    return radiusFromDetId(hit.detId()); 
  }

  float radiusFromHit(const EcalRecHit& hit) {
    return radiusFromDetId(hit.detid()); 
  }

  float radiusFromHit(const HBHERecHit& hit) {
    return radiusFromDetId(hit.detid()); 
  }

  float radiusFromHit(const HFRecHit& hit) {
    return radiusFromDetId(hit.detid()); 
  }

  float radiusFromHit(const HORecHit& hit) {
    return radiusFromDetId(hit.detid()); 
  }

  void beginRun(const edm::Run&, const edm::EventSetup& iSetup) override {
    geometry_ = &iSetup.getData(caloGeoToken_);
  }

  GlobalPoint positionFromDetId(DetId id) {
    DetId::Detector det = id.det();
    if (det == DetId::Ecal) {
        EcalSubdetector subdet = static_cast<EcalSubdetector>(id.subdetId());
        if (subdet == EcalBarrel){
            EBDetId ebId(id);
            const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalBarrel);
            return cellGeometry->getGeometry(ebId)->getPosition();
        } else if(subdet == EcalEndcap){
            EEDetId eeId(id);
            const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalEndcap);
            return cellGeometry->getGeometry(eeId)->getPosition();
        } else if (subdet == EcalPreshower){
            ESDetId esId(id); 
            const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalPreshower);
            return cellGeometry->getGeometry(esId)->getPosition();
        } else {
            throw cms::Exception("CaloHitPositionTableProducer") << "Unsupported Ecal subdetector type " << subdet;
        }
    } else if (det == DetId::Hcal) {
        HcalDetId hcalId(id);
        const HcalGeometry *cellGeometry = dynamic_cast<const HcalGeometry *>(geometry_->getSubdetectorGeometry(hcalId));
        return cellGeometry->getPosition(hcalId);
    } else {
      throw cms::Exception("CaloHitPositionTableProducer") << "Unsupported DetId type" << det;
    }
  }

  float radiusFromDetId(DetId id) {
    return 0.;
  }

protected:
  edm::ESGetToken<CaloGeometry, CaloGeometryRecord> caloGeoToken_;
  const CaloGeometry* geometry_;
};

#include "FWCore/Framework/interface/MakerMacros.h"
typedef CaloHitPositionTableProducer<EcalRecHit> EcalRecHitPositionTableProducer;
typedef CaloHitPositionTableProducer<HBHERecHit> HBHERecHitPositionTableProducer;
typedef CaloHitPositionTableProducer<HFRecHit> HFRecHitPositionTableProducer;
typedef CaloHitPositionTableProducer<HORecHit> HORecHitPositionTableProducer;

typedef CaloHitPositionTableProducer<CaloRecHit> CaloRecHitPositionTableProducer;
typedef CaloHitPositionTableProducer<reco::PFRecHit> CaloPFRecHitPositionTableProducer;
typedef CaloHitPositionTableProducer<PCaloHit> CaloSimHitPositionTableProducer;

DEFINE_FWK_MODULE(EcalRecHitPositionTableProducer);
DEFINE_FWK_MODULE(HBHERecHitPositionTableProducer);
DEFINE_FWK_MODULE(HFRecHitPositionTableProducer);
DEFINE_FWK_MODULE(HORecHitPositionTableProducer);

DEFINE_FWK_MODULE(CaloRecHitPositionTableProducer);
DEFINE_FWK_MODULE(CaloPFRecHitPositionTableProducer);
DEFINE_FWK_MODULE(CaloSimHitPositionTableProducer);
