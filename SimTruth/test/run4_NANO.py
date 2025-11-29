# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step1 --filein file:test.root --fileout testNanoML.root --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions auto:mc --step NANO
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9

process = cms.Process('NANO', Phase2C17I13M9)
options = VarParsing('python')
options.setDefault('outputFile', 'testNanoML.root')
options.register("nThreads", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "number of threads")
options.register("runPFTruth", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "Don't run PFTruth (currently not working with pileup)")
options.register("nEvents", -1, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "number of events to process")
#options.register("runPFTruth", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int,
#    "generate PFTruth")
options.parseArguments()

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtendedRun4D110Reco_cff')
process.load('Configuration.Geometry.GeometryExtendedRun4D110_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('DPGAnalysis.HGCalNanoAOD.nanoHGCML_cff')
process.load('L1Trigger.L1THGCal.l1tHGCalTriggerGeometryESProducer_cfi')
#added
# Fix for ProductNotFound error with FlatEtaRangeGunProducer
process.tpClusterProducer.pixelSimLinkSrc = cms.InputTag("simSiPixelDigis", "Pixel")
process.tpClusterProducer.phase2OTSimLinkSrc = cms.InputTag("simSiPixelDigis", "Tracker")
#added
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')


# load HGCAL TPG simulation
process.load('L1Trigger.L1THGCal.hgcalTriggerPrimitives_cff')
process.load('L1Trigger.L1THGCalUtilities.HGC3DClusterSelectors_cff')
process.load('L1Trigger.L1THGCalUtilities.hgcalTriggerNtuples_cff')
from L1Trigger.L1THGCalUtilities.hgcalTriggerChains import HGCalTriggerChains
import L1Trigger.L1THGCalUtilities.vfe as vfe
import L1Trigger.L1THGCalUtilities.concentrator as concentrator
import L1Trigger.L1THGCalUtilities.clustering2d as clustering2d
import L1Trigger.L1THGCalUtilities.clustering3d as clustering3d
import L1Trigger.L1THGCalUtilities.selectors as selectors
import L1Trigger.L1THGCalUtilities.customNtuples as ntuple

chains = HGCalTriggerChains()
chains.register_vfe("Floatingpoint", vfe.CreateVfe())
chains.register_concentrator("Threshold0", concentrator.CreateThreshold(
  threshold_scintillator=cms.double(-1),
  threshold_silicon=cms.double(-1)
))
## BE1
chains.register_backend1("Dummy", clustering2d.CreateDummy())
## BE2
chains.register_backend2("Histomax", clustering3d.CreateHistoMax())
chains.register_chain('Floatingpoint', 'Threshold0', 'Dummy', 'Histomax')
process = chains.create_sequences(process)
process.hgcl1tpg_step = cms.Path(process.L1THGCalTriggerPrimitives)

# This isn't working with pileup
if not options.runPFTruth:
    process.pfTruth = cms.Sequence()
    process.trackSCAssocTable = cms.Sequence()

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.nEvents),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)
process.options.numberOfThreads=cms.untracked.uint32(options.nThreads)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
#    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
#    SkipEvent = cms.untracked.vstring(),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(1)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    makeTriggerResults = cms.obsolete.untracked.bool,
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(1),
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
    annotation = cms.untracked.string('step1 nevts:1'),
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
    fileName = cms.untracked.string(options.outputFile),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

process.NANOAODSIMoutput.outputCommands.remove("keep edmTriggerResults_*_*_*")

from CaloML.SimTruth.SimTruth_cff import setupSimTruthTables, setupSimTruth
from CaloML.CaloHits.SimHits_cff import setupSimHitTables

process.fullTruthSeq = cms.Sequence()
process.customNanoHGCMLSequence = cms.Sequence(
    process.nanoMetadata +
    process.genVertexTable +
    process.genVertexT0Table +
    process.genParticleTable
)
# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:mc', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(
    #process.nanoHGCMLSequence+
    process.customNanoHGCMLSequence+
    process.fullTruthSeq
)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(
        process.hgcl1tpg_step,
        process.nanoAOD_step,
        process.endjob_step,
        process.NANOAODSIMoutput_step
)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.
from DPGAnalysis.HGCalNanoAOD.nanoHGCML_cff import customizeReco,customizeMergedSimClusters
# Uncomment if you didn't schedule SimClusters/CaloParticles
# process = customizeNoMergedCaloTruth(process)
# merged simclusters (turn off if you aren't running through PEPR)
process = customizeMergedSimClusters(process)
process = customizeReco(process)

from CaloML.CaloHits.SimHits_cff import setupL1THGCalSimHits, setupHcalSimHits, setupCalibratedHGCalSimHits
from CaloML.CaloHits.RecHits_cff import setupRecHitTables

process = setupCalibratedHGCalSimHits(process)
process = setupL1THGCalSimHits(process)

for subdet in ['HGCAL', 'L1THGCAL']:
    process = setupSimTruth(process, subdet, verbose=0)
    process = setupSimTruthTables(process, subdet)
    process = setupSimHitTables(process, subdet)
    process = setupRecHitTables(process, subdet, truth=subdet)

# End of customisation functions


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
