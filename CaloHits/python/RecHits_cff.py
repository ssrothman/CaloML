import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]

from CaloML.SimTruth.common_cff import rechits # pyright: ignore[reportMissingImports]

def setupRecHitTables(process, subdet, truth):
    if subdet in rechits:
        params = rechits[subdet]
    else:
        valid_options = "', '".join(rechits.keys())
        raise ValueError(f"subdet must be one of '{valid_options}'")

    setattr(process, 'RecHit%sTruth%sPositionTable'%(subdet, truth),
        cms.EDProducer(
            params['pos_producer'],
            src = params['hits'],
            name = cms.string('RecHits%sTruth%s'%(subdet, truth)),
            cut = cms.string(''),
            doc = cms.string('')
        )
    )
    setattr(process, 'RecHit%sTruth%sPropertiesTable'%(subdet, truth),
        cms.EDProducer(
            params['props_producer'],
            src = params['hits'],
            name = cms.string('RecHits%sTruth%s'%(subdet, truth)),
            cut = cms.string(''),
            doc = cms.string('')
        )
    )

    setattr(process, 'RecHit%sTruth%sProducer'%(subdet, truth),
        cms.EDProducer(
            params['hittruth_producer'],
            rechits = params['hits'],
            simclusters = cms.InputTag('HitOverlapTruthMerger%s:mergedSimClusters'%truth),
            verbose = cms.int32(0)
        )
    )

    setattr(process, 'RecHit%sTruth%sTruthTable'%(subdet, truth),
        cms.EDProducer(
            'HitTruthTableProducer',
            src = cms.InputTag('RecHit%sTruth%sProducer'%(subdet, truth)),
            name = cms.string('RecHits%sTruth%s'%(subdet, truth)),
            doc = cms.string('')
        )
    )

    setattr(process, 'RecHit%sTruth%sTablesTask'%(subdet, truth),
        cms.Task(
            getattr(process, 'RecHit%sTruth%sPositionTable'%(subdet, truth)),
            getattr(process, 'RecHit%sTruth%sPropertiesTable'%(subdet, truth)),
            getattr(process, 'RecHit%sTruth%sProducer'%(subdet, truth)),
            getattr(process, 'RecHit%sTruth%sTruthTable'%(subdet, truth))
        )
    )
    process.schedule.associate(getattr(process, 'RecHit%sTruth%sTablesTask'%(subdet, truth)))
    
    return process