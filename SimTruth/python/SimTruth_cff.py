import FWCore.ParameterSet.Config as cms # pyright: ignore[reportMissingImports]

from CaloML.SimTruth.common_cff import merging_params # pyright: ignore[reportMissingImports]

def setupSimTruth(process, subdet, verbose=0):
    #lookup parameters
    if subdet in merging_params:
        params = merging_params[subdet]
    else:
        valid_options = "', '".join(merging_params.keys())
        raise ValueError(f"subdet must be one of '{valid_options}'")

    producers = []

    setattr(process, 'SimTreeTruthMerger%s'%subdet,
        cms.EDProducer("SimTreeTruthMerger",
            simtracks = cms.InputTag('g4SimHits'),
            simvertices = cms.InputTag('g4SimHits'),

            simhits = params.simhits,

            caloR = params.caloR,
            caloZ = params.caloZ,

            verbose = cms.int32(verbose)
        )
    )

    setattr(process, 'SimTreeMergedTrackInfo%s'%subdet,
        cms.EDProducer("SimTrackInfoBuilder",
            simtracks = cms.InputTag('SimTreeTruthMerger%s:mergedSimTracks'%subdet),
            simvertices = cms.InputTag('g4SimHits'),

            caloR = params.caloR,
            caloZ = params.caloZ,

            verbose = cms.int32(verbose)
        )
    )

    setattr(process, 'SimTreeMergedClusterInfo%s'%subdet,
        cms.EDProducer("SimClusterInfoBuilder",
            simclusters = cms.InputTag('SimTreeTruthMerger%s:mergedSimClusters'%subdet),     
            simhits = cms.VInputTag('SimTreeTruthMerger%s:relabeledSimHits'%subdet),
            simtracks = cms.InputTag('SimTreeTruthMerger%s:mergedSimTracks'%subdet),
            simtrackInfos = cms.InputTag('SimTreeMergedTrackInfo%s'%subdet),
            verbose = cms.int32(verbose)
        )
    )

    setattr(process, 'ImpactDistanceTruthMerger%s'%subdet,
        cms.EDProducer(
            'ImpactDistanceTruthMerger',
            #simvertices = cms.InputTag('g4SimHits'),
            simhits = cms.VInputTag('SimTreeTruthMerger%s:relabeledSimHits'%subdet),
            simclusters = cms.InputTag('SimTreeTruthMerger%s:mergedSimClusters'%subdet),
            simclusterInfos = cms.InputTag('SimTreeMergedClusterInfo%s'%subdet),

            caloR = params.caloR,
            caloZ = params.caloZ,

            distanceTol = params.distanceTol,
            dRTol = cms.double(0.0),
            dEtaTol = cms.double(0.0),
            dPhiTol = cms.double(0.0),

            verbose = cms.int32(verbose)
        )
    )

        
    setattr(process, 'HitOverlapTruthMerger%s'%subdet,
        cms.EDProducer(
            'HitOverlapTruthMerger',
            simhits = cms.VInputTag('SimTreeTruthMerger%s:relabeledSimHits'%subdet),
            simclusters = cms.InputTag('ImpactDistanceTruthMerger%s:mergedSimClusters'%subdet),
            simclusterInfos = cms.InputTag('ImpactDistanceTruthMerger%s:mergedSimClusterInfos'%subdet),

            overlapThreshold = params.overlapThreshold,

            verbose = cms.int32(verbose)
        )
    )

    producers += [getattr(process, 'SimTreeMergedTrackInfo%s'%subdet)]
    producers += [getattr(process, 'SimTreeMergedClusterInfo%s'%subdet)]
    producers += [getattr(process, 'SimTreeTruthMerger%s'%subdet)]
    producers += [getattr(process, 'ImpactDistanceTruthMerger%s'%subdet)]
    producers += [getattr(process, 'HitOverlapTruthMerger%s'%subdet)]

    setattr(process, 'SimTruth%sTask'%subdet,
        cms.Task(*producers)
    )
    process.schedule.associate(
        getattr(process, 'SimTruth%sTask'%subdet)
    )

    return process

from CaloML.SimTruth.SimClusterTable_cfi import SimClusterTable # pyright: ignore[reportMissingImports]

def setupSimTruthTables(process, subdet):
    setattr(process, 'MergedSimCluster%sTable'%subdet,
        SimClusterTable.clone(
            src = cms.InputTag('HitOverlapTruthMerger%s:mergedSimClusters'%subdet),
            name = 'MergedSimCluster%s'%subdet
        )
    )

    setattr(process, 'MergedSimClusterInfo%sTable'%subdet,
        cms.EDProducer("MergedSimClusterInfoTableProducer",
            name = cms.string('MergedSimCluster%s'%subdet),
            doc = cms.string(''),
            src = cms.InputTag('HitOverlapTruthMerger%s:mergedSimClusterInfos'%subdet),
            extension = cms.bool(True)
        )
    )

    setattr(process, 'SimTruth%sTablesTask'%subdet,
        cms.Task(
            getattr(process, 'MergedSimCluster%sTable'%subdet),
            getattr(process, 'MergedSimClusterInfo%sTable'%subdet)
        )
    )

    process.schedule.associate(
        getattr(process, 'SimTruth%sTablesTask'%subdet)
    )

    return process


