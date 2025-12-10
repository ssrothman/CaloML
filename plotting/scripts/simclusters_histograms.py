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
                        'MAG(vtx0)',
                        'MAG(calo0)',
                        'MAG(calo0-vtx0)'
                        'AKnum',
                        'frac0',
                        'simEnergy',  
                        'nSimHits', 'nParticles', 
                        'track_pdgId', 
                        'track_threeCharge',
                        'track_pt', 'track_eta', 'track_phi', 'track_mass', 'impact_energy', 
                    ], 
                    help='Hit properties to plot')
args = parser.parse_args()

import simon_mpl_util as smu
from local_util.naming import get_simcluster_collection_name

ds = smu.NanoEventsDataset(args.input+":Events")
print("Loaded dataset with %d events" % ds.num_rows)

collections = []
cuts = []
labels = []

collection = get_simcluster_collection_name(args.truth)
cut = smu.NoCut()
label = None

for prop in args.properties:
    if prop == 'frac0':
        var = smu.RatioVariable(
            smu.Variable('%s.energy0' % collection),
            smu.Variable('%s.impact_energy' % collection)
        )
    elif prop == 'AKnum':
        var = smu.AkNumVariable('%s' % collection)
        print(var.key)
    elif prop == 'MAG(vtx0)':
        var = smu.Distance3dVariable(
            smu.Variable('%s.vtx_x0' % collection),
            smu.Variable('%s.vtx_y0' % collection),
            smu.Variable('%s.vtx_z0' % collection),
            smu.Variable("GenVtx.x"),
            smu.Variable("GenVtx.y"),
            smu.Variable("GenVtx.z"),
        )
    elif prop == 'MAG(calo0)':
        var = smu.Distance3dVariable(
            smu.Variable('%s.calo_x0' % collection),
            smu.Variable('%s.calo_y0' % collection),
            smu.Variable('%s.calo_z0' % collection),
            smu.Variable("GenVtx.x"),
            smu.Variable("GenVtx.y"),
            smu.Variable("GenVtx.z"),
        )
    elif prop == 'MAG(calo0-vtx0)':
        var = smu.Distance3dVariable(
            smu.Variable('%s.calo_x0' % collection),
            smu.Variable('%s.calo_y0' % collection),
            smu.Variable('%s.calo_z0' % collection),
            smu.Variable('%s.vtx_x0' % collection),
            smu.Variable('%s.vtx_y0' % collection),
            smu.Variable('%s.vtx_z0' % collection),
        )
    else:
        var = smu.Variable('%s.%s' % (collection, prop))
    
    print(var.key)

    if 'pdgid' in prop.lower():
        import json
        with open('local_util/common.json', 'r') as f:
            pdgid_lookup = json.load(f)['pdgid_label_lookup']
        binning = smu.AutoIntCategoryBinning(pdgid_lookup)
    else:
        binning = smu.AutoBinning()

    smu.plot_histogram(
        var,
        cut,
        ds,
        binning,
        label,
        logy=True,
        output_path='%s_%s' % (args.output_prefix, prop)
    )
