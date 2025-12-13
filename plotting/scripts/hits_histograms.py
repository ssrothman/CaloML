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
parser.add_argument('--properties', type=str, nargs='+', 
                    default=[
                        #'RES(genE,recE)'
                        #'energy', 'simenergy', 'time', 
                        #'nClusters', 'frac0'
                    ], 
                    help='Hit properties to plot (default: [energy, simenergy, time, nClusters, frac0])')

parser.add_argument('--minenergy', type=float, default=None)
parser.add_argument ('--maxenergy', type=float, default=None)
parser.add_argument('--mineta', type=float, default=None)
parser.add_argument('--maxeta', type=float, default=None)

parser.add_argument('--force-range', type=float, nargs=2, default=None,
                    help='Force histogram range to given min and max values')

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
    allcuts = []
    allcuts.append(cut)

    if args.minenergy is not None and args.maxenergy is None:
        allcuts.append(
            smu.GreaterThanCut("%s.simenergy" % collection, args.minenergy)
        )
    elif args.maxenergy is not None and args.minenergy is None:
        allcuts.append(
            smu.LessThanCut("%s.simenergy" % collection, args.maxenergy)
        )
    elif args.minenergy is not None and args.maxenergy is not None:
        allcuts.append(
            smu.TwoSidedCut("%s.simenergy" % collection, args.minenergy, args.maxenergy)
        )

    if len(allcuts) == 1:
        cuts.append(allcuts[0])
    else:
        cuts.append(smu.AndCuts(*allcuts))

    labels.append(subdet)

binning = smu.AutoBinning()
if args.force_range is not None:
    binning.force_range(*args.force_range)

for prop in args.properties:
    variables = []
    for collection in collections:
        if prop == 'RES(genE,recE)':
            var = smu.RelativeResolutionVariable(
                smu.BasicVariable("%s.simenergy" % collection),
                smu.BasicVariable("%s.energy" % collection)
            )
        else:
            var = smu.BasicVariable('%s.%s' % (collection, prop))

        variables.append(var)
    
    smu.plot_histogram(
        variables,
        cuts,
        ds,
        binning,
        labels,
        logy=True,
        density=True,
        output_path='%s_%s' % (args.output_prefix, prop)
    )
