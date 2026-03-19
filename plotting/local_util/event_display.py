import simonplot as smp
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name, common_names
import numpy as np
from simonpy.coordinates import eta_to_theta
import awkward as ak

def plot_an_event(filepath, ievt, 
                  subdets, truth, 
                  hits_cut=smp.cut.GreaterThanCut('energy', 0.0), 
                  clusters_cut=smp.cut.GreaterThanCut('impact_eta', 0), 
                  genpart_cut = smp.cut.GreaterThanCut('eta', 0),
                  mode = 'etaphi', #options are ['etaphi', 'xyz']
                  show_genpart = True,
                  show_noise=True, 
                  savefig='eventdisplay'):
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

    Eta = smp.variable.EtaFromXYZVariable(X, Y, Z)
    Phi = smp.variable.PhiFromXYZVariable(X, Y, Z)
    R = smp.variable.Magnitude2dVariable(X, Y)

    varX = smp.variable.ConcatVariable.build_for_collections(X, rechit_collections)
    varY = smp.variable.ConcatVariable.build_for_collections(Y, rechit_collections)
    varZ = smp.variable.ConcatVariable.build_for_collections(Z, rechit_collections)

    varEta = smp.variable.ConcatVariable.build_for_collections(Eta, rechit_collections)
    varPhi = smp.variable.ConcatVariable.build_for_collections(Phi, rechit_collections)
    varR = smp.variable.ConcatVariable.build_for_collections(R, rechit_collections)

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
        clusterlabels.append(f'Sim {pid_name}, pT={clus_pt[i]:.1f} GeV')

    cuts = []
    for clustersel in clusterselections:
        cuts.append(
            smp.cut.ConcatCut.build_for_collections(smp.cut.AndCuts([hits_cut, clustersel]), rechit_collections, unique_cuts_l=rechit_cuts)
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

        genpart_pt = smp.variable.BasicVariable('pt', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
        genpart_eta = smp.variable.BasicVariable('eta', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
        genpart_phi = smp.variable.BasicVariable('phi', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]
        genpart_pdgid = smp.variable.BasicVariable('pdgId', collection_name=genpart_collection).evaluate(dataset, smp.cut.NoCut())[0]

        for i in range(nGenPart):
            if not genpart_mask[i]:
                continue

            pt = genpart_pt[i]
            eta = genpart_eta[i]
            phi = genpart_phi[i]
            theta = eta_to_theta(eta)

            rvar = smp.variable.Magnitude3dVariable(
                varX,
                varY,
                varZ
            )
            rvals = rvar.evaluate(
                dataset, smp.cut.NoCut()
            )
            minr = ak.min(rvals)
            maxr = ak.max(rvals)

            start_r = minr * 0.5
            end_r = maxr * 1.05

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
                smp.plottables.LineSpec([x_start, x_end], [y_start, y_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_lines_xz.append(
                smp.plottables.LineSpec([x_start, x_end], [z_start, z_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_lines_yz.append(
                smp.plottables.LineSpec([y_start, y_end], [z_start, z_end], 
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_points.append(
                smp.plottables.PointSpec([eta], [phi],
                            c='k', marker='*',
                            s=200, label=genlabel)
            )

    if mode == 'etaphi':
        smp.scatter_2d(
            varEta, varPhi,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_etaphi",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff = genpart_points
        )

        smp.scatter_2d(
            varEta, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_etaR",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )

        smp.scatter_2d(
            varPhi, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_phiR",
            legend_loc=(1.05, 0.9, 'upper left'),
            #add_stuff = genpart_points
        )

    elif mode == 'xyz':
        smp.scatter_2d(
            varX, varY, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_xy",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff=genpart_lines_xy
        )
        smp.scatter_2d(
            varX, varZ, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_xz",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff=genpart_lines_xz 
        )
        smp.scatter_2d(
            varY, varZ, 
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=True,
            notext = True,
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
        hits_cut=smp.cut.GreaterThanCut('energy', 0.1), 
        clusters_cut=smp.cut.GreaterThanCut('impact_eta', 0), 
        genpart_cut = smp.cut.GreaterThanCut('eta', 0),
        mode = 'etaphi', #options are ['etaphi', 'xyz', 'barrellayers', 'endcaplayers']
        show_genpart = True,
        barrel=True,
        show_noise=True, 
        savefig='eventbylayer'):

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
    dataset = smp.plottables.NanoEventsDataset(
        fname=filepath, entry_start=ievt, entry_stop=ievt + 1,
        key = 'events',
        label = '',
        color = 'k'
    )


    #identify simclusters
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
        clusterlabels.append(f'Sim {pid_name}, pT={clus_pt[i]:.1f} GeV')

    X = smp.variable.BasicVariable('x')
    Y = smp.variable.BasicVariable('y')
    Z = smp.variable.BasicVariable('z')

    Eta = smp.variable.EtaFromXYZVariable(X, Y, Z)
    Phi = smp.variable.PhiFromXYZVariable(X, Y, Z)

    if doEB:
        rechit_collection, rechit_cut = get_subdet_collection_cut('EB', truth=truth)
        rechit_cut.override_label('ECAL EB')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)

        cuts = [smp.cut.AndCuts([rechit_cut, clustercut]) for clustercut in clusterselections]
        for cut in cuts:
            cut.set_collection_name(rechit_collection)
        
        smp.scatter_2d(
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
        rechit_cut.override_label('HCAL HB')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)

        for layer in range(1, 5):
            layercut = smp.cut.EqualsCut("depth", layer)
            cuts = [smp.cut.AndCuts([rechit_cut, clustercut, layercut]) for clustercut in clusterselections]
            for cut in cuts:
                cut.set_collection_name(rechit_collection)
            
            smp.scatter_2d(
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
        rechit_cut.override_label('HCAL HO')

        Eta.set_collection_name(rechit_collection)
        Phi.set_collection_name(rechit_collection)
       
        cuts = [smp.cut.AndCuts([rechit_cut, clustercut]) for clustercut in clusterselections]
        for cut in cuts:
            cut.set_collection_name(rechit_collection)
        
        smp.scatter_2d(
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
