# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: jmeNano --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --step NANO:@JME --conditions auto:phase1_2024_realistic --era Run3_2024 --nThreads 8 -n 6000 --filein root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/50cc2328-b8cb-4f46-b1eb-6b0c20cc791c.root,root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/65d70b74-9290-48d4-851d-0e30ab83ab84.root,root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/99593e77-5aec-4587-9429-f6f122584b43.root,root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/8170391e-946d-4d12-9ea7-fb67c15d7d00.root --fileout file:jmeNano_QCDFlatPU_2024.root --python_filename runJMENano_ABC_QCDFlatPU_cfg.py --no_exec
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_2024_cff import Run3_2024

process = cms.Process('NANO',Run3_2024)

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
        'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/50cc2328-b8cb-4f46-b1eb-6b0c20cc791c.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/65d70b74-9290-48d4-851d-0e30ab83ab84.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/99593e77-5aec-4587-9429-f6f122584b43.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to120_150X_mcRun3_2024_realistic_v2-v2/2810000/8170391e-946d-4d12-9ea7-fb67c15d7d00.root'
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
    fileName = cms.untracked.string('file:jmeNano_QCDFlatPU_2024.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2024_realistic', '')

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

process.source.delayReadingEventProducts = cms.untracked.bool(False)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
