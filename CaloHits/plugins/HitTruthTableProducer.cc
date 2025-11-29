#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/Common/interface/View.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/ForwardDetId/interface/HGCalDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCScintillatorDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCSiliconDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCalTriggerDetId.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"
#include "DataFormats/CaloRecHit/interface/CaloRecHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "DataFormats/HGCRecHit/interface/HGCRecHit.h" 
#include "DataFormats/L1THGCal/interface/HGCalTriggerCell.h"
#include "CaloML/DataFormats/interface/HitTruthInfo.h"

#include <algorithm>
#include <vector>
#include <iostream>

class HitTruthTableProducer : public edm::stream::EDProducer<> {
public:
HitTruthTableProducer(edm::ParameterSet const& params)
      : name_(params.getParameter<std::string>("name")),
        doc_(params.getParameter<std::string>("doc")),
        src_(consumes<edm::View<CaloML::HitTruthInfo>>(params.getParameter<edm::InputTag>("src"))) {
    produces<nanoaod::FlatTable>();
}

  ~HitTruthTableProducer() override {}

  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override {
    edm::Handle<edm::View<CaloML::HitTruthInfo>> hits;
    iEvent.getByToken(src_, hits);
    
    std::vector<float> simenergies;
    std::vector<int> nClusters;
    std::vector<int> cluster0, cluster1, cluster2, cluster3;
    std::vector<float> frac0, frac1, frac2, frac3;

    for (const auto& hit : *hits){
        simenergies.push_back(hit.simenergy);
        nClusters.push_back(hit.simclusters.size());

        if (hit.simclusters.size() > 0){
            cluster0.push_back(hit.simclusters[0]);
            frac0.push_back(hit.fracs[0]);
        } else {
            cluster0.push_back(-1);
            frac0.push_back(0.0f);
        }

        if (hit.simclusters.size() > 1){
            cluster1.push_back(hit.simclusters[1]);
            frac1.push_back(hit.fracs[1]);
        } else {
            cluster1.push_back(-1);
            frac1.push_back(0.0f);
        }

        if (hit.simclusters.size() > 2){
            cluster2.push_back(hit.simclusters[2]);
            frac2.push_back(hit.fracs[2]);
        } else {
            cluster2.push_back(-1);
            frac2.push_back(0.0f);
        }

        if (hit.simclusters.size() > 3){
            cluster3.push_back(hit.simclusters[3]);
            frac3.push_back(hit.fracs[3]);
        } else {
            cluster3.push_back(-1);
            frac3.push_back(0.0f);
        }
    }

    auto tab = std::make_unique<nanoaod::FlatTable>(hits->size(), name_, false, true);
    tab->addColumn<float>("simenergy", simenergies, "Simulated energy associated to the hit");
    tab->addColumn<int>("nClusters", nClusters, "Number of simclusters contributing to the hit");
    tab->addColumn<int>("cluster0", cluster0, "Index of the simcluster contributing the most to the hit");
    tab->addColumn<float>("frac0", frac0, "Fraction of energy contributed by simcluster0");
    tab->addColumn<int>("cluster1", cluster1, "Index of the simcluster contributing the second most to the hit");
    tab->addColumn<float>("frac1", frac1, "Fraction of energy contributed by simcluster1");
    tab->addColumn<int>("cluster2", cluster2, "Index of the simcluster contributing the third most to the hit");
    tab->addColumn<float>("frac2", frac2, "Fraction of energy contributed by simcluster2");
    tab->addColumn<int>("cluster3", cluster3, "Index of the simcluster contributing the fourth most to the hit");
    tab->addColumn<float>("frac3", frac3, "Fraction of energy contributed by simcluster3");

    iEvent.put(std::move(tab));
  }

protected:
  const std::string name_, doc_;
  edm::EDGetTokenT<edm::View<CaloML::HitTruthInfo>> src_;
};

DEFINE_FWK_MODULE(HitTruthTableProducer);