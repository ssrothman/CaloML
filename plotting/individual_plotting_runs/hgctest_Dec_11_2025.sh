#!/bin/bash

thefile="/home/submit/srothman/cmsdata/CaloML/testing/NANO_Run4_PiGun_Endcaps.root"
mkdir -p plots/hgctest_Dec_11_2025/

python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_offline_nomerge --truth HGCAL --rechits HGCalEE HGCalHSi HGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev1 --truth HGCALv1 --rechits HGCalEE HGCalHSi HGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev2 --truth HGCALv2 --rechits HGCalEE HGCalHSi HGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev3 --truth HGCALv3 --rechits HGCalEE HGCalHSi HGCalHSc --properties energy simenergy time nClusters frac0 &
wait

python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_online_nomerge --truth L1THGCAL --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev1 --truth L1THGCALv1 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev2 --truth L1THGCALv2 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --properties energy simenergy time nClusters frac0 &
python scripts/hits_histograms.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev3 --truth L1THGCALv3 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --properties energy simenergy time nClusters frac0 &
wait

#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_offline --truth HGCAL --rechits HGCalEE HGCalHSi HGCalHSc --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_online --truth L1THGCAL --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --nevts 100 &
#wait


#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_offline_nomerge --truth HGCAL --rechits HGCalEE HGCalHSi HGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev1 --truth HGCALv1 --rechits HGCalEE HGCalHSi HGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev2 --truth HGCALv2 --rechits HGCalEE HGCalHSi HGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_offline_mergev3 --truth HGCALv3 --rechits HGCalEE HGCalHSi HGCalHSc --add_simtrack_vertices --nevts 100 &
#wait

#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_online_nomerge --truth L1THGCAL --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev1 --truth L1THGCALv1 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev2 --truth L1THGCALv2 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --add_simtrack_vertices --nevts 100 &
#python scripts/hits_coordinates.py $thefile plots/hgctest_Dec_11_2025/hits_online_mergev3 --truth L1THGCALv3 --rechits L1THGCalEE L1THGCalHSi L1THGCalHSc --add_simtrack_vertices --nevts 100 &
#wait