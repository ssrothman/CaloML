import FWCore.ParameterSet.Config as cms

from CaloML.PFClusters.SimplePFClusterFlatTableProducer_cfi import SimplePFClusterFlatTableProducer
from CaloML.PFClusters.PFClusterHitsTableProducer_cfi import PFClusterHitsTableProducer


def setupClusterTables(process, src, clusterTableName, clusterHitsTableName, doc=''):
    """
    Setup PFCluster and PFRecHit flat table producers.
    
    Args:
        process: CMS process object
        src: Input collection (e.g., 'particleFlowClusterHCAL')
        clusterTableName: Name for cluster-level table module (e.g., 'HcalClusterTable')
        clusterHitsTableName: Name for cluster hits table module (e.g., 'HcalClusterHitsTable')
        doc: Optional documentation string prefix
    
    Returns:
        cms.Task containing both producers
    """
    
    # Get base names from module names
    clusterBaseName = clusterTableName.replace('Table', '')
    clusterHitsBaseName = clusterHitsTableName.replace('Table', '')
    
    # Create cluster table
    setattr(process, clusterTableName, SimplePFClusterFlatTableProducer.clone(
        src = cms.InputTag(src),
        name = cms.string(clusterBaseName),
        doc = cms.string(doc if doc else f'Table of PFClusters in {clusterBaseName.replace("PFCluster", "")}'),
    ))
    
    # Create cluster hits table
    setattr(process, clusterHitsTableName, PFClusterHitsTableProducer.clone(
        src = cms.InputTag(src),
        name = cms.string(clusterHitsBaseName),
        doc = cms.string(doc if doc else f'Table of PFRecHits associated with reco::PFCluster objects'),
    ))
    
    # Create and associate task
    taskName = clusterTableName.replace('Table', 'TablesTask')
    task = cms.Task(getattr(process, clusterTableName), getattr(process, clusterHitsTableName))
    setattr(process, taskName, task)
    process.schedule.associate(task)
    
    return task
