from typing import Any

import simonplot as smp
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name, common_names
import numpy as np
from simonpy.coordinates import eta_to_theta
import awkward as ak

def PF_event_display(filepath, ievt,
                     PFCname,
                     hits_cut=smp.cut.GreaterThanCut('energy', 0.0),
                     cluster_cut=smp.cut.GreaterThanCut('eta', 0),
                     mode='etaphi',
                     savefig='eventdisplay',
                     verbose=True):
    
    dataset = smp.plottables.NanoEventsDataset(
        fname = filepath, 
        entry_start=ievt, 
        entry_stop=ievt + 1,
        color = 'k',
        label = '',
        key = 'events'
    )

    varX = smp.variable.BasicVariable('x', collection_name=PFCname+"Hits")
    varY = smp.variable.BasicVariable('y', collection_name=PFCname+"Hits")
    varZ = smp.variable.BasicVariable('z', collection_name=PFCname+"Hits")

    varEta = smp.variable.BasicVariable('eta', collection_name=PFCname+"Hits")
    varPhi = smp.variable.BasicVariable('phi', collection_name=PFCname+"Hits")
    varR = smp.variable.Magnitude2dVariable(varX, varY)

    cluster_cut.set_collection_name(PFCname)
    clustermask = cluster_cut.evaluate(dataset)[0] # only one event
    nClus = len(clustermask)

    clus_pt = smp.variable.BasicVariable('pt', collection_name=PFCname).evaluate(dataset, smp.cut.NoCut())[0]

    selected_cluster_indices = [i for i in range(nClus) if clustermask[i]]
    selected_cluster_indices.sort(key=lambda i: float(clus_pt[i]), reverse=True)

    cluster_selections = []
    cluster_labels = []

    for i in selected_cluster_indices:
        clustersel = smp.cut.EqualsCut('clusterIdx', i)
        clustersel.set_collection_name(PFCname+"Hits")
        cluster_selections.append(clustersel)
        cluster_labels.append('pT = %.1f GeV'%clus_pt[i])

    cuts: list[Any] = []
    for clustersel in cluster_selections:
        cuts.append(
            smp.cut.AndCuts([hits_cut, clustersel])
        )
        cuts[-1].set_collection_name(PFCname+"Hits")

    if mode == 'etaphi':
        if verbose:
            print("eta phi plot")
        smp.scatter_2d(
            varEta, varPhi,
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_etaphi",
            legend_loc=(1.05, 0.9, 'upper left'),
        )

        if verbose:
            print("eta R plot")
        smp.scatter_2d(
            varEta, varR,
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_etaR",
            legend_loc=(1.05, 0.9, 'upper left'),
        )

        if verbose:
            print("phi R plot")
        smp.scatter_2d(
            varPhi, varR,
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_phiR",
            legend_loc=(1.05, 0.9, 'upper left'),
        )

    elif mode == 'xyz':
        if verbose:
            print("xy plot")
        smp.scatter_2d(
            varX, varY, 
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_xy",
            legend_loc=(1.05, 0.9, 'upper left'),
        )
        if verbose:
            print("xz plot")
        smp.scatter_2d(
            varX, varZ, 
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_xz",
            legend_loc=(1.05, 0.9, 'upper left'),
        )
        if verbose:
            print("yz plot")
        smp.scatter_2d(
            varY, varZ, 
            cuts, dataset,
            labels_=cluster_labels,
            ensure_square_aspect=True,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_yz",
            legend_loc=(1.05, 0.9, 'upper left'),
        )
    else:
        raise ValueError("Invalid mode %s"%mode)        

