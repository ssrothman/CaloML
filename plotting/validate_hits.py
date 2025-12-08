from .common import *

def xyz_to_etaphi(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z / r)
    eta = -np.log(np.tan(theta / 2))
    phi = np.arctan2(y, x)
    return eta, phi

def truth_hit_histograms(hits_l, labels_l, firstN=-1):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    nclusters_l = []
    frac0_l = []

    for hits, label in zip(hits_l, labels_l):
        nclusters = ak.flatten(hits.nClusters[:firstN])
        frac0 = ak.flatten(hits.frac0[:firstN])

        nclusters_l.append(nclusters)
        frac0_l.append(frac0)

    maxnclust = ak.max(nclusters_l, axis=None)
    axes[0].hist(nclusters_l, bins=np.arange(0, maxnclust + 2) - 0.5,
                 histtype='step', label=labels_l,
                 density=True)
    axes[1].hist(frac0_l, bins=100,
                histtype='step', label=labels_l,
                density=True)

    axes[0].set_xlabel('Number of matched truth clusters')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Number of Matched Truth Clusters')
    axes[0].set_yscale('log')
    axes[0].legend()

    axes[1].set_xlabel('Fraction of energy in the leading cluster')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Fraction of Energy in Leading Cluster')
    axes[1].set_yscale('log')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('plots/hits_truth_histograms.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

def basic_hit_histograms(hits_l, labels_l, firstN=-1):
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))

    energies_l = []
    simenergies_l = []
    times_l = []

    for hits, label in zip(hits_l, labels_l):
        energies = ak.flatten(hits.energy[:firstN])
        simenergies = ak.flatten(hits.simenergy[:firstN])
        times = ak.flatten(hits.time[:firstN])

        energies_l.append(energies)
        simenergies_l.append(simenergies)
        times_l.append(times)

    axes[0].hist(energies_l, bins=100,
                 histtype='step', label=labels_l,
                 density=True)
    axes[1].hist(simenergies_l, bins=100,
                 histtype='step', label=labels_l,
                 density=True)
    axes[2].hist(times_l, bins=100,
                histtype='step', label=labels_l,
                density=True)

    axes[0].set_xlabel('Hit Energy [GeV]')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Hit Energy Distribution')
    axes[0].set_yscale('log')
    axes[0].legend()

    axes[1].set_xlabel('Hit Simulated Energy [GeV]')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Hit Simulated Energy Distribution')
    axes[1].set_yscale('log')
    axes[1].legend()

    axes[2].set_xlabel('Hit Time [ns]')
    axes[2].set_ylabel('Counts')
    axes[2].set_title('Hit Time Distribution')
    axes[2].set_yscale('log')
    axes[2].legend()

    plt.tight_layout()
    plt.savefig('plots/hits_basic_histograms.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()

def plot_hit_coordinates(hits_l, labels_l, firstN=10):
    fig = plt.figure(figsize=(18, 6))
    ax_xy = fig.add_subplot(131)
    ax_xz = fig.add_subplot(132)
    ax_yz = fig.add_subplot(133)    

    for hits, label in zip(hits_l, labels_l):
        x = ak.flatten(hits.x[:firstN])
        y = ak.flatten(hits.y[:firstN])
        z = ak.flatten(hits.z[:firstN])

        ax_xy.scatter(x, y, s=1, label=label)
        ax_xz.scatter(x, z, s=1, label=label)
        ax_yz.scatter(y, z, s=1, label=label)

    ax_xy.set_xlabel('X [cm]')
    ax_xy.set_ylabel('Y [cm]')
    ax_xy.set_title('Hit Coordinates: XY Plane')
    ax_xy.axis('equal')
    ax_xy.legend(loc='upper right',
                 fontsize='large',
                 markerscale=4)

    ax_xz.set_xlabel('X [cm]')
    ax_xz.set_ylabel('Z [cm]')
    ax_xz.set_title('Hit Coordinates: XZ Plane')
    ax_xz.axis('equal')
    ax_xz.legend(loc='upper right',
                 fontsize='large',
                 markerscale=4)

    ax_yz.set_xlabel('Y [cm]')
    ax_yz.set_ylabel('Z [cm]')
    ax_yz.set_title('Hit Coordinates: YZ Plane')
    ax_yz.axis('equal') 
    ax_yz.legend(loc='upper right',
                 fontsize='large',
                 markerscale=4)
    
    plt.tight_layout()
    plt.savefig('plots/hits_coordinates.png', 
                format='png',
                dpi=300,
                bbox_inches='tight')
    plt.close()