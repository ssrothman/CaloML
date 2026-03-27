import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]

def setupHGCWaferInfoTables(process, TCs, TCtruth, tctablename):
    process.HGCWaferInfos = cms.EDProducer("HGCWaferInfoProducer",
        TCs = cms.InputTag(TCs),
        verbose = cms.int32(0)
    )
    process.HGCWaferInfoTable = cms.EDProducer("HGCWaferInfoTableProducer",
        TCs = cms.InputTag(TCs),
        TCtruth = cms.InputTag(TCtruth),
        waferInfo = cms.InputTag("HGCWaferInfos"),
        verbose = cms.int32(0),

        bitsPerADC = cms.uint32(22),
        bitsPerNorm = cms.uint32(12),
        bitsPerCALQ = cms.uint32(23),
        bitsPerInput = cms.uint32(8),

        bitShiftNormalize = cms.bool(True),
        useTransverseADC = cms.bool(True),
        useModuleFactor=cms.bool(False),
        normByMax=cms.bool(False),

        name = cms.string("HGCWafers"),
        tctablename = cms.string(tctablename)
    )

    process.HGCWaferInfoTask = cms.Task(process.HGCWaferInfos, process.HGCWaferInfoTable)
    process.schedule.associate(process.HGCWaferInfoTask)

    return process