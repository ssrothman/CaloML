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
parser.add_argument('--add_simtrack_vertices', action='store_true',
                    help='Whether to add simtrack vertex points to the plots')
parser.add_argument('--add_simtrack_impacts', action='store_true',
                    help='Whether to add simtrack impact points to the plots')
parser.add_argument("--nevts", type=int, default=None,
                    help="Number of events to use (default: all events)")
args = parser.parse_args()

import simon_mpl_util as smu
from local_util.naming import get_subdet_collection_cut, get_simcluster_collection_name

ds = smu.NanoEventsDataset(args.input+":Events", entry_stop=args.nevts)
print("Loaded dataset with %d events" % ds.num_rows)

collections = []
cuts = []
labels = []

for subdet in args.rechits:
    collection, cut = get_subdet_collection_cut(subdet, args.truth)
    collections.append(collection)
    cuts.append(cut)
    labels.append(subdet)

simcluster_collection = get_simcluster_collection_name(args.truth)

if args.add_simtrack_vertices:
    cuts.append(smu.NoCut())
    labels.append("SimTrack Vertices")

if args.add_simtrack_impacts:
    cuts.append(smu.NoCut())
    labels.append("SimTrack Impacts")

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

    if args.add_simtrack_vertices:
        varX.append(
            smu.Variable('%s.vtx_%s0' % (simcluster_collection, props[0]))
        )
        varY.append(
            smu.Variable('%s.vtx_%s0' % (simcluster_collection, props[1]))
        )
    if args.add_simtrack_impacts:
        varX.append(
            smu.Variable('%s.calo_%s0' % (simcluster_collection, props[0]))
        )
        varY.append(
            smu.Variable('%s.calo_%s0' % (simcluster_collection, props[1]))
        )

    output_path = '%s_%s' % (args.output_prefix, ''.join(props))
    if args.add_simtrack_vertices:
        output_path += '_with_simtrack_vertices'
    if args.add_simtrack_impacts:
        output_path += '_with_simtrack_impacts'

    smu.scatter_2d(
        varX, varY,
        cuts,
        ds,
        labels,
        output_path=output_path,
        ensure_square_aspect=True
    )
