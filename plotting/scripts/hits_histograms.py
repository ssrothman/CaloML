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
                        'RES(genE,recE)'
                        'energy', 'simenergy', 'time', 
                        'nClusters', 'frac0'
                    ], 
                    help='Hit properties to plot (default: [energy, simenergy, time, nClusters, frac0])')

parser.add_argument('--minenergy', type=float, default=None)
parser.add_argument ('--maxenergy', type=float, default=None)
parser.add_argument('--mineta', type=float, default=None)
parser.add_argument('--maxeta', type=float, default=None)
parser.add_argument('--nevts', type=int, default=-1)
parser.add_argument('--force-range', type=float, nargs=2, default=None,
                    help='Force histogram range to given min and max values')

args = parser.parse_args()

import simonplot as smp
from local_util.naming import get_subdet_collection_cut
import os

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

for subdet in args.rechits:
    collection, cut = get_subdet_collection_cut(subdet, args.truth)
    collections.append(collection)
    allcuts = []
    allcuts.append(cut)

    if args.minenergy is not None and args.maxenergy is None:
        allcuts.append(
            smp.cut.GreaterThanCut("%s.simenergy" % collection, args.minenergy)
        )
    elif args.maxenergy is not None and args.minenergy is None:
        allcuts.append(
            smp.cut.LessThanCut("%s.simenergy" % collection, args.maxenergy)
        )
    elif args.minenergy is not None and args.maxenergy is not None:
        allcuts.append(
            smp.cut.TwoSidedCut("%s.simenergy" % collection, args.minenergy, args.maxenergy)
        )

    if len(allcuts) == 1:
        cuts.append(allcuts[0])
    else:
        cuts.append(smp.cut.AndCuts(allcuts))

    labels.append(subdet)

binning = smp.binning.AutoBinning()
if args.force_range is not None:
    binning.force_range(*args.force_range)

for prop in args.properties:
    variables = []
    for collection in collections:
        if prop == 'RES(genE,recE)':
            var = smp.variable.RelativeResolutionVariable(
                smp.variable.BasicVariable("%s.simenergy" % collection),
                smp.variable.BasicVariable("%s.energy" % collection)
            )
        else:
            var = smp.variable.BasicVariable('%s.%s' % (collection, prop))

        variables.append(var)
    

    opath = '%s_%s' % (args.output_prefix, prop)
    ofolder = os.path.dirname(opath)
    oprefix = os.path.basename(opath)

    smp.plot_histogram(
        variables,
        cuts,
        smp.variable.ConstantVariable(1.0),
        ds,
        binning,
        labels,
        logy=True,
        density=True,
        output_folder=ofolder,
        output_prefix=oprefix
    )
