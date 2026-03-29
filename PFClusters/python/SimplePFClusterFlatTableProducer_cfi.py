import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]
from PhysicsTools.NanoAOD.common_cff import Var # pyright: ignore[reportMissingImports]

SimplePFClusterFlatTableProducer = cms.EDProducer(
    "SimplePFClusterFlatTableProducer",
    src = cms.InputTag("particleFlowClusterHCAL"),
    name = cms.string("pfCluster"),
    doc = cms.string("Table of reco::PFCluster objects"),
    cut = cms.string(""),
    variables = cms.PSet(
        energy = Var("energy", "float", doc="Energy of the PFCluster"),
        eta = Var("eta", "float", doc="Eta of the PFCluster position"),
        phi = Var("phi", "float", doc="Phi of the PFCluster position"),
        pt = Var("pt", "float", doc="Transverse momentum of the PFCluster"),
        x = Var("x", "float", doc="X position of the PFCluster"),
        y = Var("y", "float", doc="Y position of the PFCluster"),
        z = Var("z", "float", doc="Z position of the PFCluster"),
        layer = Var("layer", "int", doc="Layer of the PFCluster"),
        depth = Var('depth', float, doc="Depth of the PFCluster"),
        time = Var('time', float, doc="Time of the PFCluster"),
        nHits = Var('hitsAndFractions.size()', 'int', doc="Number of hits in the PFCluster"),
    ),
)
