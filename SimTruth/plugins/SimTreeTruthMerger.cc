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
#include "CaloML/SimTruth/interface/util.h"


class SimTreeTruthMerger : public edm::stream::EDProducer<> {
public:
    explicit SimTreeTruthMerger(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    void beginRun(const edm::Run&, const edm::EventSetup&) override;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
    uint32_t recursive_find_parent(
            uint32_t startTrackIdx,
            const std::vector<SimTrack>& simTracks,
            const std::vector<SimVertex>& simVertices,
            const std::unordered_map<uint32_t, uint32_t>& geantToIndexMap);

    edm::EDGetToken simtracks_token_;
    edm::EDGetToken simvertices_token_;
    edm::EDGetToken simtrack_infos_token_;
    std::vector<edm::EDGetToken> simhits_tokens_;

    double caloR_;
    double caloZ_;

    int verbose_;
};


SimTreeTruthMerger::SimTreeTruthMerger(const edm::ParameterSet& conf)
    : simtracks_token_(consumes<std::vector<SimTrack>>(conf.getParameter<edm::InputTag>("simtracks"))),
      simvertices_token_(consumes<std::vector<SimVertex>>(conf.getParameter<edm::InputTag>("simvertices"))),
      caloR_(conf.getParameter<double>("caloR")),
      caloZ_(conf.getParameter<double>("caloZ")),
      verbose_(conf.getParameter<int>("verbose"))
{
    const auto& simhits_tags = conf.getParameter<std::vector<edm::InputTag>>("simhits");
    for (const auto& tag : simhits_tags) {
        simhits_tokens_.push_back(consumes<edm::PCaloHitContainer>(tag));
    }

    produces<std::vector<SimCluster>>("mergedSimClusters");
    produces<edm::PCaloHitContainer>("relabeledSimHits");
    produces<std::vector<SimTrack>>("mergedSimTracks");
}

void SimTreeTruthMerger::beginRun(const edm::Run&, const edm::EventSetup& es) {
    //noop
}

uint32_t SimTreeTruthMerger::recursive_find_parent(
        uint32_t startTrackIdx,
        const std::vector<SimTrack>& simTracks,
        const std::vector<SimVertex>& simVertices,
        const std::unordered_map<uint32_t, uint32_t>& geantToIndexMap) {

    const auto& track = simTracks[startTrackIdx];
    int iVert = track.vertIndex();
    if (iVert < 0){
        return startTrackIdx;
    }

    const auto& vertex = simVertices[iVert];
    if (vertex.parentIndex() < 0){
        return startTrackIdx;
    }

    const auto& pos = vertex.position();

    bool vertexPastCaloBoundary = false;
    vertexPastCaloBoundary = std::abs(pos.Z()) > caloZ_;
    vertexPastCaloBoundary |= std::sqrt(pos.X()*pos.X() + pos.Y()*pos.Y()) > caloR_;

    uint32_t parentIdx = geantToIndexMap.at(vertex.parentIndex());
    const auto& parent = simTracks[parentIdx];

    if (verbose_){
        if(vertexPastCaloBoundary){
            printf("Merging back to calorimeter front face.\n");
            printf("\tVertex position: (%g, %g, %g)\n", pos.X(), pos.Y(), pos.Z());
            printf("\tParent: (%g, %g, %g), (%d; %f)\n",
                parent.momentum().pt(),
                parent.momentum().eta(),
                parent.momentum().phi(),
                parent.type(),
                parent.charge()
            );
            printf("\tDaughter: (%g, %g, %g), (%d; %f)\n",
                track.momentum().pt(),
                track.momentum().eta(),
                track.momentum().phi(),
                track.type(),
                track.charge()
            );
        } else {
            printf("Not merging parent and daughter.\n");
            printf("\tVertex position: (%g, %g, %g)\n",
                    pos.X(), pos.Y(), pos.Z());
            printf("\tParent: (%g, %g, %g), (%d; %f)\n",
                    parent.momentum().pt(),
                    parent.momentum().eta(),
                    parent.momentum().phi(),
                    parent.type(),
                    parent.charge()
            );
            printf("\tDaughter: (%g, %g, %g), (%d; %f)\n",
                    track.momentum().pt(),
                    track.momentum().eta(),
                    track.momentum().phi(),
                    track.type(),
                    track.charge()
            );
        }
    }

    if (vertexPastCaloBoundary){
        return recursive_find_parent(
            geantToIndexMap.at(vertex.parentIndex()),
            simTracks, 
            simVertices,
            geantToIndexMap
        );
    } else {
        return startTrackIdx;
    }
}

void SimTreeTruthMerger::produce(edm::Event& evt, const edm::EventSetup& es) {
    // Get the simtracks
    edm::Handle<std::vector<SimTrack>> simtracks_h;
    evt.getByToken(simtracks_token_, simtracks_h);
    const auto& simtracks = *simtracks_h;

    // Get the simvertices
    edm::Handle<std::vector<SimVertex>> simvertices_h;
    evt.getByToken(simvertices_token_, simvertices_h);
    const auto& simvertices = *simvertices_h;

    // Get the simhits
    std::vector<edm::PCaloHitContainer> simhits;
    for (const auto& token : simhits_tokens_) {
        edm::Handle<edm::PCaloHitContainer> simhits_h;
        evt.getByToken(token, simhits_h);
        simhits.push_back(*simhits_h);
    }

    // key: geantTrackId, value: index in simtracks
    std::unordered_map<uint32_t, uint32_t> geantToIndexMap;
    for(size_t i = 0; i < simtracks.size(); ++i){
        geantToIndexMap[simtracks[i].trackId()] = i;
    }

    // key: track index in simtracks vector
    // value: index of the parent track in simtracks vector
    std::unordered_map<uint32_t, uint32_t> trackToParentMap;
    std::set<uint32_t> parentTracks;
    for(size_t i = 0; i < simtracks.size(); ++i){
        uint32_t parentIdx = recursive_find_parent(
            i, simtracks, simvertices, 
            geantToIndexMap
        );
        trackToParentMap[i] = parentIdx;
        parentTracks.insert(parentIdx);
    }

    // key: parent track index in simtracks vector
    // value: indices of child tracks in simtracks vector
    std::unordered_map<uint32_t, std::vector<uint32_t>> parentToChildMap;
    for(size_t i = 0; i < simtracks.size(); ++i){
        parentToChildMap[trackToParentMap[i]].push_back(i);
    }

    // key: track index in simtracks vector
    // value: vector of (i, j) with
    //      i = index of simhit collection in simhits vector
    //      j = index of simhit in the collection
    std::unordered_map<uint32_t, std::vector<std::pair<uint32_t, uint32_t>>> trackToHitsMap;
    // key: det id
    // value: total sim energy
    std::unordered_map<uint32_t, double> detIdToEnergyMap;

    for (size_t i = 0; i < simhits.size(); ++i) {
        const auto& hits = simhits[i];
        for (size_t j=0; j<hits.size(); ++j){
            const auto& hit = hits[j];
            uint32_t trackId = hit.geantTrackId();
            uint32_t trackIdx = geantToIndexMap[trackId];
            uint32_t parentTrackIdx = trackToParentMap[trackIdx];

            trackToHitsMap[parentTrackIdx].emplace_back(i, j);

            // Add energy to the detIdToEnergyMap
            uint32_t detId = hit.id();
            double energy = hit.energy();
            detIdToEnergyMap[detId] += energy;
        }
    }

    auto relabeledSimHits = std::make_unique<edm::PCaloHitContainer>();
    auto mergedclusters = std::make_unique<std::vector<SimCluster>>();
    auto mergedtracks = std::make_unique<std::vector<SimTrack>>();

    for (uint32_t parentTrack : parentTracks){
        const auto& track = simtracks[parentTrack];
        mergedtracks->push_back(track);

        if (trackToHitsMap.find(parentTrack) == trackToHitsMap.end()) {
            continue; // No hits for this parent track
        }

        const auto& hits = trackToHitsMap[parentTrack];

        std::unordered_map<uint32_t, double> detIdToEnergyPerTrack;
        double totalEnergy = 0.0;

        for (const auto& hitkey : hits) {
            const auto& hit = simhits[hitkey.first][hitkey.second];

            PCaloHit newhit(
                    hit.id(),
                    float(hit.energy()),
                    float(hit.time()),
                    track.trackId(),
                    float(hit.energyEM()/hit.energy()),
                    hit.depth());
            newhit.setEventId(hit.eventId());

            relabeledSimHits->push_back(newhit);

            detIdToEnergyPerTrack[hit.id()] += hit.energy();
            totalEnergy += hit.energy();
        }

        // build merged cluster using utility
        auto newcluster = CaloML::makeMergedSimCluster(track, detIdToEnergyPerTrack, detIdToEnergyMap);
        mergedclusters->push_back(newcluster);
    }

    // Put the results into the event
    evt.put(std::move(mergedclusters), "mergedSimClusters");
    evt.put(std::move(relabeledSimHits), "relabeledSimHits");
    evt.put(std::move(mergedtracks), "mergedSimTracks");
}

void SimTreeTruthMerger::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("simtracks", edm::InputTag(""));
    desc.add<edm::InputTag>("simvertices", edm::InputTag(""));
    desc.add<std::vector<edm::InputTag>>("simhits", std::vector<edm::InputTag>());
    desc.add<double>("caloR", 300.0);
    desc.add<double>("caloZ", 300.0);
    desc.add<int>("verbose", 0);
    descriptions.add("simTreeTruthMerger", desc);
}

DEFINE_FWK_MODULE(SimTreeTruthMerger);
