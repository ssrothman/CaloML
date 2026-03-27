import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]

from CaloML.SimTruth.common_cff import rechits

def setupHGCWaferInfoTables(process, subdet, truth):
    TCs = rechits[subdet]['hits'][0]
    TCtruth = 'RecHit' + subdet + 'Truth' + truth + 'Producer'
    tctablename = 'RecHits' + subdet + 'Truth' + truth

    setattr(process, '%sWaferInfosTruth%sProducer' % (subdet, truth), cms.EDProducer("HGCWaferInfoProducer",
        TCs = cms.InputTag(TCs),
        verbose = cms.int32(0)
    ))
    
    setattr(process, '%sWaferInfosTruth%sTable' % (subdet, truth), cms.EDProducer("HGCWaferInfoTableProducer",
        TCs = cms.InputTag(TCs),
        TCtruth = cms.InputTag(TCtruth),
        waferInfo = cms.InputTag("%sWaferInfosTruth%sProducer" % (subdet, truth)),
        verbose = cms.int32(0),

        bitsPerADC = cms.uint32(22),
        bitsPerNorm = cms.uint32(12),
        bitsPerCALQ = cms.uint32(23),
        bitsPerInput = cms.uint32(8),

        bitShiftNormalize = cms.bool(True),
        useTransverseADC = cms.bool(True),
        useModuleFactor=cms.bool(False),
        normByMax=cms.bool(False),

        name = cms.string("%sWafers%s" % (subdet, truth)),
        tctablename = cms.string(tctablename)
    ))

    setattr(process, '%sWaferInfoTruth%sTask' % (subdet, truth), cms.Task(
        getattr(process, '%sWaferInfosTruth%sProducer' % (subdet, truth)),
        getattr(process, '%sWaferInfosTruth%sTable' % (subdet, truth))
    ))
    process.schedule.associate(getattr(process, '%sWaferInfoTruth%sTask' % (subdet, truth)))

    return process