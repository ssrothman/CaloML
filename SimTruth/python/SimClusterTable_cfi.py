import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]
from PhysicsTools.NanoAOD.common_cff import Var # pyright: ignore[reportMissingImports]

SimClusterTable = cms.EDProducer(
    "SimpleSimClusterFlatTableProducer",
    src = cms.InputTag(''),
    name = cms.string(''),
    extension = cms.bool(False),  # this is the main table for the simclusters
    singleton = cms.bool(False),  # the number of entries is variable
    variables = cms.PSet(
        track_pt = Var('pt()', 'float', doc='pt of the simcluster'),
        track_eta = Var('eta()', 'float', doc='eta of the simcluster'),
        track_phi = Var('phi()', 'float', doc='phi of the simcluster'),
        track_energy = Var('energy()', 'float', doc='energy of the simcluster'),
        track_mass = Var('mass()', 'float', doc='mass of the simcluster'),
        track_pdgId = Var('pdgId()', 'int', doc='PDG ID of the simcluster'),
        track_threeCharge = Var('threeCharge()', 'int', doc='3*charge of the simcluster'),

        nSimHits = Var('numberOfRecHits', 'int', doc='number of simhits in the simcluster'),
        simEnergy = Var('simEnergy()', 'float', doc='simulated energy of the simcluster'),
    )
)

