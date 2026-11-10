import FWCore.ParameterSet.Config as cms

#
# Run 3 dual-weight ABCNet, no PUPPI inputs, one-hot pdgId, domain-adapted (MDMM), trained on
# the normal pileup profile
# (Run3_ttbar_vbf_dualWeight_noPUPPI_onehot_SWD_GenJet_GenMET_ConeRegress_eta0to5_DomainAdv_SWDcalpt_normalPU_MDMM),
# frozen from the Keras SavedModel's serving signature with test/freeze_ABCNet_graph.py.
# The earlier models are kept in data/: ABCNet_Run3_dualWeight_noPUPPI_onehot.pb (nominal) and
# ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv.pb (domain-adapted); select one with graph_path.
#
# Products:
#   abc        combined weight (SWD * calibration). The one to cluster jets and
#              compute MET with; continuous, can exceed 1.
#   abc:swd    SWD weight, in [0, 1].
#
# When swapping in another model, keep these in step with it:
#
#   n_feats  must equal the number of input features the graph expects, i.e. the
#            length of "input_names" in preprocess_json. The output tensor's last
#            dimension is n_feats + 2 (the network passes the input features
#            through and appends the SWD and combined weights), or n_feats + 3 for
#            the domain-adapted models (an adversary score before those two); the
#            producer reads the last two columns and throws on any other width.
#   n_knns   must equal the second input tensor's last dimension (k = 15 here).
#   n_pf_cands is a truncation cap only (the training h5 kept the hardest 6000);
#            the graph takes a dynamic particle axis and the producer sends the
#            true multiplicity, with no zero padding.
#
abc = cms.EDProducer("ABCNetProducer",
                     candName = cms.InputTag("packedPFCandidates"),
                     graph_path = cms.FileInPath("CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv_normalPU_MDMM.pb"),
                     preprocess_json = cms.FileInPath("CommonTools/PileupAlgos/data/preprocessing_info_Run3_dualWeight_noPUPPI.json"),
                     input_tensor_name_1 = cms.string("input_1"),
                     input_tensor_name_2 = cms.string("input_2"),
                     output_tensor_name = cms.string("Identity"),
                     n_pf_cands = cms.int32(6000),
                     n_feats = cms.int32(23),
                     n_knns = cms.int32(15),
                     debug = cms.bool(False)
)
