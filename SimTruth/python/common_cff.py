import FWCore.ParameterSet.Config as cms 

rechits = {
    'HGCAL' : {
        'hits' : cms.VInputTag(
            'HGCalRecHit:HGCEERecHits',
            'HGCalRecHit:HGCHEFRecHits',
            'HGCalRecHit:HGCHEBRecHits'
        ),
        'pos_producer' : 'HGCalRecHitPositionTableProducer',
        'props_producer' : 'HGCalRecHitPropertiesTableProducer',
        'hittruth_producer' : 'HGCalRecHitTruthBuilder'
    },
    'L1THGCAL' : {
        'hits' : cms.VInputTag(
            'FloatingpointThreshold0:HGCalConcentratorProcessorSelection'
        ),
        'pos_producer' : 'L1THGCalRecHitPositionTableProducer',
        'props_producer' : 'HGCalTriggerCellPropertiesTableProducer',
        'hittruth_producer' : 'HGCalTriggerCellTruthBuilder'
    },
    'HBHE' : {
        'hits' : cms.VInputTag(
            'hbhereco',
        ),
        'pos_producer' : 'HBHERecHitPositionTableProducer' ,
        'props_producer' : 'HBHERecHitPropertiesTableProducer',
        'hittruth_producer' : 'HBHERecHitTruthBuilder'
    },
    'HF' : {
        'hits' : cms.VInputTag(
            'hfreco',
        ),
        'pos_producer' : 'HFRecHitPositionTableProducer',
        'props_producer' : 'HFRecHitPropertiesTableProducer',
        'hittruth_producer' : 'HFRecHitTruthBuilder'
    },
    'HO' : {
        'hits' : cms.VInputTag(
            'horeco',
        ),
        'pos_producer' : 'HORecHitPositionTableProducer' ,
        'props_producer' : 'HORecHitPropertiesTableProducer',
        'hittruth_producer' : 'HORecHitTruthBuilder'
    },
    'ECALBARREL' : {
        'hits' : cms.VInputTag(
            'ecalRecHit:EcalRecHitsEB',
        ),
        'pos_producer' : 'EcalRecHitPositionTableProducer',
        'props_producer' : 'EcalRecHitPropertiesTableProducer',
        'hittruth_producer' : 'EcalRecHitTruthBuilder'
    },
    'ECAL' : {
        'hits' : cms.VInputTag(
            'ecalRecHit:EcalRecHitsEB',
            'ecalRecHit:EcalRecHitsEE',
            'ecalPreshowerRecHit:EcalRecHitsES'
        ),
        'pos_producer' : 'EcalRecHitPositionTableProducer',
        'props_producer' : 'EcalRecHitPropertiesTableProducer',
        'hittruth_producer' : 'EcalRecHitTruthBuilder'
    }
}

raw_hgcal_simhits = cms.VInputTag(
    'g4SimHits:HGCHitsEE',
    'g4SimHits:HGCHitsHEfront',
    'g4SimHits:HGCHitsHEback'
)

merging_params = {
    #geometry from https://cms-docdb.cern.ch/cgi-bin/PublicDocDB/RetrieveFile?docid=13251&filename=20210803%20HGCAL%20PARAMETER%20DRAWING.pdf&version=11
    'HGCAL' : cms.PSet(
        caloR = cms.double(136.5),
        caloZ = cms.double(318.5),
        overlapThreshold = cms.double(-1),
        distanceTol = cms.double(-1),
        simhits = cms.VInputTag(
            'CalibratedHGCalSimHits'
        )
    ),

    #ibid
    'L1THGCAL' : cms.PSet(
        caloR = cms.double(136.5),
        caloZ = cms.double(318.5),
        overlapThreshold = cms.double(-1),
        distanceTol = cms.double(-1),
        simhits = cms.VInputTag(
            'TCSimHits'
        )
    ),

    #geometry from https://cms-docdb.cern.ch/cgi-bin/DocDB/RetrieveFile?docid=3661&filename=quarterView-HBHE.pdf&version=1
    'HCAL' : cms.PSet(
        caloR = cms.double(180.6),
        caloZ = cms.double(388.8),
        overlapThreshold = cms.double(.8),
        distanceTol = cms.double(0.5),
        simhits = cms.VInputTag(
            'CalibratedHcalSimHits'
        )
    ),

    #geometry is a guess. would love to find a real diagram
    'ECAL' : cms.PSet(
        caloR = cms.double(135.0),
        caloZ = cms.double(310.0),
        overlapThreshold = cms.double(-1),
        distanceTol = cms.double(-1),
        simhits = cms.VInputTag(
            'g4SimHits:EcalHitsEB',
            'g4SimHits:EcalHitsEE',
            'g4SimHits:EcalHitsES'
        )
    ),

    'ECALBARREL' : cms.PSet(
        caloR = cms.double(135.0),
        caloZ = cms.double(310.0),
        overlapThreshold = cms.double(-1),
        distanceTol = cms.double(-1),
        simhits = cms.VInputTag(
            'g4SimHits:EcalHitsEB'
        )
    )   
}

