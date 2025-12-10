import argparse

parser = argparse.ArgumentParser(description='Produce basic hit validation plots for CaloML NANO files')
parser.add_argument('input', type=str, 
                    help='Input file (CaloML NANO format)')
parser.add_argument('output_prefix', type=str, 
                    help='Output prefix for plots')
parser.add_argument('--truth', type=str, default='ECALHCAL', 
                    help='Name of truth collection to use (default: ECALHCAL)')
parser.add_argument('--rechits', type=str, nargs='+', default=['EB', 'EE', 'ES', 'HB', 'HE', 'HO'], 
                    help='Rechit collections to use (default: [EB, EE, ES, HB, HE, HO])')
parser.add_argument('--properties', type=str, nargs='+', default=['energy', 'simenergy', 'time', 'nClusters', 'frac0'], 
                    help='Hit properties to plot (default: [energy, simenergy, time, nClusters, frac0])')
args = parser.parse_args()

import simon_mpl_util as smu
from local_util.naming import get_subdet_collection_cut

ds = smu.NanoEventsDataset(args.input+":Events")
print("Loaded dataset with %d events" % ds.num_rows)

collections = []
cuts = []
labels = []

for subdet in args.rechits:
    collection, cut = get_subdet_collection_cut(subdet, args.truth)
    collections.append(collection)
    cuts.append(cut)
    labels.append(subdet)

for prop in args.properties:
    variables = []
    for collection in collections:
        var = smu.Variable('%s.%s' % (collection, prop))
        variables.append(var)
    
    smu.plot_histogram(
        variables,
        cuts,
        ds,
        smu.AutoBinning(),
        labels,
        logy=True,
        density=True,
        output_path='%s_%s' % (args.output_prefix, prop)
    )
