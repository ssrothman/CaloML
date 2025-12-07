import FWCore.ParameterSet.Config as cms

def setupGenParticlesTables(process):
    process.genParticleTable.externalVariables = cms.PSet()
    process.genParticleTable.src = cms.InputTag('genParticles')
    process.schedule.associate(process.genParticleTablesTask)
    process.schedule.associate(process.genVertexTablesTask)

    return process