merging_params['ECALBARRELHCAL'] = cms.PSet(
    caloR = merging_params['ECALBARREL'].caloR,
    caloZ = merging_params['ECALBARREL'].caloZ,

    overlapThreshold = cms.double(0.0),
    distanceTol = cms.double(0.0),

    simhits = cms.VInputTag(
        merging_params['ECALBARREL'].simhits +
        merging_params['HCAL'].simhits
    )
)

merging_params['ECALHCAL'] = cms.PSet(
    caloR = merging_params['ECAL'].caloR,
    caloZ = merging_params['ECAL'].caloZ,

    overlapThreshold = cms.double(-1), 
    distanceTol = cms.double(-1),

    simhits = cms.VInputTag(
        merging_params['ECAL'].simhits +
        merging_params['HCAL'].simhits
    )
)

merging_params['L1THGCALoverlap1'] = merging_params['L1THGCAL'].clone(
    overlapThreshold = cms.double(0.2),
)
merging_params['L1THGCALoverlap2'] = merging_params['L1THGCAL'].clone(
    overlapThreshold = cms.double(0.4),
)
merging_params['L1THGCALoverlap3'] = merging_params['L1THGCAL'].clone(
    overlapThreshold = cms.double(0.6),
)
merging_params['L1THGCALoverlap4'] = merging_params['L1THGCAL'].clone(
    overlapThreshold = cms.double(0.8),
)


merging_params['L1THGCALdistance1'] = merging_params['L1THGCAL'].clone(
    distanceTol = cms.double(0.1)
)
merging_params['L1THGCALdistance2'] = merging_params['L1THGCAL'].clone(
    distanceTol = cms.double(0.2)
)
merging_params['L1THGCALdistance3'] = merging_params['L1THGCAL'].clone(
    distanceTol = cms.double(0.3)
)
merging_params['L1THGCALdistance4'] = merging_params['L1THGCAL'].clone(
    distanceTol = cms.double(0.4)
)

merging_params['L1THGCALfull'] = merging_params['L1THGCAL'].clone(
    distanceTol = cms.double(0.5),
    overlapThreshold = cms.double(0.8)
)


merging_params['HGCALoverlap1'] = merging_params['HGCAL'].clone(
    overlapThreshold = cms.double(0.2),
)
merging_params['HGCALoverlap2'] = merging_params['HGCAL'].clone(
    overlapThreshold = cms.double(0.4),
)
merging_params['HGCALoverlap3'] = merging_params['HGCAL'].clone(
    overlapThreshold = cms.double(0.6),
)
merging_params['HGCALoverlap4'] = merging_params['HGCAL'].clone(
    overlapThreshold = cms.double(0.8),
)


merging_params['HGCALdistance1'] = merging_params['HGCAL'].clone(
    distanceTol = cms.double(0.1)
)
merging_params['HGCALdistance2'] = merging_params['HGCAL'].clone(
    distanceTol = cms.double(0.5)
)
merging_params['HGCALdistance3'] = merging_params['HGCAL'].clone(
    distanceTol = cms.double(1.0)
)
merging_params['HGCALdistance4'] = merging_params['HGCAL'].clone(
    distanceTol = cms.double(2.0)
)
