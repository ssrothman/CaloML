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
#include "SimDataFormats/CaloAnalysis/interface/SimCluster.h"
#include "SimDataFormats/Track/interface/SimTrack.h"
#include "SimDataFormats/Vertex/interface/SimVertex.h"

#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "CommonTools/BaseParticlePropagator/interface/RawParticle.h"
#include "CommonTools/BaseParticlePropagator/interface/BaseParticlePropagator.h"
#include "CaloML/SimTruth/interface/util.h"

class ImpactDistanceTruthMerger : public edm::stream::EDProducer<> {
public:
    explicit ImpactDistanceTruthMerger(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    void beginRun(const edm::Run&, const edm::EventSetup&) override;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
    edm::EDGetToken simclusters_token_;
    edm::EDGetToken simclusterinfos_token_;
    std::vector<edm::EDGetToken> simhits_tokens_;

    double caloR_;
    double caloZ_;

    double distanceTol_, dRTol_, dEtaTol_, dPhiTol_;

    int verbose_;
};


ImpactDistanceTruthMerger::ImpactDistanceTruthMerger(const edm::ParameterSet& conf)
    : simclusters_token_(consumes<std::vector<SimCluster>>(conf.getParameter<edm::InputTag>("simclusters"))),
      simclusterinfos_token_(consumes<std::vector<CaloML::MergedSimClusterInfo>>(conf.getParameter<edm::InputTag>("simclusterInfos"))),
      caloR_(conf.getParameter<double>("caloR")),
      caloZ_(conf.getParameter<double>("caloZ")),
      distanceTol_(conf.getParameter<double>("distanceTol")),
      dRTol_(conf.getParameter<double>("dRTol")),
      dEtaTol_(conf.getParameter<double>("dEtaTol")),
      dPhiTol_(conf.getParameter<double>("dPhiTol")),
      verbose_(conf.getParameter<int>("verbose")) 
{
    std::vector<edm::InputTag> simhits_tags = conf.getParameter<std::vector<edm::InputTag>>("simhits");
    for (const auto& tag : simhits_tags) {
        simhits_tokens_.emplace_back(consumes<edm::PCaloHitContainer>(tag));
    }

    produces<std::vector<SimCluster>>("mergedSimClusters");
    produces<std::vector<SimTrack>>("mergedSimTracks");
    produces<std::vector<CaloML::MergedSimClusterInfo>>("mergedSimClusterInfos");
}

void ImpactDistanceTruthMerger::beginRun(const edm::Run&, const edm::EventSetup& es) {
    //noop
}

static double impactDistance(
        const CaloML::SimTrackInfo& info1,
        const CaloML::SimTrackInfo& info2) {

    double dx = info1.caloImpact.X() - info2.caloImpact.X();
    double dy = info1.caloImpact.Y() - info2.caloImpact.Y();
    double dz = info1.caloImpact.Z() - info2.caloImpact.Z();
    double R = std::sqrt(dx*dx + dy*dy + dz*dz);
    return R;
}

static double impactDR(
        const CaloML::SimTrackInfo& info1,
        const CaloML::SimTrackInfo& info2) {

    double dR = reco::deltaR(
        info1.caloImpact.eta(),
        info1.caloImpact.phi(),
        info2.caloImpact.eta(),
        info2.caloImpact.phi()
    );
    return dR;
}

static double impactDEta(
        const CaloML::SimTrackInfo& info1,
        const CaloML::SimTrackInfo& info2) {

    double dEta = std::abs(info1.caloImpact.eta() - info2.caloImpact.eta());
    return dEta;
}

static double impactDPhi(
        const CaloML::SimTrackInfo& info1,
        const CaloML::SimTrackInfo& info2) {

    double dPhi = reco::deltaPhi(
        info1.caloImpact.phi(),
        info2.caloImpact.phi()
    );
    return dPhi;
}


void ImpactDistanceTruthMerger::produce(edm::Event& evt, const edm::EventSetup& es) {
    // Get the simhits (needed for energy maps)
    std::vector<edm::Handle<edm::PCaloHitContainer>> simhits_handles;
    simhits_handles.resize(simhits_tokens_.size());
    for (size_t i = 0; i < simhits_tokens_.size(); ++i) {
        evt.getByToken(simhits_tokens_[i], simhits_handles[i]);
    }

    //get the simclusters
    edm::Handle<std::vector<SimCluster>> simclusters_h;
    evt.getByToken(simclusters_token_, simclusters_h);
    const auto& simclusters = *simclusters_h;

    // Get the simcluster infos
    edm::Handle<std::vector<CaloML::MergedSimClusterInfo>> simclusterinfos_h;
    evt.getByToken(simclusterinfos_token_, simclusterinfos_h);
    const auto& simclusterinfos = *simclusterinfos_h;

    auto totalEnergies = CaloML::buildTotalEnergies(simhits_handles);

    std::vector<std::set<uint32_t>> adjacencies;
    adjacencies.resize(simclusters.size());
    for (size_t i=0; i<simclusters.size(); ++i){
        for(size_t j=i+1; j<simclusters.size(); ++j){
            // Only attempt distance-based merging if both clusters have a single generator particle
            double R = impactDistance(
                simclusterinfos[i].simTrackInfos[0],
                simclusterinfos[j].simTrackInfos[0]
            );
            double dR = impactDR(
                simclusterinfos[i].simTrackInfos[0],
                simclusterinfos[j].simTrackInfos[0]
            );
            double dEta = impactDEta(
                simclusterinfos[i].simTrackInfos[0],
                simclusterinfos[j].simTrackInfos[0]
            );
            double dPhi = impactDPhi(
                simclusterinfos[i].simTrackInfos[0],
                simclusterinfos[j].simTrackInfos[0]
            );

            bool passR = R < distanceTol_;
            bool passDR = dR < dRTol_;
            bool passDEtaPhi = (dEta < dEtaTol_) && (dPhi < dPhiTol_);

            if (passR || passDR || passDEtaPhi) {
                adjacencies[i].insert(j);
                adjacencies[j].insert(i);
            }
        }
    }

    std::vector<bool> visited(simclusters.size(), false);
    std::vector<std::vector<uint32_t>> components;
    //use BFS to find connected components
    for (size_t i = 0; i < simclusters.size(); ++i) {
        if (visited[i]) continue;

        std::vector<uint32_t> component;
        std::queue<uint32_t> queue;
        queue.push(i);
        visited[i] = true;

        while (!queue.empty()) {
            uint32_t current = queue.front();
            queue.pop();
            component.push_back(current);

            for (uint32_t neighbor : adjacencies[current]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.push(neighbor);
                }
            }
        }
        components.push_back(component);
    }

