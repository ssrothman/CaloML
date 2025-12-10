import argparse

parser = argparse.ArgumentParser(description='Produce hit coordinate plots for CaloML NANO files')
parser.add_argument('input', type=str, 
                    help='Input file (CaloML NANO format)')
parser.add_argument('output_prefix', type=str, 
                    help='Output prefix for plots')
parser.add_argument('--truth', type=str, default='ECALHCAL', 
                    help='Name of truth collection to use (default: ECALHCAL)')
parser.add_argument('--rechits', type=str, nargs='+', default=['EB', 'EE', 'ES', 'HB', 'HE', 'HO'], 
                    help='Rechit collections to use (default: [EB, EE, ES, HB, HE, HO])')
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

vX = 'x'
vY = 'y'
vZ = 'z'

for props in [[vX, vY], [vY, vZ], [vX, vZ]]:
    varX = []
    varY = []
    for collection in collections:
        varX.append(
            smu.Variable('%s.%s' % (collection, props[0]))
        )
        varY.append(
            smu.Variable('%s.%s' % (collection, props[1]))
        )
    
    smu.scatter_2d(
        varX, varY,
        cuts,
        ds,
        labels,
        output_path='%s_%s' % (args.output_prefix, ''.join(props)),
        ensure_square_aspect=True
    )
