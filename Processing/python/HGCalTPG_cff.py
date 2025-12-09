import FWCore.ParameterSet.Config as cms

def setupHGCalTPG(process):
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
    process.hgcl1tpg_path = cms.Path(process.L1THGCalTriggerPrimitives)

    #add sequence to schedule
    process.schedule.insert(0, process.hgcl1tpg_path)

    return process