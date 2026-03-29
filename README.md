 # CMSSW Sim Truth Package <!-- omit from toc -->

 This package provides utilities for:
  
   - Accessing the sim-level truth information as provided by Geant
   - Merging simclusters according to various geometric and physics criteria 
   - Writing flat NanoAOD tables for:
     - SimHits
     - RecHits
     - SimClusters [including information from the associated Geant tracks]
     - RecHit assignment to SimClusters 
     - PF Clusters, and associated PF RecHits

This code is designed to be completely modular and compatible with all of the different CMSSW calorimeter hit datatypes, including all calorimeter subsystems (ECAL [EB, EE, ES], HCAL [HBHE, HO,HF], HGCAL, and HGCAL L1T (including both trigger cell granularity and whole-module granularity)). Note that the L1T HGCAL functionality requires the L1 HGCAL Trigger Primitives branch [see later]. 

Truth definitions are easy to create for different subdetectors, or multiple simultaneous subdetectors (eg ECAL+HCAL). Default definitions are provided for ECAL, HCAL, ECAL+HCAL, HGCAL, and L1THGCAL

- [1. Quick start](#1-quick-start)
  - [1.1 Setup your environment](#11-setup-your-environment)
    - [Offline truth](#offline-truth)
    - [HGCAL L1 Trigger Truth](#hgcal-l1-trigger-truth)
  - [1.2 Example configs](#12-example-configs)
- [2. NANO file contents](#2-nano-file-contents)
  - [detid reference](#detid-reference)
- [3. Custom configuration](#3-custom-configuration)
  - [3.1 SimHits setup](#31-simhits-setup)
    - [HCAL setup](#hcal-setup)
    - [HGCAL setup](#hgcal-setup)
    - [L1THGCAL setup](#l1thgcal-setup)
    - [ECAL setup](#ecal-setup)
  - [3.2 Build merged sim truth](#32-build-merged-sim-truth)
  - [3.3 Write flat NanoAOD tables](#33-write-flat-nanoaod-tables)
    - [Merged Simclusters](#merged-simclusters)
    - [SimHits](#simhits)
    - [RecHits](#rechits)
    - [HGCAL Modules](#hgcal-modules)
    - [PF Clusters](#pf-clusters)
- [4. Config generation](#4-config-generation)
  - [4.1 GEN-SIM-DIGI](#41-gen-sim-digi)
  - [4.2 RECO](#42-reco)
  - [4.3 NANO](#43-nano)
- [5. Plotting](#5-plotting)
- [6. Technical details](#6-technical-details)


## 1. Quick start

This has only been tested with `CMSSW_15_0_0` and `CMSSW_15_0_6`, but I don't see any reason it shouldn't be easy to get it working in any reasonably modern CMSSW release

### 1.1 Setup your environment 

#### Offline truth

Just build this package against CMSSW:

```bash
cmsrel CMSSW_15_0_6
cd CMSSW_15_0_6/src
cmsenv
git clone git@github.com:ssrothman/CaloML.git -b CMSSW_15_0_X
scram b -j8
```

#### HGCAL L1 Trigger Truth

For HGCAL L1T you need the HGCAL trigger primitives simulation code:

```bash
cmsrel CMSSW_15_0_6
cd CMSSW_15_0_6/src
cmsenv
git cms-init
git cms-merge-topic ssrothman:ECON_15_0_6
git clone git@github.com:ssrothman/CaloML.git -b CMSSW_15_0_X
scram b -j8
```

### 1.2 Example configs

Example `cmsRun` configs can be found in `CaloML/SimTruth/test/`. By default I have provided an example config for Run3 ECAL+HCAL clustering ([run3_NANO.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/SimTruth/test/run3_NANO.py)) and an example config for simultaneous online+offline Run4 HGCAL clustering ([run4_NANO.py]((https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/SimTruth/test/run4_NANO.py))).

An appropriate input file must contain:
 - All of the RecHits for the subdetector(s) of interest
 - The geant4 sim information

Then, simply modify the test config to point at your input file, and run 

```bash
cmsRun CaloML/SimTruth/test/<cfg>.py
```

## 2. NANO file contents

The NANO files produced by this package contain the following branches (where fields formatted `<x>` should be replaced with the appropriate string):

 - `SimHits<subdet>`: the simhits for truth definition labeled by `subdet`, with fields for detId, energy, time, and cartesian coordinates
 - `MergedSimCluster<subdet>`: the merged truth simclusters for the truth definition labeled by `subdet`, with fields for the number of simhits, the simenergy, and the properties of the corresponding sim truth particle 
 - `RecHits<subdet>Truth<truth>`: the rechits for subdetector `subdet` and truth information corresponding to the truth definition labeled by `truth`. There are fields for thedetId, energy, and cartesian coordinates, as well as truth information, in the following format:
   - a `simenergy` field for the total sim energy deposited in the detector cell
   - a `nClusters` field for the total number of matched sim clusters
   - The top four matched sim clusters, described as four pairs of `cluster<i>` and `frac<i>` fields for `i` from 0 to 3. 
     - `cluster<i>` contains the index in the SimClusters table of the truth simcluster with rank `i`, and
     - `frac<i>` is the floating-point fraction of the simenergy in this RecHit that is attributable to that SimCluster. 
     - These are sorted such that `frac<i> >= frac<i+1>`. 
     - When there is no corresponding truth information `frac<i> = 0` and `cluster<i> = -1`

For more details see section 3.3.

### detid reference

The `det` and `subdet` fields are opaque integers, referencing internal CMSSW enums. For reference, I reproduce here the lookup:

The det field is
```c++
enum Detector {
    Tracker = 1,
    Muon = 2,
    Ecal = 3,
    Hcal = 4,
    Calo = 5,
    Forward = 6,
    VeryForward = 7,
    HGCalEE = 8,
    HGCalHSi = 9,
    HGCalHSc = 10,
    HGCalTrigger = 11
};
```

The ECAL subdetector field is 
```c++
enum EcalSubdetector { 
  EcalBarrel = 1, 
  EcalEndcap = 2, 
  EcalPreshower = 3, 
  EcalTriggerTower = 4, 
  EcalLaserPnDiode = 5 
};
```

The HCAL subdetector field is
```c++
enum HcalSubdetector {
  HcalEmpty = 0,
  HcalBarrel = 1,
  HcalEndcap = 2,
  HcalOuter = 3,
  HcalForward = 4,
  HcalTriggerTower = 5,
  HcalOther = 7
};
```

The HGCAL subdetector field is
```c++
enum ForwardSubdetector {
  ForwardEmpty = 0,
  FastTime = 1,
  BHM = 2,
  HGCEE = 3,
  HGCHEF = 4,
  HGCHEB = 5,
  HFNose = 6,
  HGCTrigger = 7
};
```

The L1T HGCAL subdetector field is
```c++
enum HGCalTriggerSubdetector { 
  HFNoseTrigger = 0, 
  HGCalEETrigger = 1, 
  HGCalHSiTrigger = 2, 
  HGCalHScTrigger = 3 
};
```


## 3. Custom configuration

### 3.1 SimHits setup

The SimHits for HGCAL, L1THGCAL, and HCAL need some additional setup before we can build the truth:

#### HCAL setup

HCAL SimHits need to be [relabled](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/plugins/RelabelledHcalSimHitsProducer.cc) and [calibrated]((https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/plugins/CalibratedHcalSimHitsProducer.cc)) before passing them to the rest of my code. I have defined a process modifier `setupHcalSimHits()`, defined in [SimHits_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/SimHits_cff.py) for this task. 

#### HGCAL setup

HGCAL SimHits need to be [calibrated](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/plugins/CalibratedHGCalSimHitProducer.cc) before passing them to the rest of my code. I have defined a process modifier `setupCalibratedHGCalSimHits()`, defined in [SimHits_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/SimHits_cff.py) for this task. 

#### L1THGCAL setup

The L1THGCAL truth code takes as input the calibrated HGCAL SimHits defned above, and then merges them according to the L1T HGCAL Trigger Cell geometry ([code](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/plugins/TriggerCellSimHitsProducer.cc)). I have defined a process modifier `setupL1THGCalSimHits()`, defined in [SimHits_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/SimHits_cff.py) for this task. 

Note that L1T HGCAL setup requres both the `setupCalibratedHGCalSimHits()` and `setupL1THGCalSimHits()` process modifiers. 

#### ECAL setup

Currently, ECAL hits do not require any additional setup.

### 3.2 Build merged sim truth

The SimTruth definition is built in multiple steps, corresponding to different physical and geometric merging steps. The truth definition is setup by the `setupSimTruth(subdet)` process modifier, defned in [SimTruth_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/SimTruth/python/SimTruth_cff.py). The `subdet` argument is a lookup into the dictionary of confguration parameters defined in [common_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/SimTruth/python/common_cff.py). By default, the supported `subdet`'s are 

 - HGCAL: offline HGCAL truth
 - L1THGCAL: HGCAL truth for L1 trigger
 - HCAL: Simultaneous truth for HBHE, HO, and HF
 - ECALALL: Simultaneous truth for EB, EE, and ES
 - ECALBARREL: Truth for EB
 - ECALHCAL: Simultaneous truth for HCAL (as above) and EB (as above)

The behavior can easily be modified by changng the parameters in `common_cff.py`, or else by defining new `subdet`'s. Note that the `subdet` string is used in the names of various CMSSW modules and so any new `subdet` names should be distinct from all others (to avoid name clashes) and follow all CMSSW naming rules (eg no underscores). 

### 3.3 Write flat NanoAOD tables

I have provided various utilities to write RecHit and SimHit postion, detector information, energies, timing, etc. The available NANOAOD tables are:

#### Merged Simclusters

The NANO table for merged simclusters is setup with `setupSimTruthTables(truth)` (defined in [SimTruth_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/SimTruth/python/SimTruth_cff.py)). The argument to this function is the name of the truth definition from the lookup table in `common_cff.py`.

This table includes the following imformation:
```python

'''
Properties arising from the associated simhits
'''
nSimHits : int # number of associated simhits
simEnergy : float # total associated sim energy

'''
 Properties of the (merged) Geant track associated with the simcluster.

 This track is generated by my truth merging algorithm, and depending on the truth merging the pdgId may be undefined
'''
track_pt
track_eta
track_phi
track_energy
track_mass
track_pdgId
track_threeCharge

'''
Properties of the (merged) Geant track, extrapolated to the front face of the calorimeter
'''
impact_energy
impact_eta
impact_phi
impact_pt

'''
Properties of the four leading geant tracks that were merged to form this merged simcluster
'''
pdg{0-3} : int # pdgId 
energy{0-3} : float # energy
reason{0-3} : int # flag describing the reason that this track was merged into the merged truth definition
vtx_{x,y,z,t}{0-3} : float # xyzt coordinates of the vertex at which this geant track was produced (need not be the original impact point)
calo_{x,y,z,t}{0-3} : float # xyzt coordinates of the point at which this geant track was extrapolated to the front face of the calorimeter
```

#### SimHits

The NANO table for SimHits is setup with `setupSimHitTables(truth)` (defined in [SimHits_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/SimHits_cff.py)). The argument to this function is the name of the truth definition from the lookup table in `common_cff.py`.

This table includes the following imformation:
```python
'''
xyz coordinates for the simhit
'''
x : float 
y : float
z : float

'''
hit properties
'''
energy : float
time : float

'''
properties of the detector cell that recorded the hit
'''
det : int # CMSSW detector enum
subdet: int # CMSSW subdetector enum

# HCAL-specific:
depth : int # HCAL depth int 

# HGCAL-specific:
layer : int # layer depth
zside : int # +-1 for which endcap we are in
waferU : int # waferU for silicon, ieta for scintilator 
waferV : int # waferV for silicon, iphi for scintilator 
cellU : int # cellU for silicon, ieta for scintilator 
cellV : int # cellV for silicon, iphi for scintilator 
hwType : int # enum denoting hardware type
            # si: 
            #     0 - high density 120um
            #     1 - low density 200um
            #     2 - low density 300um
            #     3 - high density 200um
            # sc: (sipm enum) + 2 * (granularity enum) + 4 * (tiletype enum) 
            # with
            #   sipm enum:
            #        0 - small
            #        1 - large
            #   granularity enum:
            #        0 - normal
            #        1 - fine
            #   tilestype enum:
            #        1 - "c"
            #        2 - "m"
```

#### RecHits

The NANO table for RecHits is setup by`setupRecHitTables(subdet, truth)` (defined in [RecHits_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/RecHits_cff.py)). The two arguments are:
  - `subdet` : the reco-level subdetector to get RecHits for
  - `truth` : the name of the truth definition (from common_cff.py) to get the truth quantities from
  
These arguments are segmented to allow for the possibilty of running multiple truth definitions at once (eg for testing, comparison). Note that because the HCAL uses different datatypes for HBHE, HF, and HO, this list of valid `subdet`'s at RecHit level is different from the list of valid `subdet`'s at sim level. 

This table includes all the same information as the simhits tables, plus the following truth info:
```python
nClusters : int # number of associated merged simclusters
simenergy : float # total associated simenergy

#for the leading (up to) 4 associated simclusters:
cluster{0-3} : int # index of the simcluster in the mergedsimclusters collection
frac{0-3} : float # fraction of the associated simenergy that is due to this source
```

#### HGCAL Modules

For HGCAL L1T studies, I have also implemented support for writing out information at module-level granularity (eg the silicon wafers, consisting of 48 trigger cells each). This is set up with `setupHGCWaferInfoTables(subdet, truth)` (defined in [HGCWafers_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/CaloHits/python/HGCWafers_cff.py)). The two arguments are the same as for the RecHits

This produces three tables. 

First, the main wafer properties table, which includes:
```python
'''
generic properties
'''
waferid : int # unique ID number for the HGCAL module
det : int # CMSSW detector enum
subdet : int # CMSSW subdetector enum
waferU : int # si - waferU ; sc - ieta
waferV : int # si - waferV ; sc - iphi
hwType : int # wafertype enum. same as RecHits table
zside : int # +-1 for pos/minus endcap

'''
coordinates of module center
'''
x,y,z : float
eta,phi : float

'''
energy
'''
energy : float # sum of reconstructed energy over all associated TCs

'''
truth information.
Uses the same truth definition as for the TCs
Just summed over all the TCs in the module
'''
simenergy : float # sum of simenergy over all associated TCs
# for the 4 leading associated merged simclusters
cluster{0-3} : int # index in the MergedSimclusters collection
frac{0-3} : float # fraction of associated simenergy due to that source

'''
Number of associated TCs 
(used to reshape TCs array)
'''
nTC : int # number of associated trigger cells that pass zero-suppression (ie that appear in the RecHits table)

'''
ECON inputs
'''
sumCALQ : int # sum of CALQ values across all associated TCs
```

Then, there is the table of associated TCs. This has only one branch:
```python
TCidx : int # index of the associated TC in the TCs collection
```
This can be used to get the array of associated trigger cells per module. For example:
```python
 >>> TCs = x.RecHitsL1THGCALTruthL1THGCAL
 >>> wafers = x.HGCWafers
 >>> idx = x.HGCWafersTCs.TCidx
 >>> nTC = ak.flatten(wafers.nTC, axis=None)
 >>> TCs_per_wafer = ak.unflatten(TCs[idx], nTC, axis-=1)
```

Finally, there is the ECON inputs table. This has:
```python
ADC: int # raw ADC value from ROC emulation
norm: int # normalization constants 
CALQ : int # normalized CALQ values (= ADC * norm)
AEin : float # quantized AE inputs, casted to float and normalized to [0-1]
```
This table has 64 entries per module, corresponding to the 8x8 AE input space (for the conv2D). To get the values per module, you can unflatten:
```python
 >>> ECON_per_module = ak.unflatten(x.HGCWafersECONinputs, 64, axis=-1)
 >>> ECON_8x8 = ak.unflatten(ECON_per_module, 8, axis=-=1)
```

Finally, this also adds another branch to the RecHits table with the TC -> module mapping:
```python
waferidx : int # index in the HGCWafers array
```

#### PF Clusters

For particle flow studies and comparison with different PF algorithms, I also have implemented support for PF clusters. This produces two tables: one for PF Clusters and one for the associated PFRecHits. These are set up with `setupClusterTables()` from [ClusterTables_cff.py](https://github.com/ssrothman/CaloML/blob/CMSSW_15_0_X/PFClusters/python/ClusterTables_cff.py). 

The PF Clusters table has the following fields:
```python
energy : flat # total reco energy for the cluster

# centroid(?) coordinates
eta : float
phi : float
x : float
y : float
z : float
layer : int # "Layer" ie subdetector
depth : float # in HCAL depth segementation
time : float
nHits : int # used to unflatten the Hits table
```

And the PFRecHits table has the following fields:
```python
'''
cluster properties
'''
clusterIdx : int # index of the associated PFCluster
clusterEnergy : float # energy of the associated PFCluster

'''
hit properties
'''
time : float
energy : float
fractionInCluster : float # between 0-1. Fraction of energy assigned to PFcluster
energyInCluster : float # = energy * fraction
flags : int # flags 

'''
coordinates / detector cell properties
'''
x : float
y : float
z : float 
eta : float
phi : float
detId : int # unique ID for the detector cell
det : int # CMSSW detector enum
subdet : int # CMSSW subdetector enum
```

## 4. Config generation

The NANO configurations from this repo are compatible with edm files generated in any way, so long as they have the necessary branches. That said, I have also set up a recipe for generating MC from scratch. There are two steps:

### 4.1 GEN-SIM-DIGI

We can generate cmsRun configs with `cmsDriver.py`. There are two different commands for Run 3 or Run 4.

Run 3:
```bash
cmsDriver.py Configuration/Generator/python/SinglePiPt10_pythia8_cfi.py \
    --fileout GSD.root \
    --mc \
    --eventcontent FEVTDEBUG \
    --datatier GEN-SIM-DIGI-RAW \
    --step GEN,SIM,DIGI,L1,DIGI2RAW,HLT:@relval2024 \
    --conditions auto:phase1_2024_realistic  \
    --era Run3_2024  \
    --beamspot Realistic25ns13p6TeVEarly2022Collision  \
    --no_exec \
    --python_filename=CaloML/Processing/test/GSD_Run3.py \
    --customise CaloML/Processing/customize_generator_cff.customize_particle_gun
```

Run 4:
```bash
cmsDriver.py Configuration/Generator/python/SinglePiPt10_pythia8_cfi.py \
    --fileout GSD.root \
    --mc \
    --eventcontent FEVTDEBUG \
    --datatier GEN-SIM-DIGI-RAW \
    --step GEN,SIM,DIGI,L1TrackTrigger,L1,L1P2GT,DIGI2RAW,HLT:@relvalRun4 \
    --geometry ExtendedRun4D110 \
    --conditions auto:phase2_realistic_T33_13TeV \
    --era Phase2C17I13M9 \
    --beamspot NoSmear \
    --no_exec \
    --python_filename=CaloML/Processing/test/GSD_Run4.py \
    --customise CaloML/Processing/customize_generator_cff.customize_particle_gun
```

### 4.2 RECO

Run 3:
```bash
cmsDriver.py step4 \
    --filein GSD.root \
    --fileout RECO.root \
    --mc \
    --eventcontent FEVTDEBUG \
    --datatier GEN-SIM-RECO \
    --step RAW2DIGI,L1Reco,RECO,RECOSIM \
    --conditions auto:phase1_2024_realistic \
    --era Run3_2024 \
    --no_exec \
    --python_filename=CaloML/Processing/test/RECO_Run3.py
```

Run 4:
```bash
cmsDriver.py step4 \
    --filein GSD.root \
    --fileout RECO.root \
    --mc \
    --eventcontent FEVTDEBUG \
    --datatier GEN-SIM-RECO \
    --step RAW2DIGI,L1Reco,RECO,RECOSIM \
    --geometry ExtendedRun4D110 \
    --conditions auto:phase2_realistic_T33 \
    --era Phase2C17I13M9 \
    --no_exec \
    --python_filename=CaloML/Processing/test/RECO_Run4.py
```

### 4.3 NANO

This step can be run off any edm files that contain the needed information. To align with the syntax expected by `cmsDriver`, I have defined some "sequences" in CaloML/Processing/SimTruthSequences_cff.py. Custom sequences can be created as detailed in section 3. 

Using this syntax, NANO step configs can be created with:

Run 3:
```bash
cmsDriver.py NANO \
    --filein RECO.root \
    --fileout NANO.root \
    --mc \
    --eventcontent NANOAODSIM \
    --datatier NANOAODSIM \
    --step NANO \
    --conditions auto:phase1_2024_realistic \
    --era Run3_2024 \
    --no_exec \
    --python_filename=CaloML/Processing/test/NANO_Run3.py \
    --customise CaloML/Processing/SimTruthSequences_cff.SimTruthSequence_ECALHCAL,\
CaloML/SimTruth/GenParticles_cff.setupGenParticlesTables \
    --customise_commands="process.schedule.remove(process.nanoAOD_step)"
```

Run 4:
```bash
cmsDriver.py NANO \
    --filein RECO.root \
    --fileout NANO.root \
    --mc \
    --eventcontent NANOAODSIM \
    --datatier NANOAODSIM \
    --step NANO \
    --geometry ExtendedRun4D110 \
    --conditions auto:phase2_realistic_T33 \
    --era Phase2C17I13M9 \
    --no_exec \
    --python_filename=CaloML/Processing/test/NANO_Run4.py \
    --customise CaloML/Processing/SimTruthSequences_cff.SimTruthSequence_HGCAL,\
CaloML/Processing/SimTruthSequences_cff.SimTruthSequence_L1THGCAL,\
CaloML/Processing/HGCalTPG_cff.setupHGCalTPG,\
CaloML/SimTruth/GenParticles_cff.setupGenParticlesTables \
    --customise_commands="process.schedule.remove(process.nanoAOD_step)"
```


## 5. Plotting

I have written some plotting routines. They rely on my personal python backends, which are included as submodules (setup with `git submodule update --init --recursive`). There are a few useful scripts in `CaloML/plotting/scripts`

## 6. Technical details

The mechanics of the truth definition are detailed in slides [here](https://docs.google.com/presentation/d/1ELqLcqRZ1xdQrV5IbrIfoffT0ajOvjTFdIlm5xdPgv4/edit?usp=sharing). Validation studies are available [here](TO DO).