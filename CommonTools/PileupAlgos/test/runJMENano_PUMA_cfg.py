# JME custom NanoAOD with PUMA (ABCNet) jets and MET, on 2024 MC MiniAOD.
#
# Adds to the standard JME nano: JetABC (AK4) and FatJetABC (AK8) clustered from the ABCNet-weighted PF
# candidates, and ABCMET. The model is the default in python/ABCNet_cff.py (MDMM); graph= selects another.
# No PF candidates are stored: use runJMENano_PUMA_PFCands_cfg.py for those, with the per-candidate weights.
#
#   cmsRun runJMENano_PUMA_cfg.py inputFiles=<file:... or root://...> maxEvents=1000 out=nano.root \
#       [nThreads=4] [skip=0] [graph=CommonTools/PileupAlgos/data/<model>.pb]
#
# Built on runJMENano_ABC_cfg.py (cmsDriver: --step NANO:@JME --era Run3_2024
# --conditions auto:phase1_2024_realistic --mc). For other campaigns regenerate that with the matching era
# and conditions; MiniAOD from before 14_2_X also needs the run3_nanoAOD_pre142X era modifier.
import os
import sys

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/CommonTools/PileupAlgos/test"))
from runJMENano_ABC_cfg import process

opts = VarParsing("analysis")
opts.register("skip", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "events to skip")
opts.register("nThreads", 4, VarParsing.multiplicity.singleton, VarParsing.varType.int, "threads")
# own output name: VarParsing's outputFile would get _numEvent<N> appended
opts.register("out", "nano.root", VarParsing.multiplicity.singleton, VarParsing.varType.string, "output file")
opts.register("graph", "", VarParsing.multiplicity.singleton, VarParsing.varType.string,
              "ABCNet graph (FileInPath); default: the one in ABCNet_cff.py")
opts.parseArguments()

process.source.fileNames = opts.inputFiles
process.source.skipEvents = cms.untracked.uint32(opts.skip)
process.maxEvents.input = opts.maxEvents
process.options.numberOfThreads = opts.nThreads
process.NANOAODSIMoutput.fileName = "file:" + opts.out
if opts.graph:
    process.abc.graph_path = cms.FileInPath(opts.graph)
