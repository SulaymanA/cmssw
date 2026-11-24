# JME custom NanoAOD with PUMA (ABCNet) jets and MET, on 2024 MiniAOD, MC (default) or data (data=True).
#
# Adds to the standard JME nano: JetPUMA (AK4) and FatJetPUMA (AK8) clustered from the ABCNet-weighted PF
# candidates, and PUMAMET. The model is the default in python/ABCNet_cff.py (MDMM); graph= selects another.
# No PF candidates are stored: use runJMENano_PUMA_PFCands_cfg.py for those, with the per-candidate weights.
#
#   cmsRun runJMENano_PUMA_cfg.py inputFiles=<file:... or root://...> maxEvents=1000 out=nano.root \
#       [data=True] [nThreads=1] [skip=0] [graph=CommonTools/PileupAlgos/data/<model>.pb]
#
# In batch jobs set nThreads equal to the CPUs requested (request_cpus in Condor).
#
# Built on the cmsDriver configs (--step NANO:@JME --era Run3_2024)
#   MC:   runJMENano_ABC_cfg.py       --mc   --conditions auto:phase1_2024_realistic
#   data: runJMENano_ABC_data_cfg.py  --data --conditions 150X_dataRun3_v2 (the 2024 MINIv6 reprocessing,
#         e.g. /JetMET0/Run2024C-MINIv6NANOv15-v1/MINIAOD)
# For other campaigns regenerate these with the matching era and conditions; MiniAOD from before 14_2_X
# also needs the run3_nanoAOD_pre142X era modifier.
import os
import sys

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

opts = VarParsing("analysis")
opts.register("data", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "run on data")
opts.register("skip", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "events to skip")
opts.register("nThreads", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "threads (match request_cpus in batch jobs)")
# own output name: VarParsing's outputFile would get _numEvent<N> appended
opts.register("out", "nano.root", VarParsing.multiplicity.singleton, VarParsing.varType.string, "output file")
opts.register("graph", "", VarParsing.multiplicity.singleton, VarParsing.varType.string,
              "ABCNet graph (FileInPath); default: the one in ABCNet_cff.py")
opts.parseArguments()

sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/CommonTools/PileupAlgos/test"))
if opts.data:
    from runJMENano_ABC_data_cfg import process
    output = process.NANOAODoutput
else:
    from runJMENano_ABC_cfg import process
    output = process.NANOAODSIMoutput

process.source.fileNames = opts.inputFiles
process.source.skipEvents = cms.untracked.uint32(opts.skip)
process.maxEvents.input = opts.maxEvents
process.options.numberOfThreads = opts.nThreads
output.fileName = "file:" + opts.out
if opts.graph:
    process.abc.graph_path = cms.FileInPath(opts.graph)
