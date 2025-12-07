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

class SimTrackInfoBuilder : public edm::stream::EDProducer<> {
public:
    explicit SimTrackInfoBuilder(const edm::ParameterSet&);
    
    void produce(edm::Event&, const edm::EventSetup&) override;
    void beginRun(const edm::Run&, const edm::EventSetup&) override;

private:
    edm::EDGetToken simtracks_token_;
    edm::EDGetToken simvertices_token_;

    double caloR_;
    double caloZ_;
    edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> magfield_token_;
    BaseParticlePropagator propagator_;

    int verbose_;
};


SimTrackInfoBuilder::SimTrackInfoBuilder(const edm::ParameterSet& conf)
    : simtracks_token_(consumes<std::vector<SimTrack>>(conf.getParameter<edm::InputTag>("simtracks"))),
      simvertices_token_(consumes<std::vector<SimVertex>>(conf.getParameter<edm::InputTag>("simvertices"))),
      caloR_(conf.getParameter<double>("caloR")),
      caloZ_(conf.getParameter<double>("caloZ")),
      magfield_token_(esConsumes<MagneticField, IdealMagneticFieldRecord, edm::Transition::BeginRun>()),
      verbose_(conf.getParameter<int>("verbose")) 
{

    produces<std::vector<CaloML::SimTrackInfo>>();

    propagator_.setPropagationConditions(
        caloR_, caloZ_
    ); 
}

void SimTrackInfoBuilder::beginRun(const edm::Run&, const edm::EventSetup& es) {
    edm::ESHandle<MagneticField> magfield;
    magfield = es.getHandle(magfield_token_);
    propagator_.setMagneticField(magfield->inTesla(GlobalPoint(0,0,0)).z());
}

void SimTrackInfoBuilder::produce(edm::Event& evt, const edm::EventSetup& es) {
    //get the simtracks
    edm::Handle<std::vector<SimTrack>> simtracks_h;
    evt.getByToken(simtracks_token_, simtracks_h);
    const auto& simtracks = *simtracks_h;

    // Get the simvertices
    edm::Handle<std::vector<SimVertex>> simvertices_h;
    evt.getByToken(simvertices_token_, simvertices_h);
    const auto& simvertices = *simvertices_h;

    auto simTrackInfos = std::make_unique<std::vector<CaloML::SimTrackInfo>>();

    for (const auto& track : simtracks) {
        const auto& vertex = simvertices[track.vertIndex()];
        RawParticle trackP(
            track.momentum().Px(),
            track.momentum().Py(),
            track.momentum().Pz(),
            track.momentum().E(),
            track.charge()
        );
        trackP.setVertex(
            vertex.position().X(),
            vertex.position().Y(),
            vertex.position().Z(),
            vertex.position().T()
        );
        propagator_.setParticle(trackP);
        propagator_.propagate();
        trackP = propagator_.particle();

        CaloML::SimTrackInfo info;
        info.vtx = math::XYZTLorentzVectorD(
            vertex.position().X(),
            vertex.position().Y(),
            vertex.position().Z(),
            vertex.position().T()  
        );
        info.caloImpact = math::XYZTLorentzVectorD(
            trackP.vertex().X(),
            trackP.vertex().Y(),
            trackP.vertex().Z(),
            trackP.vertex().T()
        );
        info.momentumAtCalo = math::XYZTLorentzVectorD(
            trackP.px(),
            trackP.py(),
            trackP.pz(),
            trackP.E()
        );
        simTrackInfos->push_back(info);
    }

    evt.put(std::move(simTrackInfos));
}

DEFINE_FWK_MODULE(SimTrackInfoBuilder);
