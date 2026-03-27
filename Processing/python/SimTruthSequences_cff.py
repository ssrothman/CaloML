from CaloML.CaloHits.HGCWafers_cff import setupHGCWaferInfoTables
import FWCore.ParameterSet.Config as cms

from CaloML.SimTruth.common_cff import * # pyright: ignore[reportMissingImports]
from CaloML.SimTruth.SimTruth_cff import setupSimTruth, setupSimTruthTables # pyright: ignore[reportMissingImports]
from CaloML.CaloHits.SimHits_cff import setupHcalSimHits, setupCalibratedHGCalSimHits, setupL1THGCalSimHits, setupSimHitTables # pyright: ignore[reportMissingImports]
from CaloML.CaloHits.RecHits_cff import setupRecHitTables # pyright: ignore[reportMissingImports]
 
def SimTruthSequence_ECALHCAL(process):
    process = setupHcalSimHits(process)
    process = setupSimTruth(process, 'ECALHCAL', verbose=0)
    process = setupSimTruthTables(process, 'ECALHCAL')
    process = setupSimHitTables(process, 'ECALHCAL')
    process = setupRecHitTables(process, 'ECAL', 'ECALHCAL')
    process = setupRecHitTables(process, 'HBHE', 'ECALHCAL')
    process = setupRecHitTables(process, 'HO', 'ECALHCAL')
    return process

def SimTruthSequence_HGCAL(process):
    process = setupCalibratedHGCalSimHits(process)

    process = setupSimTruth(process, "HGCAL", verbose=0)
    process = setupSimTruthTables(process, "HGCAL")
    process = setupSimHitTables(process, "HGCAL")
    process = setupRecHitTables(process, "HGCAL", "HGCAL")

    return process

def SimTruthSequence_L1THGCAL(process):
    process = setupCalibratedHGCalSimHits(process)
    process = setupL1THGCalSimHits(process)

    process = setupSimTruth(process, "L1THGCAL", verbose=0)
    process = setupSimTruthTables(process, "L1THGCAL")
    process = setupSimHitTables(process, "L1THGCAL")
    process = setupRecHitTables(process, "L1THGCAL", "L1THGCAL")

    process = setupHGCWaferInfoTables(
        process, 
        'L1THGCAL',
        'L1THGCAL'
    )

    return process