def plot_an_event(filepath, ievt, 
                  subdets, truth, 
                  hits_cut=smp.cut.GreaterThanCut('energy', 0.0), 
                  clusters_cut=smp.cut.GreaterThanCut('impact_eta', 0), 
                  genpart_cut = smp.cut.GreaterThanCut('eta', 0),
                  mode = 'etaphi', #options are ['etaphi', 'xyz']
                  show_genpart = True,
                  show_noise=True, 
                  savefig='eventdisplay',
                  verbose = True):
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

    selected_cluster_indices = [i for i in range(nClus) if clustermask[i]]
    selected_cluster_indices.sort(key=lambda i: float(clus_pt[i]), reverse=True)

    for i in selected_cluster_indices:

        clusterselections.append(smp.cut.EqualsCut('cluster0', i))
        pid = str(clus_pdgid[i])
        pid_name = common_names['pdgid_label_lookup'].get(pid, pid)
        clusterlabels.append(f'Sim {pid_name}, pT={clus_pt[i]:.1f} GeV')

    cuts: list[Any] = []
    for clustersel in clusterselections:
        cuts.append(
            smp.cut.ConcatCut.build_for_collections(smp.cut.AndCuts([hits_cut, clustersel]), rechit_collections, unique_cuts_l=rechit_cuts)
        )

    genpart_lines_xy = []
    genpart_lines_xz = []
    genpart_lines_yz = []
    genpart_lines_etaR = []
    genpart_lines_phiR = []

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

        r3Dvar = smp.variable.Magnitude3dVariable(
            varX,
            varY,
            varZ
        )

        r3Dvals = r3Dvar.evaluate(
            dataset, smp.cut.OrCuts(cuts)
        )
        minr3D = ak.min(r3Dvals)
        maxr3D = ak.max(r3Dvals)

        r2Dvals = varR.evaluate(
            dataset, smp.cut.OrCuts(cuts)
        )
        r2D_start = np.min(r2Dvals) * 0.8
        r2D_end = np.max(r2Dvals) * 1.05

        selected_genpart_indices = [i for i in range(nGenPart) if genpart_mask[i]]
        selected_genpart_indices.sort(key=lambda i: float(genpart_pt[i]), reverse=True)

        for i in selected_genpart_indices:

            if verbose:
                print("Setting up genpart", i)

            pt = genpart_pt[i]
            eta = genpart_eta[i]
            phi = genpart_phi[i]
            theta = eta_to_theta(eta)


            start_r3D = minr3D * 0.8
            end_r3D = maxr3D * 1.05

            x_start = start_r3D * np.sin(theta) * np.cos(phi)
            y_start = start_r3D * np.sin(theta) * np.sin(phi)
            z_start = start_r3D * np.cos(theta)

            x_end = end_r3D * np.sin(theta) * np.cos(phi)
            y_end = end_r3D * np.sin(theta) * np.sin(phi)
            z_end = end_r3D * np.cos(theta)

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

            genpart_lines_etaR.append(
                smp.plottables.LineSpec([eta, eta], [r2D_start, r2D_end],
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_lines_phiR.append(
                smp.plottables.LineSpec([phi, phi], [r2D_start, r2D_end],
                            c='k', linestyle='--',
                            label=genlabel)
            )
            genpart_points.append(
                smp.plottables.PointSpec([eta], [phi],
                            c='k', marker='*',
                            s=200, label=genlabel)
            )

    if mode == 'etaphi':
        if verbose:
            print("eta phi plot")
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

        if verbose:
            print("eta R plot")
        smp.scatter_2d(
            varEta, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_etaR",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff = genpart_lines_etaR
        )

        if verbose:
            print("phi R plot")
        smp.scatter_2d(
            varPhi, varR,
            cuts, dataset,
            labels_=clusterlabels,
            ensure_square_aspect=False,
            notext = True,
            ps = 10.0,
            output_path=savefig+"_phiR",
            legend_loc=(1.05, 0.9, 'upper left'),
            add_stuff = genpart_lines_phiR
        )

    elif mode == 'xyz':
        if verbose:
            print("xy plot")
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
        if verbose:
            print("xz plot")
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
        if verbose:
            print("yz plot")
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

        cuts: list[Any] = [smp.cut.AndCuts([rechit_cut, clustercut]) for clustercut in clusterselections]
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
            cuts: list[Any] = [smp.cut.AndCuts([rechit_cut, clustercut, layercut]) for clustercut in clusterselections]
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
       
        cuts: list[Any] = [smp.cut.AndCuts([rechit_cut, clustercut]) for clustercut in clusterselections]
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
