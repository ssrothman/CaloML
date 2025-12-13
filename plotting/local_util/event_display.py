import simon_mpl_util as smu
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name, common_names
import numpy as np

def plot_an_event(filepath, ievt, 
                  subdets, truth, 
                  hits_cut=smu.NoCut(), 
                  clusters_cut=smu.GreaterThanCut('impact_eta', 0), 
                  genpart_cut = smu.GreaterThanCut('eta', 0),
                  show_noise=True, 
                  savefig=None):
    """Plot an event from a given file.

    Args:
        filepath (str): Path to the file containing the event data.
        ievt (int): Index of the event to plot.
        subdets (list): List of subdetectors to include in the plot.
        hits_cut (int): Minimum number of hits to consider for plotting.
        clusters_cut (int): Minimum number of clusters to consider for plotting.
        savefig (str, optional): Path to save the figure. If None, the figure is shown instead.
    """

    dataset = smu.NanoEventsDataset(filepath, entry_start=ievt, entry_stop=ievt + 1)

    rechit_collections = []
    rechit_cuts = []

    for subdet in subdets:
        rechit_collection, rechit_cut = get_subdet_collection_cut(subdet, truth=truth)
        rechit_cuts.append(rechit_cut)
        rechit_collections.append(rechit_collection)

    X = smu.BasicVariable('x')
    Y = smu.BasicVariable('y')
    Z = smu.BasicVariable('z')

    varX = smu.ConcatVariable.build_for_collections(X, rechit_collections)
    varY = smu.ConcatVariable.build_for_collections(Y, rechit_collections)
    varZ = smu.ConcatVariable.build_for_collections(Z, rechit_collections)

    clusterselections = []
    clusterlabels = []

    if show_noise:
        noise = smu.EqualsCut('cluster0', -1)
        clusterselections.append(noise)
        clusterlabels.append('Noise')
    
    # Get cluster selection
    cluster_collection = get_simcluster_collection_name(truth=truth)
    clusters_cut.set_collection_name(cluster_collection)
    clustermask = clusters_cut.evaluate(dataset)[0] # only one event

    nClus = len(clustermask)

    # get cluster properties
    clus_pdgid = smu.BasicVariable('track_pdgId', collection_name=cluster_collection).evaluate(dataset)[0]
    clus_pt = smu.BasicVariable('track_pt', collection_name=cluster_collection).evaluate(dataset)[0]

    for i in range(nClus):
        if not clustermask[i]:
            continue

        clusterselections.append(smu.EqualsCut('cluster0', i))
        pid = str(clus_pdgid[i])
        pid_name = common_names['pdgid_label_lookup'].get(pid, pid)
        clusterlabels.append(f'{pid_name}, pT={clus_pt[i]:.1f} GeV')

    cuts = []
    for clustersel in clusterselections:
        cuts.append(
            smu.ConcatCut.build_for_collections(smu.AndCuts(hits_cut, clustersel), rechit_collections, unique_cuts_l=rechit_cuts)
        )

    #get gen particles
    genpart_collection = 'GenPart'
    genpart_cut.set_collection_name(genpart_collection)
    genpart_mask = genpart_cut.evaluate(dataset)[0] #only one event
    nGenPart = len(genpart_mask)

    genpart_pt = smu.BasicVariable('pt', collection_name=genpart_collection).evaluate(dataset)[0]
    genpart_eta = smu.BasicVariable('eta', collection_name=genpart_collection).evaluate(dataset)[0]
    genpart_phi = smu.BasicVariable('phi', collection_name=genpart_collection).evaluate(dataset)[0]
    genpart_pdgid = smu.BasicVariable('pdgId', collection_name=genpart_collection).evaluate(dataset)[0]

    genpart_lines_xy = []

    for i in range(nGenPart):
        if not genpart_mask[i]:
            continue

        pt = genpart_pt[i]
        eta = genpart_eta[i]
        phi = genpart_phi[i]
        theta = smu.eta_to_theta(eta)

        start_r = 0
        end_r = 300

        x_start = start_r * np.sin(theta) * np.cos(phi)
        y_start = start_r * np.sin(theta) * np.sin(phi)
        z_start = start_r * np.cos(theta)

        x_end = end_r * np.sin(theta) * np.cos(phi)
        y_end = end_r * np.sin(theta) * np.sin(phi)
        z_end = end_r * np.cos(theta)

        #genpart_xs.append([x_start, x_end])
        #genpart_ys.append([y_start, y_end])
        #genpart_zs.append([z_start, z_end])

        pid = str(genpart_pdgid[i])
        pid_name = common_names['pdgid_label_lookup'].get(pid, 'unknown')

        genpart_lines_xy.append(
            smu.LineSpec([x_start, x_end], [y_start, y_end], 
                         c='k', linestyle='--',
                         label=f'Gen: {pid_name}, pt={pt:.1f} GeV')
        )

    IP = smu.PointSpec([0], [0], c='grey', marker='*', s=100, label='IP')

    smu.scatter_2d(
        varX, varY, 
        cuts, dataset,
        labels_=clusterlabels,
        ensure_square_aspect=True,
        notext = True,
        ps = 10.0,
        output_path=savefig,
        legend_loc=(1.05, 0.9, 'upper left'),
        add_stuff=genpart_lines_xy + [IP]
    )