    if (verbose_){
        printf("Clusters:\n");
        for(size_t i=0; i<simclusters.size(); ++i){
            printf("Cluster %zu: ", i);
            printf("(%g, %g, %g), (%d; %f)",
                    simclusters[i].pt(),
                    simclusters[i].eta(),
                    simclusters[i].phi(),
                    simclusters[i].pdgId(),
                    simclusters[i].charge());
            printf("\n");
        }

        printf("Connected components:\n");
        for(const auto& comp : components){
            printf("Component: ");
            for(int idx : comp){
                printf("%d ", idx);
            }
            printf("\n");
        }
    }

    auto mergedClusters = std::make_unique<std::vector<SimCluster>>();
    auto mergedTracks = std::make_unique<std::vector<SimTrack>>();
    auto mergedClusterInfos = std::make_unique<std::vector<CaloML::MergedSimClusterInfo>>();

    for (const auto& component : components) {
        if (component.size() == 1) {
            mergedClusters->push_back(simclusters[component[0]]);
            mergedClusterInfos->push_back(simclusterinfos[component[0]]);
            mergedTracks->push_back(simclusters[component[0]].g4Tracks()[0]);
        } else {
            SimTrack mergedTrack = CaloML::mergeTracksFromComponent(simclusters, component);
            auto mergedHitEnergies = CaloML::computeMergedHitEnergiesForComponent(simclusters, component, totalEnergies);
            SimCluster newcluster = CaloML::makeMergedSimCluster(mergedTrack, mergedHitEnergies, totalEnergies);
            CaloML::MergedSimClusterInfo mergedInfo = CaloML::mergeSimClusterInfos(simclusterinfos, component);
            
            mergedClusterInfos->push_back(mergedInfo);
            mergedClusters->push_back(newcluster);
            mergedTracks->push_back(mergedTrack);
        }
    }

    evt.put(std::move(mergedClusters), "mergedSimClusters");
    evt.put(std::move(mergedTracks), "mergedSimTracks");
    evt.put(std::move(mergedClusterInfos), "mergedSimClusterInfos");
}

void ImpactDistanceTruthMerger::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("simclusters", edm::InputTag(""));
    desc.add<edm::InputTag>("simclusterInfos", edm::InputTag(""));
    desc.add<std::vector<edm::InputTag>>("simhits", std::vector<edm::InputTag>());
    desc.add<double>("caloR", 300.0);
    desc.add<double>("caloZ", 300.0);
    desc.add<double>("distanceTol", 10.0);
    desc.add<double>("dRTol", 0.5);
    desc.add<double>("dEtaTol", 0.2);
    desc.add<double>("dPhiTol", 0.2);
    desc.add<int>("verbose", 0);
    descriptions.add("impactDistanceTruthMerger", desc);
}

DEFINE_FWK_MODULE(ImpactDistanceTruthMerger);
