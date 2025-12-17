import simon_mpl_util as smu
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name, common_names
import numpy as np

def plot_an_event(filepath, ievt, 
                  subdets, truth, 
                  hits_cut=smu.GreaterThanCut('energy', 0.1), 
                  clusters_cut=smu.GreaterThanCut('impact_eta', 0), 
                  genpart_cut = smu.GreaterThanCut('eta', 0),
                  mode = 'etaphi', #options are ['etaphi', 'xyz', 'barrellayers', 'endcaplayers']
                  show_genpart = True,
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

    Eta = smu.EtaFromXYZVariable(X, Y, Z)
    Phi = smu.PhiFromXYZVariable(X, Y, Z)
    R = smu.Magnitude2dVariable(X, Y)

    varX = smu.ConcatVariable.build_for_collections(X, rechit_collections)
    varY = smu.ConcatVariable.build_for_collections(Y, rechit_collections)
    varZ = smu.ConcatVariable.build_for_collections(Z, rechit_collections)

    varEta = smu.ConcatVariable.build_for_collections(Eta, rechit_collections)
    varPhi = smu.ConcatVariable.build_for_collections(Phi, rechit_collections)
    varR = smu.ConcatVariable.build_for_collections(R, rechit_collections)

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
        clusterlabels.append(f'Sim {pid_name}, pT={clus_pt[i]:.1f} GeV')

    cuts = []
    for clustersel in clusterselections:
        cuts.append(
            smu.ConcatCut.build_for_collections(smu.AndCuts(hits_cut, clustersel), rechit_collections, unique_cuts_l=rechit_cuts)
        )

    genpart_lines_xy = []
    genpart_lines_xz = []
    genpart_lines_yz = []

    genpart_points = []

    if show_genpart:
        #get gen particles
        genpart_collection = 'GenPart'
        genpart_cut.set_collection_name(genpart_collection)
        genpart_mask = genpart_cut.evaluate(dataset)[0] #only one event
        nGenPart = len(genpart_mask)

        genpart_pt = smu.BasicVariable('pt', collection_name=genpart_collection).evaluate(dataset)[0]
        genpart_eta = smu.BasicVariable('eta', collection_name=genpart_collection).evaluate(dataset)[0]
        genpart_phi = smu.BasicVariable('phi', collection_name=genpart_collection).evaluate(dataset)[0]
        genpart_pdgid = smu.BasicVariable('pdgId', collection_name=genpart_collection).evaluate(dataset)[0]

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

            pid = str(genpart_pdgid[i])
            pid_name = common_names['pdgid_label_lookup'].get(pid, 'unknown')
            genlabel = f'Gen {pid_name}, pt={pt:.1f} GeV'

            genpart_lines_xy.append(
                smu.LineSpec([x_start, x_end], [y_start, y_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_lines_xz.append(
                smu.LineSpec([x_start, x_end], [z_start, z_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_lines_yz.append(
                smu.LineSpec([y_start, y_end], [z_start, z_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_points.append(
                smu.PointSpec([eta], [phi],
                            c='k', marker='*',
                            s=200, label=genlabel)
            )

    if mode == 'etaphi':
        smu.scatter_2d(
            varEta, varPhi,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_etaphi",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff = genpart_points
        )

        smu.scatter_2d(
            varEta, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_etaR",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )

        smu.scatter_2d(
            varPhi, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_phiR",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )

    elif mode == 'xyz':
        smu.scatter_2d(
            varX, varY, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_xy",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff=genpart_lines_xy
        )
        smu.scatter_2d(
            varX, varZ, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_xz",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff=genpart_lines_xz 
        )
        smu.scatter_2d(
            varY, varZ, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_yz",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff=genpart_lines_yz
        )
    else:
        raise ValueError("Invalid mode %s"%mode)
    
def plot_an_event_by_layer(
        filepath, ievt, 
        subdets, truth, 
        hits_cut=smu.GreaterThanCut('energy', 0.1), 
        clusters_cut=smu.GreaterThanCut('impact_eta', 0), 
        genpart_cut = smu.GreaterThanCut('eta', 0),
        mode = 'etaphi', #options are ['etaphi', 'xyz', 'barrellayers', 'endcaplayers']
        show_genpart = True,
        barrel=True,
        show_noise=True, 
        savefig=None):

    #check inputs

    doEB = 'EB' in subdets
    #doEE = 'EE' in subdets
    #doES = 'ES' in subdets

    doHB = 'HB' in subdets
    #doHE = 'HE' in subdets
    doHO = 'HO' in subdets

    if barrel and not (doEB or doHB or doHO):
        raise ValueError("Asked for barrel, but no barrel subdets!")
    
    if not barrel:
        raise NotImplementedError("Endcaps by layer not yet supported")
    
    #build dataset
    dataset = smu.NanoEventsDataset(filepath, entry_start=ievt, entry_stop=ievt + 1)


    #identify simclusters
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
        clusterlabels.append(f'Sim {pid_name}, pT={clus_pt[i]:.1f} GeV')

    X = smu.BasicVariable('x')
    Y = smu.BasicVariable('y')
    Z = smu.BasicVariable('z')

    Eta = smu.EtaFromXYZVariable(X, Y, Z)
    Phi = smu.PhiFromXYZVariable(X, Y, Z)

    if doEB:
        rechit_collection, rechit_cut = get_subdet_collection_cut('EB', truth=truth)
        rechit_cut.override_plottext('ECAL EB')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)

        cuts = [smu.AndCuts(rechit_cut, clustercut) for clustercut in clusterselections]
        for cut in cuts:
            cut.set_collection_name(rechit_collection)
        
        smu.scatter_2d(
            Eta, Phi,
            cuts, dataset,
            labels_= clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_etaphi_EB",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )
    if doHB:
        rechit_collection, rechit_cut = get_subdet_collection_cut('HB', truth=truth)
        rechit_cut.override_plottext('HCAL HB')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)

        for layer in range(1, 5):
            layercut = smu.EqualsCut("depth", layer)
            cuts = [smu.AndCuts(rechit_cut, clustercut, layercut) for clustercut in clusterselections]
            for cut in cuts:
                cut.set_collection_name(rechit_collection)
            
            smu.scatter_2d(
                Eta, Phi,
                cuts, dataset,
                labels_= clusterlabels,
                ensure_square_aspect=True,
                notext = False,
                ps = 10.0,
                output_path=savefig+"_etaphi_HB%d"%layer,
                legend_loc=(1.05, 0.9, 'upper left'),
                #add_stuff = genpart_points
            )
    if doHO:
        rechit_collection, rechit_cut = get_subdet_collection_cut('HO', truth=truth)
        rechit_cut.override_plottext('HCAL HO')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)
       
        cuts = [smu.AndCuts(rechit_cut, clustercut) for clustercut in clusterselections]
        for cut in cuts:
            cut.set_collection_name(rechit_collection)
        
        smu.scatter_2d(
            Eta, Phi,
            cuts, dataset,
            labels_= clusterlabels,
            ensure_square_aspect=True,
            notext = False,
            ps = 10.0,
            output_path=savefig+"_etaphi_HO",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )
