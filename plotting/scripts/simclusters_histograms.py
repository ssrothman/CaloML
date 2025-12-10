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
                        'simEnergy',  
                        'nSimHits', 'nParticles', 
                        #'track_pdgId', 
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
    var = smu.Variable('%s.%s' % (collection, prop))
    
    smu.plot_histogram(
        var,
        cut,
        ds,
        smu.AutoBinning(),
        label,
        logy=True,
        output_path='%s_%s' % (args.output_prefix, prop)
    )
