import simonplot as smp
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name, common_names
import numpy as np
from simonpy.coordinates import eta_to_theta

def plot_an_event(filepath, ievt, 
                  subdets, truth, 
                  hits_cut=smp.cut.NoCut(), 
                  clusters_cut=smp.cut.GreaterThanCut('impact_eta', 0), 
                  genpart_cut = smp.cut.GreaterThanCut('eta', 0),
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

    dataset = smp.plottables.NanoEventsDataset(
        fname = filepath, 
        entry_start=ievt, 
        entry_stop=ievt + 1,
        color = 'k',
        label = '',
        key = 'events'
    )

    rechit_collections = []
    rechit_cuts = []

    for subdet in subdets:
        rechit_collection, rechit_cut = get_subdet_collection_cut(subdet, truth=truth)
        rechit_cuts.append(rechit_cut)
        rechit_collections.append(rechit_collection)

    X = smp.variable.BasicVariable('x')
    Y = smp.variable.BasicVariable('y')
    Z = smp.variable.BasicVariable('z')

    varX = smp.variable.ConcatVariable.build_for_collections(X, rechit_collections)
    varY = smp.variable.ConcatVariable.build_for_collections(Y, rechit_collections)
    varZ = smp.variable.ConcatVariable.build_for_collections(Z, rechit_collections)

    clusterselections = []
    clusterlabels = []

    if show_noise:
        noise = smp.cut.EqualsCut('cluster0', -1)
        clusterselections.append(noise)
        clusterlabels.append('Noise')
    
    # Get cluster selection
    cluster_collection = get_simcluster_collection_name(truth=truth)
    clusters_cut.set_collection_name(cluster_collection)
    clustermask = clusters_cut.evaluate(dataset)[0] # only one event

    nClus = len(clustermask)

    # get cluster properties
    clus_pdgid = smp.variable.BasicVariable('track_pdgId', collection_name=cluster_collection).evaluate(dataset, smp.cut.NoCut())[0]
    clus_pt = smp.variable.BasicVariable('track_pt', collection_name=cluster_collection).evaluate(dataset, smp.cut.NoCut())[0]

    for i in range(nClus):
        if not clustermask[i]:
            continue

        clusterselections.append(smp.cut.EqualsCut('cluster0', i))
        pid = str(clus_pdgid[i])
        pid_name = common_names['pdgid_label_lookup'].get(pid, pid)
        clusterlabels.append(f'{pid_name}, pT={clus_pt[i]:.1f} GeV')

    cuts = []
    for clustersel in clusterselections:
        cuts.append(
            smp.cut.ConcatCut.build_for_collections(smp.cut.AndCuts([hits_cut, clustersel]), rechit_collections, unique_cuts_l=rechit_cuts)
        )

    #get gen particles
    genpart_collection = 'GenPart'
    genpart_cut.set_collection_name(genpart_collection)
    genpart_mask = genpart_cut.evaluate(dataset)[0] #only one event
    nGenPart = len(genpart_mask)

    genpart_pt = smp.variable.BasicVariable('pt', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
    genpart_eta = smp.variable.BasicVariable('eta', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
    genpart_phi = smp.variable.BasicVariable('phi', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
    genpart_pdgid = smp.variable.BasicVariable('pdgId', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]

    genpart_lines_xy = []

    for i in range(nGenPart):
        if not genpart_mask[i]:
            continue

        pt = genpart_pt[i]
        eta = genpart_eta[i]
        phi = genpart_phi[i]
        theta = eta_to_theta(eta)

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
            smp.plottables.LineSpec([x_start, x_end], [y_start, y_end], 
                         c='k', linestyle='--',
                         label=f'Gen: {pid_name}, pt={pt:.1f} GeV')
        )

    IP = smp.plottables.PointSpec([0], [0], c='grey', marker='*', s=100, label='IP')

    smp.scatter_2d(
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
