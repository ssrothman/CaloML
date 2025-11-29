#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/Common/interface/View.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/ForwardDetId/interface/HGCScintillatorDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCSiliconDetId.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"
#include "DataFormats/CaloRecHit/interface/CaloRecHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
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

#include <vector>
#include <iostream>

template <typename T>
class CaloHitPropertiesTableProducer : public edm::stream::EDProducer<> {
public:
  CaloHitPropertiesTableProducer(edm::ParameterSet const& params)
      : name_(params.getParameter<std::string>("name")), 
        doc_(params.getParameter<std::string>("doc")),
        cut_(params.getParameter<std::string>("cut"), true) {
    produces<nanoaod::FlatTable>();

    const std::vector<edm::InputTag> srctags = params.getParameter<std::vector<edm::InputTag>>("src");
    for (const auto& tag : srctags) {
        srcs_.emplace_back(consumes<T>(tag));
    }
  }

  ~CaloHitPropertiesTableProducer() override {}

  uint32_t detIdFromHit(const PCaloHit& hit) { 
    return hit.id();
  }

  uint32_t detIdFromHit(const CaloRecHit& hit) { 
    return hit.detid();
  }

  uint32_t detIdFromHit(const reco::PFRecHit& hit) { 
    return hit.detId();
  }

  uint32_t detIdFromHit(const EcalRecHit& hit) { 
    return hit.detid();
  }

  uint32_t detIdFromHit(const HBHERecHit& hit) { 
    return hit.detid();
  }

  uint32_t detIdFromHit(const HFRecHit& hit) { 
    return hit.detid();
  }

  uint32_t detIdFromHit(const HORecHit& hit) { 
    return hit.detid();
  }

  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override {
    edm::Handle<T> objs;

    std::vector<int> dets, subdets;
    std::vector<float> energies, times;

    for (const auto& src : srcs_){
        iEvent.getByToken(src, objs);

        for (const auto& obj : *objs) {
            if (cut_(obj)) {
                DetId detid(detIdFromHit(obj));
                DetId::Detector det = detid.det();

                dets.push_back(det);
                energies.push_back(obj.energy());
                times.push_back(obj.time());

                if (det == DetId::Ecal){
                    EcalSubdetector subdet = static_cast<EcalSubdetector>(detid.subdetId());
                    subdets.push_back(subdet);
                } else if (det == DetId::Hcal){
                    HcalDetId hcalId(detid);
                    subdets.push_back(hcalId.subdet());
                } else {
                    throw cms::Exception("CaloHitPropertiesTableProducer") << "Unsupported DetId type" << detid.det();
                }
            }
        }
    }

    auto tab = std::make_unique<nanoaod::FlatTable>(subdets.size(), name_, false, false);
    tab->addColumn<int>("subdet", subdets, "Subdetector ID");
    tab->addColumn<int>("det", dets, "Detector ID");
    tab->addColumn<float>("energy", energies, "Hit energy");
    tab->addColumn<float>("time", times, "Hit time");

    iEvent.put(std::move(tab));
  }

protected:
  const std::string name_, doc_;
  std::vector<edm::EDGetTokenT<T>> srcs_;
  const StringCutObjectSelector<typename T::value_type> cut_;
};

typedef CaloHitPropertiesTableProducer<edm::View<PCaloHit>> CaloSimHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<CaloRecHit>> CaloCaloRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<reco::PFRecHit>> CaloPFRecHitPropertiesTableProducer;

typedef CaloHitPropertiesTableProducer<edm::View<EcalRecHit>> EcalRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<HBHERecHit>> HBHERecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<HFRecHit>> HFRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<HORecHit>> HORecHitPropertiesTableProducer;

DEFINE_FWK_MODULE(CaloSimHitPropertiesTableProducer);
DEFINE_FWK_MODULE(CaloCaloRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(CaloPFRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(EcalRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HBHERecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HFRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HORecHitPropertiesTableProducer);