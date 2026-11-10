import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

opts = VarParsing('analysis')
opts.setDefault('maxEvents', 5)
opts.setDefault('inputFiles', 'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/150X_mcRun3_2024_realistic_v2-v3/100001/67db66dc-58f6-470a-92f8-5915390f1043.root')
opts.register('debug', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, '')
opts.register('graph', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, '')
opts.parseArguments()

process = cms.Process('ABCTEST')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(opts.maxEvents))
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))

from CommonTools.PileupAlgos.ABCNet_cff import abc
process.abc = abc.clone(debug=opts.debug)
if opts.graph:
    process.abc.graph_path = cms.FileInPath(opts.graph)

process.out = cms.OutputModule('PoolOutputModule',
    fileName=cms.untracked.string(opts.outputFile),
    outputCommands=cms.untracked.vstring('drop *', 'keep *_abc_*_*', 'keep *_packedPFCandidates_*_*', 'keep *_offlineSlimmedPrimaryVertices_*_*'))
process.p = cms.Path(process.abc)
process.e = cms.EndPath(process.out)
