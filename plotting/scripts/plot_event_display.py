import argparse
import sys
from typing import Any

import simonplot as smp

from local_util.event_display import PF_event_display, plot_an_event, plot_an_event_by_layer
from local_util.naming import common_names


def _normalize_input_path(path):
    return path if ':' in path else f'{path}:Events'


def _argv_has_option(argv, option):
    return any(token == option or token.startswith(f'{option}=') for token in argv)

def _build_hits_cut(min_hit_energy, side):
    cuts: list[Any] = [smp.cut.GreaterThanCut('energy', min_hit_energy)]
    rechit_z = smp.variable.BasicVariable('z')
    if side == 'pos':
        cuts.append(smp.cut.GreaterThanCut(rechit_z, 0.0))
    elif side == 'neg':
        cuts.append(smp.cut.LessThanCut(rechit_z, 0.0))

    return smp.cut.AndCuts(cuts)


def _build_clusters_cut(min_abs_eta, min_pt, max_abs_eta, side):
    cuts: list[Any] = [smp.cut.GreaterThanCut(smp.variable.AbsVariable('impact_eta'), min_abs_eta)]
    if max_abs_eta is not None:
        cuts.append(smp.cut.LessThanCut(smp.variable.AbsVariable('impact_eta'), max_abs_eta))
    if side == 'pos':
        cuts.append(smp.cut.GreaterThanCut('impact_eta', 0.0))
    elif side == 'neg':
        cuts.append(smp.cut.LessThanCut('impact_eta', 0.0))
    if min_pt is not None:
        cuts.append(smp.cut.GreaterThanCut('impact_pt', min_pt))
    if len(cuts) == 1:
        return cuts[0]
    return smp.cut.AndCuts(cuts)


def _build_pf_clusters_cut(min_abs_eta, min_pt, max_abs_eta, side):
    cuts: list[Any] = [smp.cut.GreaterThanCut(smp.variable.AbsVariable('eta'), min_abs_eta)]
    if max_abs_eta is not None:
        cuts.append(smp.cut.LessThanCut(smp.variable.AbsVariable('eta'), max_abs_eta))
    if side == 'pos':
        cuts.append(smp.cut.GreaterThanCut('eta', 0.0))
    elif side == 'neg':
        cuts.append(smp.cut.LessThanCut('eta', 0.0))
    if min_pt is not None:
        cuts.append(smp.cut.GreaterThanCut('pt', min_pt))
    if len(cuts) == 1:
        return cuts[0]
    return smp.cut.AndCuts(cuts)


def _build_genpart_cut(min_genpart_abs_eta, min_genpart_pt, max_genpart_abs_eta, side):
    cuts: list[Any] = [
        smp.cut.EqualsCut('status', 1),
        smp.cut.GreaterThanCut('pt', min_genpart_pt),
        smp.cut.GreaterThanCut(smp.variable.AbsVariable('eta'), min_genpart_abs_eta)
    ]
    if max_genpart_abs_eta is not None:
        cuts.append(smp.cut.LessThanCut(smp.variable.AbsVariable('eta'), max_genpart_abs_eta))
    if side == 'pos':
        cuts.append(smp.cut.GreaterThanCut('eta', 0.0))
    elif side == 'neg':
        cuts.append(smp.cut.LessThanCut('eta', 0.0))
    return smp.cut.AndCuts(cuts)


def _validate_subdets(subdets):
    valid_subdets = set(common_names['subdet_to_det'].keys())
    invalid_subdets = [subdet for subdet in subdets if subdet not in valid_subdets]
    if invalid_subdets:
        valid_subdet_str = ', '.join(sorted(valid_subdets))
        raise ValueError(
            f'Unknown subdetector(s): {invalid_subdets}. Valid values are: {valid_subdet_str}'
        )


