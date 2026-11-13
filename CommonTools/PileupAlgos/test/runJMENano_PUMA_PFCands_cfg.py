# runJMENano_PUMA_cfg.py plus every PF candidate (PFCands table, as the training nano) with the two
# ABCNet weights per candidate:
#   PFCands_pumaWeight      combined weight (SWD * calibration), the one PUMAMET and the PUMA jets use
#   PFCands_pumaSWDWeight   SWD weight, in [0, 1]
# About 61 kB/event against 6-7 kB/event without the candidates (DY 2024 MC; a quarter of it the two weights).
#
#   cmsRun runJMENano_PUMA_PFCands_cfg.py inputFiles=<file:... or root://...> maxEvents=1000 out=nano.root \
#       [nThreads=4] [skip=0] [graph=CommonTools/PileupAlgos/data/<model>.pb]
import os
import sys

import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import ExtVar, Var
from PhysicsTools.NanoAOD.custom_btv_cff import addPFCands

sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/CommonTools/PileupAlgos/test"))
from runJMENano_PUMA_cfg import process

process = addPFCands(process, allPF=True)
# not in addPFCands' table
process.customConstituentsExtTable.variables.energy = Var("energy()", float, doc="energy", precision=10)
process.customConstituentsExtTable.variables.fromPV = Var("fromPV(0)", "uint8",
    doc="PV association of the candidate to the leading vertex: 0 NoPV, 1 PVLoose, 2 PVTight, 3 PVUsedInFit")
process.customConstituentsExtTable.variables.vtxIdx = Var("?vertexRef().isNonnull()?vertexRef().key():-1", "int16",
    doc="index of the associated vertex in offlineSlimmedPrimaryVertices (PV_ and OtherPV_ order)")
process.customConstituentsExtTable.externalVariables = cms.PSet(
    pumaWeight=ExtVar(cms.InputTag("abc"), float, doc="PUMA (ABCNet) combined weight (SWD * calibration)"),
    pumaSWDWeight=ExtVar(cms.InputTag("abc", "swd"), float, doc="PUMA (ABCNet) SWD weight"),
)
