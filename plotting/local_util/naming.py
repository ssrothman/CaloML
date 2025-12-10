import json

with open("local_util/common.json", "r") as f:
    common_names = json.load(f)

def get_rechit_collection_name(det, truth):
    return "RecHits{}Truth{}" .format(det, truth)

def get_simcluster_collection_name(truth):
    return "MergedSimCluster{}" .format(truth)

def get_subdet_collection_cut(subdet, truth):
    from simon_mpl_util.Cut import EqualsCut

    (det, index) = common_names['subdet_to_det'][subdet]

    collection = get_rechit_collection_name(det, truth)
    cut = EqualsCut("{}.subdet".format(collection), index)

    return collection, cut
    