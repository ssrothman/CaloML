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

#include "CaloML/CaloHits/interface/util.h"

#include <vector>
#include <iostream>

template <typename T, unsigned DET>
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

  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override {
    edm::Handle<T> objs;

    std::vector<int> dets, subdets;
    std::vector<float> energies, times;

    //only used for HCAL hits
    std::vector<int> depths;

    for (const auto& src : srcs_){
        iEvent.getByToken(src, objs);

        for (const auto& obj : *objs) {
            if (cut_(obj)) {
                DetId detid(CaloML::detIdFromHit(obj));
                DetId::Detector det = detid.det();

                if (det != DET && DET != 0){
                    throw cms::Exception("CaloHitPropertiesTableProducer") << "Hit DetId does not match configured detector type";
                }

                dets.push_back(det);
                energies.push_back(obj.energy());
                times.push_back(obj.time());
                subdets.push_back(detid.subdetId()); 

                if constexpr(DET == DetId::Hcal){
                    HcalDetId hdetid(detid);
                    depths.push_back(hdetid.depth());
                }
            }
        }
    }

    auto tab = std::make_unique<nanoaod::FlatTable>(subdets.size(), name_, false, false);
    tab->addColumn<int>("subdet", subdets, "Subdetector ID");
    tab->addColumn<int>("det", dets, "Detector ID");
    tab->addColumn<float>("energy", energies, "Hit energy");
    tab->addColumn<float>("time", times, "Hit time");

    if constexpr(DET == DetId::Hcal){
        tab->addColumn<int>("depth", depths, "HCal depth");
    }
    iEvent.put(std::move(tab));
  }

protected:
  const std::string name_, doc_;
  std::vector<edm::EDGetTokenT<T>> srcs_;
  const StringCutObjectSelector<typename T::value_type> cut_;
};

typedef CaloHitPropertiesTableProducer<edm::View<PCaloHit>, 0> GenericSimHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<CaloRecHit>, 0> GenericCaloRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<reco::PFRecHit>, 0> GenericPFRecHitPropertiesTableProducer;

typedef CaloHitPropertiesTableProducer<edm::View<PCaloHit>, DetId::Detector::Ecal> EcalSimHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<CaloRecHit>, DetId::Detector::Ecal> EcalCaloRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<reco::PFRecHit>, DetId::Detector::Ecal> EcalPFRecHitPropertiesTableProducer;

typedef CaloHitPropertiesTableProducer<edm::View<PCaloHit>, DetId::Detector::Hcal> HcalSimHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<CaloRecHit>, DetId::Detector::Hcal> HcalCaloRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<reco::PFRecHit>, DetId::Detector::Hcal> HcalPFRecHitPropertiesTableProducer;

typedef CaloHitPropertiesTableProducer<edm::View<EcalRecHit>, DetId::Detector::Ecal> EcalRecHitPropertiesTableProducer;

typedef CaloHitPropertiesTableProducer<edm::View<HBHERecHit>, DetId::Detector::Hcal> HBHERecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<HFRecHit>, DetId::Detector::Hcal> HFRecHitPropertiesTableProducer;
typedef CaloHitPropertiesTableProducer<edm::View<HORecHit>, DetId::Detector::Hcal> HORecHitPropertiesTableProducer;

DEFINE_FWK_MODULE(GenericSimHitPropertiesTableProducer);
DEFINE_FWK_MODULE(GenericCaloRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(GenericPFRecHitPropertiesTableProducer);

DEFINE_FWK_MODULE(EcalSimHitPropertiesTableProducer);
DEFINE_FWK_MODULE(EcalCaloRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(EcalPFRecHitPropertiesTableProducer);

DEFINE_FWK_MODULE(HcalSimHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HcalCaloRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HcalPFRecHitPropertiesTableProducer);

DEFINE_FWK_MODULE(EcalRecHitPropertiesTableProducer);

DEFINE_FWK_MODULE(HBHERecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HFRecHitPropertiesTableProducer);
DEFINE_FWK_MODULE(HORecHitPropertiesTableProducer);