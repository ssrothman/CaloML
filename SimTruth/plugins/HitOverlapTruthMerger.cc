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

class HitOverlapTruthMerger : public edm::stream::EDProducer<> {
public:
    explicit HitOverlapTruthMerger(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
    double computeOverlap(
            const std::unordered_map<uint32_t, double>& cluster1,
            const std::unordered_map<uint32_t, double>& cluster2,
            const std::set<uint32_t>& detIds1,
            const std::set<uint32_t>& detIds2);

    edm::EDGetToken simclusters_token_;
    edm::EDGetToken simclusterinfos_token_;
    std::vector<edm::EDGetToken> simhits_tokens_;

    double overlapThreshold_;

    int verbose_;
};


HitOverlapTruthMerger::HitOverlapTruthMerger(const edm::ParameterSet& conf)
    : simclusters_token_(consumes<std::vector<SimCluster>>(conf.getParameter<edm::InputTag>("simclusters"))),
      simclusterinfos_token_(consumes<std::vector<CaloML::MergedSimClusterInfo>>(conf.getParameter<edm::InputTag>("simclusterInfos"))),
      overlapThreshold_(conf.getParameter<double>("overlapThreshold")),
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

double HitOverlapTruthMerger::computeOverlap(
        const std::unordered_map<uint32_t, double>& cluster1,
        const std::unordered_map<uint32_t, double>& cluster2,
        const std::set<uint32_t>& detIds1,
        const std::set<uint32_t>& detIds2) {

    std::set<uint32_t> commonDetIds;
    std::set_intersection(
        detIds1.begin(), detIds1.end(),
        detIds2.begin(), detIds2.end(),
        std::inserter(commonDetIds, commonDetIds.begin())
    );
    double overlapEnergy1 = 0.0;
    double overlapEnergy2 = 0.0;
    for (uint32_t detId : commonDetIds) {
        overlapEnergy1 += cluster1.at(detId);
        overlapEnergy2 += cluster2.at(detId);
    }

    double totalEnergy1 = 0.0;
    for (const auto& kvpair : cluster1) {
        totalEnergy1 += kvpair.second;
    }

    double totalEnergy2 = 0.0;
    for (const auto& kvpair : cluster2) {
        totalEnergy2 += kvpair.second;
    }

    return std::max(
        overlapEnergy1 / totalEnergy1, 
        overlapEnergy2 / totalEnergy2
    );
}

void HitOverlapTruthMerger::produce(edm::Event& evt, const edm::EventSetup& es) {
    // Get the simhits
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

    std::vector<std::unordered_map<uint32_t, double>> clusterHitEnergies;
    clusterHitEnergies.reserve(simclusters.size());
    std::vector<std::set<uint32_t>> clusterDetIds;
    clusterDetIds.reserve(simclusters.size());
    for(const auto& simcluster : simclusters){
        std::unordered_map<uint32_t, double> hitEnergies;
        std::set<uint32_t> detIds;
        for(const auto& hit : simcluster.hits_and_fractions()){
            auto it = totalEnergies.find(hit.first);
            double detE = (it!=totalEnergies.end()) ? it->second : 0.0;
            hitEnergies[hit.first] += hit.second * detE;
            detIds.insert(hit.first);
        }
        clusterHitEnergies.push_back(hitEnergies);
        clusterDetIds.push_back(detIds);
    }

    std::vector<std::set<uint32_t>> adjacencies;
    adjacencies.resize(simclusters.size());
    if (overlapThreshold_ >= 0.0) {
        for (size_t i=0; i<simclusters.size(); ++i){
            for(size_t j=i+1; j<simclusters.size(); ++j){
                double overlap = computeOverlap(
                    clusterHitEnergies[i], clusterHitEnergies[j],
                    clusterDetIds[i], clusterDetIds[j]
                );

                if (overlap > overlapThreshold_){
                    adjacencies[i].insert(j);
                    adjacencies[j].insert(i);
                }
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
            CaloML::MergedSimClusterInfo mergedInfo = CaloML::mergeSimClusterInfos(simclusterinfos, component,
                CaloML::MERGE_REASON::OVERLAP);

            mergedClusters->push_back(newcluster);
            mergedTracks->push_back(mergedTrack);
            mergedClusterInfos->push_back(mergedInfo);
        }
    }

    evt.put(std::move(mergedClusters), "mergedSimClusters");
    evt.put(std::move(mergedTracks), "mergedSimTracks");
    evt.put(std::move(mergedClusterInfos), "mergedSimClusterInfos");
}

void HitOverlapTruthMerger::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("simclusters", edm::InputTag(""));
    desc.add<edm::InputTag>("simclusterInfos", edm::InputTag(""));
    desc.add<std::vector<edm::InputTag>>("simhits", std::vector<edm::InputTag>());
    desc.add<double>("overlapThreshold", -1.0);
    desc.add<int>("verbose", 0);
    descriptions.add("hitOverlapTruthMerger", desc);
}

DEFINE_FWK_MODULE(HitOverlapTruthMerger);
