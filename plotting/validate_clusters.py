from .common import *

def basic_cluster_histograms(clusters_l, labels_l, firstN=-1):
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))

    energies_l = []
    times_l = []
    nhits_l = []

    for clusters, label in zip(clusters_l, labels_l):
        energies = ak.flatten(clusters.impact_energy[:firstN])
        times = ak.flatten(clusters.calo_t0[:firstN])
        nhits = ak.flatten(clusters.nSimHits[:firstN])

        energies_l.append(energies)
        times_l.append(times)
        nhits_l.append(nhits)

    axes[0].hist(energies_l, bins=100,
                histtype='step', label=labels_l,
                density=True)
    axes[1].hist(times_l, bins=100,
                histtype='step', label=labels_l,
                density=True)
    maxnhits = ak.max(nhits_l, axis=None)
    axes[2].hist(nhits_l, bins=np.arange(0, maxnhits + 2) - 0.5,
                histtype='step', label=labels_l,
                density=True)

    axes[0].set_xlabel('Cluster Energy [GeV]')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Cluster Energy Distribution')
    axes[0].set_yscale('log')
    axes[0].legend()

    axes[1].set_xlabel('Cluster Time [cm]')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Cluster Time Distribution')
    axes[1].set_yscale('log')
    axes[1].legend()

    axes[2].set_xlabel('Number of Sim Hits in Cluster')
    axes[2].set_ylabel('Counts')
    axes[2].set_title('Number of Sim Hits Distribution')
    axes[2].set_yscale('log')
    axes[2].legend()

    plt.tight_layout()
    plt.savefig('plots/clusters_basic_histograms.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

def id_cluster_histograms(clusters_l, labels_l, firstN=-1):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    pdgid_table_l = []
    nclusters_l = []

    for clusters, label in zip(clusters_l, labels_l):
        pdgid = ak.flatten(clusters.track_pdgId[:firstN])
        nclusters = ak.num(clusters[:firstN])

        pdgid_table = {}

        pdgid_numbers, pdgid_counts = np.unique(pdgid, return_counts=True)
        for pdg, count in zip(pdgid_numbers, pdgid_counts):
            pdgid_table[pdg] = count

        pdgid_table_l.append(pdgid_table)
        nclusters_l.append(nclusters)

    pdgid_numbers = sorted(set().union(*[table.keys() for table in pdgid_table_l]))
    pdgid_positions = np.arange(len(pdgid_numbers))
    pdgid_counts = []
    for table in pdgid_table_l:
        counts = []
        for pdg in pdgid_numbers:
            if pdg in table:
                counts.append(table[pdg])
            else:
                counts.append(0)
        pdgid_counts.append(counts)
    pdgid_positions = [pdgid_positions] * len(pdgid_counts)
    pdgid_numbers = [pdgid_numbers] * len(pdgid_counts)

    axes[0].hist(pdgid_positions, bins=np.arange(len(pdgid_numbers[0]) + 1),
                 weights=pdgid_counts,
                 histtype='barstacked', label=labels_l,
                 density=True)    
    
    maxNclus = ak.max(nclusters_l, axis=None)
    axes[1].hist(nclusters_l, bins=np.arange(0, maxNclus + 2) - 0.5,
                histtype='barstacked', label=labels_l,
                density=True)

    pdgid_labels = []
    for pdgid in pdgid_numbers[0]:
        if pdgid in pdgid_lookup:
            pdgid_labels.append(pdgid_lookup[pdgid])
        else:
            pdgid_labels.append(str(pdgid))

    axes[0].set_xticks(pdgid_positions[0]+0.5)
    axes[0].set_xticklabels(pdgid_labels, rotation='vertical')
    axes[0].set_xlabel('Merged cluster PDG ID')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Merged cluster PDG ID Distribution')
    axes[0].set_yscale('log')
    axes[0].legend()
    
    axes[1].set_xlabel('Number of merged clusters')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Number of Merged Clusters per Event')
    axes[1].set_yscale('log')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('plots/cluster_id_histograms.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

def components_cluster_histograms(clusters_l, labels_l, firstN=-1):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    nParticles_l = []
    frac0_l = []

    for clusters, label in zip(clusters_l, labels_l):
        nParticles = ak.flatten(clusters.nParticles[:firstN])
        E = clusters.impact_energy
        frac0 = ak.flatten(clusters.energy0[:firstN] / E[:firstN])

        nParticles_l.append(nParticles)
        frac0_l.append(frac0)

    maxnpart = ak.max(nParticles_l, axis=None)
    axes[0].hist(nParticles_l, bins=np.arange(0, maxnpart + 2) - 0.5,
                 histtype='step', label=labels_l,
                 density=True)
    axes[1].hist(frac0_l, bins=100,
                histtype='step', label=labels_l,
                density=True)

    axes[0].set_xlabel('Number of constituent Geant tracks')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Geant tracks per merged cluster')
    axes[0].set_yscale('log')
    axes[0].legend()

    axes[1].set_xlabel('Fraction of energy in the leading component')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Fraction of Energy in Leading Component')
    axes[1].set_yscale('log')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('plots/clusters_components_histograms.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

