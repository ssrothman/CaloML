import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]

from PhysicsTools.NanoAOD.common_cff import Var # pyright: ignore[reportMissingImports]

PFClusterHitsTableProducer = cms.EDProducer(
    "PFClusterHitsTableProducer",
    src = cms.InputTag("particleFlowClusterHCAL"),
    name = cms.string("pfClusterRecHit"),
    doc = cms.string("Table of PFRecHits associated with reco::PFCluster objects"),
    cut = cms.string(""),
)
