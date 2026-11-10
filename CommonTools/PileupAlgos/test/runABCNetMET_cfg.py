"""ABCNet (C++ producer) and PUPPI raw PF MET on MiniAOD, both computed the way
evaluation/cluster.py does: |sum of weight * pT| over all packedPFCandidates."""
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

opts = VarParsing('analysis')
opts.register('nThreads', 8, VarParsing.multiplicity.singleton, VarParsing.varType.int, '')
opts.parseArguments()

process = cms.Process('ABCMET')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 500
process.options.numberOfThreads = opts.nThreads
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(opts.maxEvents))
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))

from CommonTools.PileupAlgos.ABCNet_cff import abc
from CommonTools.PileupAlgos.Puppi_cff import puppi
from RecoMET.METProducers.pfMet_cfi import pfMet

process.abc = abc.clone()
# ValueMap of the puppiWeight() stored in MiniAOD, i.e. the PUPPI weight cluster.py uses
process.packedpuppi = puppi.clone(useExistingWeights=True,
                                  candName='packedPFCandidates',
                                  vertexName='offlineSlimmedPrimaryVertices')
process.pfMetABC = pfMet.clone(src='packedPFCandidates', applyWeight=True, srcWeights='abc')
process.pfMetPuppiRaw = pfMet.clone(src='packedPFCandidates', applyWeight=True, srcWeights='packedpuppi')

process.out = cms.OutputModule('PoolOutputModule',
    fileName=cms.untracked.string(opts.outputFile),
    outputCommands=cms.untracked.vstring('drop *', 'keep *_pfMetABC_*_*', 'keep *_pfMetPuppiRaw_*_*',
                                         'keep patMETs_slimmedMETs_*_*', 'keep patMETs_slimmedMETsPuppi_*_*'))
process.p = cms.Path(process.abc + process.packedpuppi + process.pfMetABC + process.pfMetPuppiRaw)
process.e = cms.EndPath(process.out)
