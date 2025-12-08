from .common import *

def simcluster_energy_calibration_histogram(clusters_l, labels_l):
   
    ratios = []

    for clusters in clusters_l:
        genE = ak.flatten(clusters.impact_energy)
        simE = ak.flatten(clusters.simEnergy)

        ratios.append(simE / genE)

    fig = plt.figure(figsize=(6, 5))
    plt.hist(ratios, label = labels_l,
             bins=100,
             histtype='step',
             density=True)
    
    plt.xlabel('SimCluster Energy / Geant Track Energy')
    plt.ylabel('Counts')
    plt.title('SimCluster Energy Calibration')
    plt.yscale('log')
    if len(labels_l) > 1:
        plt.legend()
    plt.axvline(1.0, color='red', linestyle='dashed')

    plt.tight_layout()
    plt.savefig('plots/simcluster_energy_calibration.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

def hit_energy_calibration_histogram(hits_l, labels_l, force_range=None):
   
    ratios = []

    for hits in hits_l:
        simE = ak.flatten(hits.simenergy)
        recE = ak.flatten(hits.energy)

        ratios.append((recE / simE)[simE != 0])

    fig = plt.figure(figsize=(6, 5))
    plt.hist(ratios, label = labels_l,
             bins=100,
             histtype='step',
             range=force_range,
             density=True)
    
    plt.xlabel('Hit E_reco / E_sim')
    plt.ylabel('Counts')
    plt.title('Hit Energy Calibration')
    plt.yscale('log')
    if len(labels_l) > 1:
        plt.legend()
    plt.axvline(1.0, color='red', linestyle='dashed')

    plt.tight_layout()
    plt.savefig('plots/hit_energy_calibration.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()