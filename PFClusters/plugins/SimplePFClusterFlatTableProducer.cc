#include "PhysicsTools/NanoAOD/interface/SimpleFlatTableProducer.h"
#include "DataFormats/ParticleFlowReco/interface/PFCluster.h"

#include "DataFormats/CaloRecHit/interface/CaloCluster.h"
typedef SimpleFlatTableProducer<reco::PFCluster> SimplePFClusterFlatTableProducer;

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(SimplePFClusterFlatTableProducer);    