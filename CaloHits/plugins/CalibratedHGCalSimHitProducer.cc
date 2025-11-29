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
#include "L1Trigger/L1THGCal/interface/HGCalTriggerGeometryBase.h"
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
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerTools.h"

#include <vector>
#include <iostream>

class CalibratedHGCalSimHitProducer : public edm::stream::EDProducer<> {
public:
  CalibratedHGCalSimHitProducer(edm::ParameterSet const& params) 
    : keV2fC_(params.getParameter<double>("keV2fC")),
      fcPerMip_(params.getParameter<std::vector<double>>("fcPerMip")),
      layerWeights_(params.getParameter<std::vector<double>>("layerWeights")),
      thicknessCorrections_(params.getParameter<std::vector<double>>("thicknessCorrections")),
      triggerGeomToken_(esConsumes<HGCalTriggerGeometryBase, CaloGeometryRecord, edm::Transition::BeginRun>()) 
  {
    
    const std::vector<edm::InputTag> srctags = params.getParameter<std::vector<edm::InputTag>>("src");
    for (const auto& tag : srctags) {
        srcTokens_.emplace_back(consumes<edm::View<PCaloHit>>(tag));
    } 

    produces<std::vector<PCaloHit>>();
  }

  ~CalibratedHGCalSimHitProducer() override {}

  void beginRun(const edm::Run& run, const edm::EventSetup& es) {
    const auto& triggerGeometry = es.getHandle(triggerGeomToken_);
    triggerTools_.setGeometry(triggerGeometry.product());
  }


  double calibrate(double energy, unsigned thickness, unsigned layer){
    double layerWeight = layerWeights_[layer];
    if (thickness == 3){//thickness 3 = scintillator
        return energy  * layerWeight / 0.48;  //ad hoc?
    }
    double thicknessCorrection = thicknessCorrections_[thickness];
    double fcPerMip = fcPerMip_[thickness];
    double TeV2GeV = 1000.0;
    return energy * keV2fC_ / fcPerMip * layerWeight * TeV2GeV / thicknessCorrection;
  }

  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override {
    std::vector<edm::Handle<edm::View<PCaloHit>>> hits_handles;
    hits_handles.resize(srcTokens_.size());
    for (size_t i = 0; i < srcTokens_.size(); ++i) {
        iEvent.getByToken(srcTokens_[i], hits_handles[i]);  
    }

    auto calibratedHits = std::make_unique<std::vector<PCaloHit>>();

    for (const auto& handle : hits_handles){
        for (const auto& hit : *handle){
            float E = hit.energy();
            unsigned thickness = triggerTools_.thicknessIndex(hit.id());
            unsigned layer = triggerTools_.layerWithOffset(hit.id());
    
            double calibratedE = calibrate(E, thickness, layer);

            PCaloHit calibratedHit(hit);
            calibratedHit.setEnergy(calibratedE);

            calibratedHits->push_back(calibratedHit);
        }
    }
    iEvent.put(std::move(calibratedHits));
  }

protected:
  std::vector<edm::EDGetTokenT<edm::View<PCaloHit>>> srcTokens_;

  double keV2fC_;
  std::vector<double> fcPerMip_;
  std::vector<double> layerWeights_;
  std::vector<double> thicknessCorrections_;

  edm::ESGetToken<HGCalTriggerGeometryBase, CaloGeometryRecord> triggerGeomToken_;

  HGCalTriggerTools triggerTools_;
};

DEFINE_FWK_MODULE(CalibratedHGCalSimHitProducer);
