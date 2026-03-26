# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: NANO --filein RECO.root --fileout NANO.root --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --step NANO --geometry ExtendedRun4D110 --conditions auto:phase2_realistic_T33 --era Phase2C17I13M9 --no_exec --python_filename=CaloML/Processing/test/NANO_Run4.py --customise CaloML/Processing/SimTruthSequences_cff.SimTruthSequence_HGCAL,CaloML/Processing/SimTruthSequences_cff.SimTruthSequence_L1THGCAL,CaloML/Processing/HGCalTPG_cff.setupHGCalTPG,CaloML/SimTruth/GenParticles_cff.setupGenParticlesTables --customise_commands=process.schedule.remove(process.nanoAOD_step)
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9

process = cms.Process('NANO',Phase2C17I13M9)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtendedRun4D110Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:/home/submit/srothman/cmsdata/CaloML/testing/RECO_Run4_PiGun_Endcaps.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('NANO nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:/home/submit/srothman/cmsdata/CaloML/testing/NANO_Run4_PiGun_Endcaps.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T33', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

from CaloML.SimTruth.common_cff import * # pyright: ignore[reportMissingImports]
from CaloML.SimTruth.SimTruth_cff import setupSimTruth, setupSimTruthTables # pyright: ignore[reportMissingImports]
from CaloML.CaloHits.SimHits_cff import setupHcalSimHits, setupCalibratedHGCalSimHits, setupL1THGCalSimHits, setupSimHitTables # pyright: ignore[reportMissingImports]
from CaloML.CaloHits.RecHits_cff import setupRecHitTables # pyright: ignore[reportMissingImports]

process = setupCalibratedHGCalSimHits(process)
process = setupL1THGCalSimHits(process)

for truth in ['L1THGCAL', 'L1THGCALfull',
              'L1THGCALoverlap1', 'L1THGCALoverlap2', 'L1THGCALoverlap3', 'L1THGCALoverlap4',
              'L1THGCALdistance1', 'L1THGCALdistance2', 'L1THGCALdistance3', 'L1THGCALdistance4']:
    process = setupSimTruth(process, truth, verbose=0)
    process = setupSimTruthTables(process, truth)
    process = setupSimHitTables(process, truth)
    process = setupRecHitTables(process, 'L1THGCAL', truth)

for truth in ['HGCAL']:
      #        'HGCALoverlap1', 'HGCALoverlap2', 'HGCALoverlap3', 'HGCALoverlap4',
      #        'HGCALdistance1', 'HGCALdistance2', 'HGCALdistance3', 'HGCALdistance4']:
    process = setupSimTruth(process, truth, verbose=0)
    process = setupSimTruthTables(process, truth)
    process = setupSimHitTables(process, truth)
    process = setupRecHitTables(process, "HGCAL", truth)

# Automatic addition of the customisation function from CaloML.Processing.HGCalTPG_cff
from CaloML.Processing.HGCalTPG_cff import setupHGCalTPG 

#call to customisation function setupHGCalTPG imported from CaloML.Processing.HGCalTPG_cff
process = setupHGCalTPG(process)

# Automatic addition of the customisation function from CaloML.SimTruth.GenParticles_cff
from CaloML.SimTruth.GenParticles_cff import setupGenParticlesTables 

#call to customisation function setupGenParticlesTables imported from CaloML.SimTruth.GenParticles_cff
process = setupGenParticlesTables(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# End of customisation functions


# Customisation from command line

process.schedule.remove(process.nanoAOD_step) 
process.source.delayReadingEventProducts = cms.untracked.bool(False)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
