import FWCore.ParameterSet.Config as cms
import math

def customize_particle_gun(process):
    process.generator = cms.EDProducer("FlatRandomPtGunProducer",
        PGunParameters = cms.PSet(
            PartID=cms.vint32(15),
            nParticles=cms.int32(1),
            exactShoot=cms.bool(False),
            randomShoot=cms.bool(False),
            MinPt=cms.double(5.0),
            MaxPt=cms.double(200.0),
            MinPhi=cms.double(-math.pi),
            MaxPhi=cms.double(math.pi),
            MinEta=cms.double(0),
            MaxEta=cms.double(1.7),
        ),
        AddAntiParticle = cms.bool(True),
        debug=cms.untracked.bool(True),
        firstRun=cms.untracked.uint32(1)
    )

    return process

## extra customization
#process.generator.PGunParameters.ParticleID = cms.vint32(211)
#process.generator.PGunParameters.MinEta = cms.double(0)
#process.generator.PGunParameters.MaxEta = cms.double(3.0)
#process.maxEvents.input = 500
#process.FEVTDEBUGoutput.fileName = 'GSD_Run3_Gun.root'