def main():
    parser = argparse.ArgumentParser(
        description='Plot event displays for CaloML NANO files'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input NANO file. Use either /path/to/file.root or /path/to/file.root:Events',
    )
    parser.add_argument(
        'output_prefix',
        type=str,
        help='Output prefix for generated event display files',
    )
    parser.add_argument(
        '--truth',
        type=str,
        default='HGCAL',
        help='Truth collection suffix (default: HGCAL; not supported with --pf)',
    )
    parser.add_argument(
        '--pf',
        action='store_true',
        help='Use PF cluster display instead of simcluster-based display',
    )
    parser.add_argument(
        '--pf-name',
        type=str,
        default=None,
        help='PF cluster table base name for --pf mode (required with --pf)',
    )
    parser.add_argument(
        '--subdets',
        nargs='+',
        default=['HGCalEE', 'HGCalHSi', 'HGCalHSc'],
        help='Subdetectors to draw (default: HGCalEE HGCalHSi HGCalHSc; not supported with --pf)',
    )
    parser.add_argument(
        '--event-start',
        type=int,
        default=0,
        help='First event index (inclusive, default: 0)',
    )
    parser.add_argument(
        '--event-stop',
        type=int,
        default=None,
        help='Last event index (exclusive, default: event-start + 1)',
    )
    parser.add_argument(
        '--mode',
        choices=['etaphi', 'xyz'],
        default='xyz',
        help='Display mode for standard plotting (default: xyz)',
    )
    parser.add_argument(
        '--by-layer',
        action='store_true',
        help='Use layer-by-layer plotting (barrel only)',
    )
    parser.add_argument(
        '--barrel',
        action='store_true',
        help='For --by-layer mode: plot barrel layers (required for now)',
    )
    parser.add_argument(
        '--show-genpart',
        action='store_true',
        help='Overlay selected gen-particles',
    )
    side_group = parser.add_mutually_exclusive_group()
    side_group.add_argument(
        '--pos-side',
        action='store_true',
        help='Require eta >= 0 for rechits/clusters/genparticles',
    )
    side_group.add_argument(
        '--neg-side',
        action='store_true',
        help='Require eta <= 0 for rechits/clusters/genparticles',
    )
    parser.add_argument(
        '--hide-noise',
        action='store_true',
        help='Do not draw rechits labeled as noise',
    )
    parser.add_argument(
        '--min-hit-energy',
        type=float,
        default=0.0,
        help='Minimum rechit energy (default: 0.0)',
    )
    parser.add_argument(
        '--min-cluster-abs-eta',
        type=float,
        default=0.0,
        help='Minimum absolute simcluster eta (default: 0.0)',
    )
    parser.add_argument(
        '--min-cluster-pt',
        type=float,
        default=None,
        help='Optional minimum simcluster pt',
    )
    parser.add_argument(
        '--max-cluster-abs-eta',
        type=float,
        default=None,
        help='Optional maximum absolute simcluster eta',
    )
    parser.add_argument(
        '--min-genpart-abs-eta',
        type=float,
        default=0.0,
        help='Minimum absolute gen particle eta when --show-genpart is set (default: 0.0)',
    )
    parser.add_argument(
        '--max-genpart-abs-eta',
        type=float,
        default=None,
        help='Optional maximum absolute gen particle eta when --show-genpart is set',
    )
    parser.add_argument(
        '--min-genpart-pt',
        type=float,
        default=0.0,
        help='Minimum gen particle pt when --show-genpart is set (default: 0.0)',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging during plotting',
    )
    args = parser.parse_args()

    _validate_subdets(args.subdets)

    if args.event_start < 0:
        raise ValueError('--event-start must be >= 0')

    event_stop = args.event_stop
    if event_stop is None:
        event_stop = args.event_start + 1
    if event_stop <= args.event_start:
        raise ValueError('--event-stop must be greater than --event-start')

    if args.by_layer and not args.barrel:
        raise ValueError('--by-layer currently supports only barrel mode. Pass --barrel.')
    if args.pf and args.by_layer:
        raise ValueError('--pf cannot be combined with --by-layer')
    if args.pf and args.show_genpart:
        raise ValueError('--pf mode does not support --show-genpart')
    if args.pf:
        if args.pf_name is None:
            raise ValueError('--pf requires --pf-name')
        if _argv_has_option(sys.argv[1:], '--truth'):
            raise ValueError('--truth is not supported with --pf')
        if _argv_has_option(sys.argv[1:], '--subdets'):
            raise ValueError('--subdets is not supported with --pf')

    side = None
    if args.pos_side:
        side = 'pos'
    elif args.neg_side:
        side = 'neg'

    input_path = _normalize_input_path(args.input)
    hits_cut: Any = _build_hits_cut(args.min_hit_energy, side)
    clusters_cut: Any = _build_clusters_cut(
        args.min_cluster_abs_eta,
        args.min_cluster_pt,
        args.max_cluster_abs_eta,
        side,
    )
    pf_clusters_cut: Any = _build_pf_clusters_cut(
        args.min_cluster_abs_eta,
        args.min_cluster_pt,
        args.max_cluster_abs_eta,
        side,
    )
    genpart_cut: Any = _build_genpart_cut(
        args.min_genpart_abs_eta,
        args.min_genpart_pt,
        args.max_genpart_abs_eta,
        side,
    )

    for ievt in range(args.event_start, event_stop):
        output_base = f'{args.output_prefix}_evt{ievt:06d}'
        if args.verbose:
            print(f'Plotting event {ievt} -> {output_base}')

        if args.pf:
            PF_event_display(
                filepath=input_path,
                ievt=ievt,
                PFCname=args.pf_name,
                hits_cut=hits_cut,
                cluster_cut=pf_clusters_cut,
                mode=args.mode,
                savefig=output_base,
                verbose=args.verbose,
            )
        elif args.by_layer:
            plot_an_event_by_layer(
                filepath=input_path,
                ievt=ievt,
                subdets=args.subdets,
                truth=args.truth,
                hits_cut=hits_cut,
                clusters_cut=clusters_cut,
                genpart_cut=genpart_cut,
                mode='etaphi',
                show_genpart=args.show_genpart,
                barrel=args.barrel,
                show_noise=not args.hide_noise,
                savefig=output_base,
            )
        else:
            plot_an_event(
                filepath=input_path,
                ievt=ievt,
                subdets=args.subdets,
                truth=args.truth,
                hits_cut=hits_cut,
                clusters_cut=clusters_cut,
                genpart_cut=genpart_cut,
                mode=args.mode,
                show_genpart=args.show_genpart,
                show_noise=not args.hide_noise,
                savefig=output_base,
                verbose=args.verbose,
            )


if __name__ == '__main__':
    main()