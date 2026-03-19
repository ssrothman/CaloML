import argparse

parser = argparse.ArgumentParser(description='Produce basic simcluster validation plots for CaloML NANO files')
parser.add_argument('input', type=str, 
                    help='Input file (CaloML NANO format)')
parser.add_argument('output_prefix', type=str, 
                    help='Output prefix for plots')
parser.add_argument('--truth', type=str, default='ECALHCAL', 
                    help='Name of truth collection to use (default: ECALHCAL)')
parser.add_argument('--properties', type=str, nargs='+', 
                    default=[
                        #'RES(simE,genE)'
                        #'MAG(vtx0)',
                        #'MAG(calo0)',
                        #'MAG(calo0-vtx0)'
                        #'AKnum',
                        #'frac0',
                        #'simEnergy',  
                        #'nSimHits', 'nParticles', 
                        #'track_pdgId', 
                        #'track_threeCharge',
                        #'track_pt', 'track_eta', 'track_phi', 'track_mass', 
                        #'impact_energy', 
                    ], 
                    help='Hit properties to plot')
args = parser.parse_args()

import simonplot as smp
from local_util.naming import get_simcluster_collection_name

ds = smp.plottables.NanoEventsDataset(
    fname = args.input+":Events",
    #entry_stop=args.nevts,
    color = 'k',
    key = 'events',
    label = ''
)
ds.set_xsec(1)

print("Loaded dataset with %d events" % ds.num_rows)

collections = []
cuts = []
labels = []

collection = get_simcluster_collection_name(args.truth)
cut = smp.cut.NoCut()
label = None

for prop in args.properties:
    if prop == 'frac0':
        var = smp.variable.RatioVariable(
            smp.variable.BasicVariable('%s.energy0' % collection),
            smp.variable.BasicVariable('%s.impact_energy' % collection)
        )
    elif prop == 'AKnum':
        var = smp.variable.AkNumVariable('%s' % collection)
        print(var.key)
    elif prop == 'MAG(vtx0)':
        var = smp.variable.Distance3dVariable(
            smp.variable.BasicVariable('%s.vtx_x0' % collection),
            smp.variable.BasicVariable('%s.vtx_y0' % collection),
            smp.variable.BasicVariable('%s.vtx_z0' % collection),
            smp.variable.BasicVariable("GenVtx.x"),
            smp.variable.BasicVariable("GenVtx.y"),
            smp.variable.BasicVariable("GenVtx.z"),
        )
    elif prop == 'MAG(calo0)':
        var = smp.variable.Distance3dVariable(
            smp.variable.BasicVariable('%s.calo_x0' % collection),
            smp.variable.BasicVariable('%s.calo_y0' % collection),
            smp.variable.BasicVariable('%s.calo_z0' % collection),
            smp.variable.BasicVariable("GenVtx.x"),
            smp.variable.BasicVariable("GenVtx.y"),
            smp.variable.BasicVariable("GenVtx.z"),
        )
    elif prop == 'MAG(calo0-vtx0)':
        var = smp.variable.Distance3dVariable(
            smp.variable.BasicVariable('%s.calo_x0' % collection),
            smp.variable.BasicVariable('%s.calo_y0' % collection),
            smp.variable.BasicVariable('%s.calo_z0' % collection),
            smp.variable.BasicVariable('%s.vtx_x0' % collection),
            smp.variable.BasicVariable('%s.vtx_y0' % collection),
            smp.variable.BasicVariable('%s.vtx_z0' % collection),
        )
    elif prop == 'RES(simE,genE)':
        var = smp.variable.RelativeResolutionVariable(
            smp.variable.BasicVariable("%s.impact_energy" % collection),
            smp.variable.BasicVariable("%s.simEnergy" % collection)
        )
    else:
        var = smp.variable.BasicVariable('%s.%s' % (collection, prop))
    
    print(var.key)

    if 'pdgid' in prop.lower():
        import json
        with open('local_util/common.json', 'r') as f:
            pdgid_lookup = json.load(f)['pdgid_label_lookup']
        binning = smp.binning.AutoIntCategoryBinning(pdgid_lookup)
    else:
        binning = smp.binning.AutoBinning()

    smp.plot_histogram(
        var,
        cut,
        smp.variable.ConstantVariable(1.0),
        ds,
        binning,
        label,
        logy=True,
        output_folder='%s_%s' % (args.output_prefix, prop)
    )
