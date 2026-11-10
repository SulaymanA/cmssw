# Timing run: the domain-adapted ttbar JME nano config on fewer events, with the end-of-job
# TimeReport (wantSummary) and the Timing service, to get the ABCNetProducer ("abc") time per
# event next to the rest of the job.
#
#   cmsRun runJMENano_ABCDA_timing_cfg.py [maxEvents=1000] [nThreads=8]
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from runJMENano_ABCDA_TTto2L2Nu_2024_cfg import process

opts = VarParsing("analysis")
opts.register("nThreads", 8, VarParsing.multiplicity.singleton, VarParsing.varType.int, "")
opts.setDefault("maxEvents", 1000)
opts.parseArguments()

process.maxEvents.input = opts.maxEvents
process.options.numberOfThreads = opts.nThreads
process.options.wantSummary = True
process.Timing = cms.Service("Timing", summaryOnly=cms.untracked.bool(True))
process.NANOAODSIMoutput.fileName = "file:jmeNano_DA_timing.root"
