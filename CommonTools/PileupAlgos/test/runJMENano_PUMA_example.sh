#!/bin/bash
# Example: JME custom NanoAOD with PUMA (ABCNet) jets and MET on 2024 MC MiniAOD.
#
#   cmsenv
#   bash $CMSSW_BASE/src/CommonTools/PileupAlgos/test/runJMENano_PUMA_example.sh [input file] [max events]
#
# Configs (in this directory):
#   runJMENano_PUMA_cfg.py          JME nano + JetPUMA (AK4), FatJetPUMA (AK8), PUMAMET; no PF candidates
#   runJMENano_PUMA_PFCands_cfg.py  the same + every PF candidate with its ABCNet weights
#                                   (PFCands_pumaWeight = combined, PFCands_pumaSWDWeight = SWD)
# Options of both: inputFiles, maxEvents, out, data (default False: MC), nThreads (default 1; in batch jobs
# set it equal to request_cpus), skip (events to skip),
# graph (ABCNet model, a FileInPath; default: the MDMM model set in python/ABCNet_cff.py).
# Both are for 2024 (era Run3_2024): MC with auto:phase1_2024_realistic, data (data=True) with
# 150X_dataRun3_v2, the 2024 MINIv6 reprocessing; see runJMENano_ABC_cfg.py for other campaigns.
#
# Remote files need a grid proxy (voms-proxy-init -voms cms) and, on nodes without
# /etc/grid-security/certificates, X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates.
set -e
INPUT=${1:-root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/150X_mcRun3_2024_realistic_v2-v3/100001/67db66dc-58f6-470a-92f8-5915390f1043.root}
NEVENTS=${2:-100}
TEST=${CMSSW_BASE:?run cmsenv first}/src/CommonTools/PileupAlgos/test

# JME nano with PUMA jets and MET (about 6-7 kB/event)
cmsRun ${TEST}/runJMENano_PUMA_cfg.py inputFiles=${INPUT} maxEvents=${NEVENTS} out=nano_PUMA.root

# ... with all PF candidates and their ABCNet weights (about 60 kB/event)
cmsRun ${TEST}/runJMENano_PUMA_PFCands_cfg.py inputFiles=${INPUT} maxEvents=${NEVENTS} out=nano_PUMA_PFCands.root

# Data: the same configs with data=True, e.g.
#   cmsRun ${TEST}/runJMENano_PUMA_cfg.py data=True maxEvents=${NEVENTS} out=nano_PUMA_data.root \
#       inputFiles=root://cms-xrd-global.cern.ch//store/data/Run2024C/JetMET0/MINIAOD/MINIv6NANOv15-v1/2530000/9f96b5b2-e380-4f80-a1ef-294b34cf135f.root

# Another ABCNet model, e.g. the nominal (not domain-adapted) one:
#   cmsRun ${TEST}/runJMENano_PUMA_cfg.py inputFiles=${INPUT} maxEvents=${NEVENTS} out=nano_PUMA_nominal.root \
#       graph=CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot.pb
