# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: jmeNano --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --step NANO:@JME --nThreads 8 -n 6000 --no_exec --era Run3,run3_nanoAOD_pre142X --conditions auto:phase1_2022_realistic --filein root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/3967752b-7b07-47a3-b390-9202848c98ba.root,root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/a61d4b3f-64b2-4579-8cb7-fb6d975dc18b.root,root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/2bd961ad-dcbb-46eb-a3dd-3e1349cfc595.root,root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/2718f9e4-761f-42e2-af01-dcce3a5aab2b.root --fileout file:jmeNano_DA_TTFlatPU_Winter22.root --python_filename runJMENano_ABCDA_TTFlatPU_Winter22_cfg.py --customise_commands 'process.abc.graph_path = cms.FileInPath("CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv.pb"); process.finalBoostedTaus.cut = "pt < 0"; process.finalTaus.cut = "pt < 0"'
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_cff import Run3
from Configuration.Eras.Modifier_run3_nanoAOD_pre142X_cff import run3_nanoAOD_pre142X

process = cms.Process('NANO',Run3,run3_nanoAOD_pre142X)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(6000),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/3967752b-7b07-47a3-b390-9202848c98ba.root',
        'root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/a61d4b3f-64b2-4579-8cb7-fb6d975dc18b.root',
        'root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/2bd961ad-dcbb-46eb-a3dd-3e1349cfc595.root',
        'root://cms-xrd-global.cern.ch//store/mc/Run3Winter22MiniAOD/TTToSemiLeptonic_TuneCP5_13p6TeV-powheg-pythia8/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/70000/2718f9e4-761f-42e2-af01-dcce3a5aab2b.root'
    ),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('jmeNano nevts:6000'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:jmeNano_DA_TTFlatPU_Winter22.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2022_realistic', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads = 8
process.options.numberOfStreams = 0

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.custom_jme_cff
from PhysicsTools.NanoAOD.custom_jme_cff import PrepJMECustomNanoAOD 

#call to customisation function PrepJMECustomNanoAOD imported from PhysicsTools.NanoAOD.custom_jme_cff
process = PrepJMECustomNanoAOD(process)

# End of customisation functions


# Customisation from command line

process.abc.graph_path = cms.FileInPath("CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv.pb"); process.finalBoostedTaus.cut = "pt < 0"; process.finalTaus.cut = "pt < 0"
process.source.delayReadingEventProducts = cms.untracked.bool(False)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
