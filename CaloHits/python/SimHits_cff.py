import FWCore.ParameterSet.Config as cms 

from CaloML.SimTruth.common_cff import merging_params, raw_hgcal_simhits 

def setupCalibratedHGCalSimHits(process):
    import SimCalorimetry.HGCalSimProducers.hgcalDigitizer_cfi as digiparam
    import RecoLocalCalo.HGCalRecProducers.HGCalUncalibRecHit_cfi as recoparam
    import RecoLocalCalo.HGCalRecProducers.HGCalRecHit_cfi as recocalibparam
    import L1Trigger.L1THGCal.hgcalLayersCalibrationCoefficients_cfi as layercalibparam


    process.CalibratedHGCalSimHits = cms.EDProducer("CalibratedHGCalSimHitProducer",
        src = raw_hgcal_simhits,
        keV2fC = digiparam.hgceeDigitizer.digiCfg.keV2fC,
        fcPerMip = recoparam.HGCalUncalibRecHit.HGCEEConfig.fCPerMIP,
        layerWeights = layercalibparam.triggerWeights.weights,
        thicknessCorrections = recocalibparam.HGCalRecHit.thicknessCorrection
    )
    process.CalibratedHGCalSimHitTask = cms.Task(
        process.CalibratedHGCalSimHits
    )
    process.schedule.associate(process.CalibratedHGCalSimHitTask)
    return process

def setupL1THGCalSimHits(process):
    process.TCSimHits = cms.EDProducer("TriggerCellSimHitsProducer",
        simHits = merging_params['HGCAL'].simhits
    )
    process.TCSimHitTask = cms.Task(
        process.TCSimHits
    )
    process.schedule.associate(process.TCSimHitTask)
    return process

def setupHcalSimHits(process):
    process.RelabelledHcalSimHits = cms.EDProducer(
        "RelabelledHcalSimHitsProducer",
        src = cms.InputTag('g4SimHits','HcalHits')
    )

    from SimCalorimetry.HcalSimProducers.hcalSimParameters_cfi import hcalSimParameters 

    process.CalibratedHcalSimHits = cms.EDProducer(
        'CalibratedHcalSimHitsProducer',
        src = cms.InputTag('RelabelledHcalSimHits'),
        HcalSimParameters = hcalSimParameters 
    )

    process.HcalSimHitTask = cms.Task(
        process.RelabelledHcalSimHits,
        process.CalibratedHcalSimHits
    )
    process.schedule.associate(process.HcalSimHitTask)
    return process

def setupSimHitTables(process, subdet):
    if subdet in merging_params:
        params = merging_params[subdet]
    else:
        valid_options = "', '".join(merging_params.keys())
        raise ValueError(f"subdet must be one of '{valid_options}'")

    if subdet == 'HGCAL':
        position_producer = 'HGCalSimHitPositionTableProducer'
        props_producer = 'HGCalSimHitPropertiesTableProducer'
    elif subdet == 'L1THGCAL':
        position_producer = 'L1THGCalSimHitPositionTableProducer'
        props_producer = 'HGCalSimHitPropertiesTableProducer' #HGCal properties producer is same for L1T and offline
    else:
        position_producer = 'CaloSimHitPositionTableProducer'
        props_producer = 'GenericSimHitPropertiesTableProducer'

    setattr(process, 'SimHit%sPositionTable'%subdet,
        cms.EDProducer(
            position_producer,
            src = cms.VInputTag(*params.simhits),
            name = cms.string('SimHits%s'%subdet),
            cut = cms.string(''),
            doc = cms.string('')
        )
    )

    setattr(process, 'SimHit%sPropertiesTable'%subdet,
        cms.EDProducer(
            props_producer,
            src = cms.VInputTag(*params.simhits),
            name = cms.string('SimHits%s'%subdet),
            cut = cms.string(''),
            doc = cms.string('')
        )
    )

    setattr(process, 'SimHit%sTablesTask'%subdet,
        cms.Task(
            getattr(process, 'SimHit%sPositionTable'%subdet),
            getattr(process, 'SimHit%sPropertiesTable'%subdet)
        )
    )

    process.schedule.associate(
            getattr(process, 'SimHit%sTablesTask'%subdet)
    )

    return process
