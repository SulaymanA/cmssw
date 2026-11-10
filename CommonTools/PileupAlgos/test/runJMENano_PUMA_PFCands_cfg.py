# runJMENano_PUMA_cfg.py plus every PF candidate (PFCands table, as the training nano) with the two
# ABCNet weights per candidate:
#   PFCands_abcWeight      combined weight (SWD * calibration), the one ABCMET and the PUMA jets use
#   PFCands_abcSWDWeight   SWD weight, in [0, 1]
# About 61 kB/event against 6-7 kB/event without the candidates (DY 2024 MC; a quarter of it the two weights).
#
#   cmsRun runJMENano_PUMA_PFCands_cfg.py inputFiles=<file:... or root://...> maxEvents=1000 out=nano.root \
#       [nThreads=4] [skip=0] [graph=CommonTools/PileupAlgos/data/<model>.pb]
import os
import sys

import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import ExtVar
from PhysicsTools.NanoAOD.custom_btv_cff import addPFCands

sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/CommonTools/PileupAlgos/test"))
from runJMENano_PUMA_cfg import process

process = addPFCands(process, allPF=True)
process.customConstituentsExtTable.externalVariables = cms.PSet(
    abcWeight=ExtVar(cms.InputTag("abc"), float, doc="ABCNet combined weight (SWD * calibration)"),
    abcSWDWeight=ExtVar(cms.InputTag("abc", "swd"), float, doc="ABCNet SWD weight"),
)
