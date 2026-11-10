#!/bin/bash
# JME custom NanoAOD with the domain-adapted ABCNet (PUMA) model on the three comparison samples:
# 2024 ttbar (TTto2L2Nu, nominal PU), 2022 flat-PU ttbar (TTToSemiLeptonic, FlatPU0to70) and
# Winter24 VBF H->inv. Same configs as the nominal-model runs, with the graph swapped via
# --customise_commands; the default in ABCNet_cff.py is left untouched.
#
#   cd $CMSSW_BASE/src/CommonTools/PileupAlgos/test && cmsenv
#   export X509_USER_PROXY=<your proxy>
#   ./runJMENano_DomainAdv.sh [nEvents, default 6000] [sample names, default all three]
#   e.g. ./runJMENano_DomainAdv.sh 6000 TTFlatPU_Winter22 VBFHInv_Winter24
set -e
NEV=${1:-6000}
ONLY="${*:2}"
GRAPH='process.abc.graph_path = cms.FileInPath("CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv.pb")'
# 12_2_X MiniAOD lacks the tau IDs this nano expects; taus are not needed here (flat-PU ttbar only)
NOTAUS='process.finalBoostedTaus.cut = "pt < 0"; process.finalTaus.cut = "pt < 0"'
COMMON="--mc --eventcontent NANOAODSIM --datatier NANOAODSIM --step NANO:@JME --nThreads 8 -n ${NEV} --no_exec"

# name | file list | era | conditions | extra customise commands
run() {
  local name=$1 files=$2 era=$3 cond=$4 extra=$5
  if [ -n "${ONLY}" ] && [[ " ${ONLY} " != *" ${name} "* ]]; then return; fi
  cmsDriver.py jmeNano ${COMMON} --era "${era}" --conditions "${cond}" \
    --filein "$(paste -sd, "${files}")" --fileout "file:jmeNano_DA_${name}.root" \
    --python_filename "runJMENano_ABCDA_${name}_cfg.py" \
    --customise_commands "${GRAPH}${extra:+; ${extra}}"
  cmsRun "runJMENano_ABCDA_${name}_cfg.py" > "jmeNano_DA_${name}.log" 2>&1
  echo "${name}: done, $(grep -ci exception "jmeNano_DA_${name}.log" || true) exception lines"
}

run TTto2L2Nu_2024     runABCNetMET_files_TTto2L2Nu_2024.txt   Run3_2024                      auto:phase1_2024_realistic
run TTFlatPU_Winter22  runJMENano_files_TTFlatPU_Winter22.txt  Run3,run3_nanoAOD_pre142X      auto:phase1_2022_realistic "${NOTAUS}"
run VBFHInv_Winter24   runJMENano_files_VBFHInv_Winter24.txt   Run3_2024,run3_nanoAOD_pre142X auto:phase1_2024_realistic
