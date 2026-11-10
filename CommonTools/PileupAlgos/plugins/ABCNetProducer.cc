//========================================================================================
// Class:      ABCNetProducer                     ---------------------------------------
//----------------------------------------------------------------------------------------
/**\class ABCNetProducer ABCNetProducer.cc PileupAlgos/plugins/ABCNetProducer.cc
------------------------------------------------------------------------------------------
 Description: This class produces ABCNet weights to be used to mitigate pileup  ---
 -----------------------------------------------------------------------------------------
 Implementation:                                                                       ---
     This EDProducer is meant to be used with CMSSW >= 10_6_26                         ---
*/
//========================================================================================
// Authors:  Fabio Iemmi (IHEP)                                      ---------------------
//         Created:  MON, 23 May 2022 10:00:28 GMT  ---------------------------------------
//========================================================================================

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h" // for edm::ParameterSet
#include "DataFormats/PatCandidates/interface/PackedCandidate.h" //for pat
#include "DataFormats/Candidate/interface/Candidate.h" // for reco
#include "CommonTools/PileupAlgos/interface/PuppiCandidate.h"// for puppi candidates
#include "DataFormats/Math/interface/LorentzVector.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "PhysicsTools/TensorFlow/interface/TensorFlow.h" // to use TensorFlow
#include "FWCore/Framework/interface/stream/EDAnalyzer.h"

#include "ABCNetProducer.h"
#include "ABCNetMakeInputs.h"

#include <limits>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <memory>
#include <nlohmann/json.hpp>

using namespace abcnet;

//////////////////////////////////////////////////////////////////////////////////
// Defining methods --------------------------------------------------------------
//////////////////////////////////////////////////////////////////////////////////

// constructors
ABCNetProducer::ABCNetProducer(const edm::ParameterSet& iConfig, const ABCNetTFCache* cache):
  tokenPFCandidates_(consumes<reco::CandidateView>(iConfig.getParameter<edm::InputTag>("candName"))),
  session_(nullptr),
  input_tensor_name_1(iConfig.getParameter<std::string>("input_tensor_name_1")),
  input_tensor_name_2(iConfig.getParameter<std::string>("input_tensor_name_2")),
  output_tensor_name_(iConfig.getParameter<std::string>("output_tensor_name")),
  n_pf_cands_(iConfig.getParameter<int>("n_pf_cands")),
  n_feats_(iConfig.getParameter<int>("n_feats")),
  n_knns_(iConfig.getParameter<int>("n_knns")),
  debug_(iConfig.getParameter<bool>("debug"))
{
  //parse data from preprocessing JSON file
  std::ifstream ifs(iConfig.getParameter<edm::FileInPath>("preprocess_json").fullPath());
  nlohmann::json js = nlohmann::json::parse(ifs);
  js.at("input_names").get_to(input_names_); //store names of input features from JSON inside input_names_
  const auto &var_info_pset = js.at("var_info"); //get the var_info block from JSON
  
  for (const auto & input_name : input_names_) {
    const auto &var_pset = var_info_pset.at(input_name);
    double upper_bound = var_pset.at("upper_bound");
    double lower_bound = var_pset.at("lower_bound");
    double norm_factor = var_pset.at("norm_factor");
    double replace_nan_value = var_pset.at("replace_nan_value");
    double pad_value = var_pset.at("pad_value");
    auto &prep_params = prep_info_map_[input_name];
    prep_params.var_info_map[input_name] = PreprocessParams::VarInfo(upper_bound,
								     lower_bound,
								     norm_factor,
								     replace_nan_value,
								     pad_value
								     );
  }
  
  //create the TF session using the meta graph from the cache
  session_ = tensorflow::createSession(cache->graphDef);

  // Produce ValueMaps of floats linking each PF candidate with its ABCNet weights.
  // The dual-weight model outputs two: the SWD weight and the combined weight
  // (SWD * calibration). The combined one is the weight to cluster with and goes
  // into the default (unlabelled) product, so consumers of "abc" use it unchanged.
  ABCNetOut_ = produces<edm::ValueMap<float>> ();
  ABCNetSWDOut_ = produces<edm::ValueMap<float>> ("swd");

};

// destructor
ABCNetProducer::~ABCNetProducer() {
};

void ABCNetProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("candName", edm::InputTag("packedPFCandidates"));
  desc.add<edm::FileInPath>("graph_path", edm::FileInPath("CommonTools/PileupAlgos/data/ABCNet_Run3_dualWeight_noPUPPI_onehot_DomainAdv_normalPU_MDMM.pb"));
  desc.add<edm::FileInPath>("preprocess_json", edm::FileInPath("CommonTools/PileupAlgos/data/preprocessing_info_Run3_dualWeight_noPUPPI.json"));
  desc.add<std::string>("input_tensor_name_1", "input_1");
  desc.add<std::string>("input_tensor_name_2", "input_2");
  desc.add<std::string>("output_tensor_name", "Identity");
  desc.add<int>("n_pf_cands", 6000);
  desc.add<int>("n_feats", 23);
  desc.add<int>("n_knns", 15);
  desc.add<bool>("debug", false);

  descriptions.add("abc", desc);
};

std::unique_ptr<ABCNetTFCache> ABCNetProducer::initializeGlobalCache(const edm::ParameterSet& iConfig) {
  // tensorflow::setLogging() was dropped from PhysicsTools/TensorFlow; TF verbosity
  // is now controlled through the TF_CPP_MIN_LOG_LEVEL environment variable.
  // get the pb file
  std::string pbFile = iConfig.getParameter<edm::FileInPath>("graph_path").fullPath();
  // load the graph definition and save it in the cache
  ABCNetTFCache* cache = new ABCNetTFCache();
  cache->graphDef = tensorflow::loadGraphDef(pbFile);
  return std::unique_ptr<ABCNetTFCache>(cache);
};

void ABCNetProducer::globalEndJob(const ABCNetTFCache* cache) {
  if (cache->graphDef != nullptr) {
    delete cache->graphDef;
  }
};

std::vector<float> ABCNetProducer::minmax_scale(const std::vector<float> &input,
						float upper_bound,
						float lower_bound,
						float norm_factor,
						float pad_value,
						float replace_nan_value
						) {
  std::vector<float> out(input.size(), pad_value);
  for (unsigned i = 0; i < input.size(); ++i) {
    //NaN carries no sign to preserve, so it is substituted outright.
    //Infinities are deliberately NOT substituted: they keep their sign and
    //saturate at upper_bound/lower_bound in the clamp below, which after the
    //division by norm_factor puts a normalised variable at exactly +/-1.
    auto val = std::isnan(input[i]) ? replace_nan_value : input[i];
    //second of all, perform the actual min-max scaling
    val = (val>upper_bound) ? upper_bound : val;
    val = (val<lower_bound) ? lower_bound : val;
    out[i] = val/norm_factor;
  }
  return out;
};

void ABCNetProducer::preprocess(std::unordered_map<std::string, std::vector<float>> & featureMap, bool debug) {

  for (const auto & input_name : input_names_) {
    const auto & preprocessing_params = prep_info_map_[input_name].var_info_map[input_name];
    featureMap[input_name] = minmax_scale(featureMap[input_name],
					  preprocessing_params.upper_bound,
					  preprocessing_params.lower_bound,
					  preprocessing_params.norm_factor,
					  preprocessing_params.pad_value,
					  preprocessing_params.replace_nan_value
					  );
  }
  
  if(debug) {
    std::cout << "*** NOW CHECKING THE SANITY OF THE PREPROCESSING STEP ***" << std::endl;
    //Only features that were actually normalised (norm_factor != 1) are expected
    //to land inside [-1;1]; the pass-through ones are not. Deciding that from the
    //JSON rather than from a hardcoded list of names keeps this in step with the
    //feature set automatically -- the previous hardcoded list went stale as soon
    //as the input variables changed.
    for (const auto & input_name : input_names_) {
      bool issue = false;
      std::cout << input_name << std::endl;
      const auto & pp = prep_info_map_[input_name].var_info_map[input_name];
      if (pp.norm_factor == 1) {
	std::cout << "Not normalised (norm_factor = 1), so values outside [-1;1] are expected. Skipping..." << std::endl;
	continue;
      }
      for (auto const & element : featureMap[input_name]) {
	if (element < -1 || element > 1) {
	  std::cout << "*** WARNING *** Found element with value outside [-1;1] interval" << std::endl;
	  issue = true;
	  break;
	}
      }
      if (!issue) std::cout << "No issues with input feature detected" << std::endl;
    }
  }
  
};

void ABCNetProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  // Get PFCandidate Collection
  edm::Handle<reco::CandidateView> PFCandidates;
  iEvent.getByToken(tokenPFCandidates_, PFCandidates);
  const reco::CandidateView *pfCol = PFCandidates.product();
  
  //make feature map and KNNs, preprocess features
  std::vector<size_t> indices; 
  auto [features, KNNs] = ABCNetMakeInputs::makeFeatureMap(pfCol, indices, n_pf_cands_, n_knns_, debug_);
  ABCNetProducer::preprocess(features, debug_);
  
  //number of candidates actually being evaluated. The graph takes a dynamic
  //particle axis, so this is the true multiplicity (capped at n_pf_cands_ by
  //makeFeatureMap), NOT n_pf_cands_ itself. Every loop below must be bounded by
  //it rather than by n_pf_cands_.
  const int nParticles = (int)features["PFCandEta"].size();

  //fill the input tensors
  tensorflow::Tensor inputs (tensorflow::DT_FLOAT, { 1, nParticles, n_feats_ });
  inputs.flat<float>().setZero();
  for (int j = 0; j < n_feats_; j++) {
    for (int i = 0; i < nParticles; i++) {
      inputs.tensor<float,3>()(0,i,j) = float(features[input_names_.at(j)].at(i)); //looks suboptimal; is there way of filling the tensor avoiding nested loops?
    }
  }
  tensorflow::Tensor knn_indices (tensorflow::DT_FLOAT, { 1, nParticles, n_knns_ });
  knn_indices.flat<float>().setZero();
  for (int i = 0; i < nParticles; i++) {
    for (int j = 0; j < n_knns_; j++){
      knn_indices.tensor<float,3>()(0,i,j) = float(KNNs.at(i*n_knns_+j));
    }
  }
  if (debug_) {
    std::cout << "PRINTING NETWORK INPUTS" << std::endl;
    for (int i = 0; i < std::min(3, nParticles); i++) {
      std::cout << "Features: \n";
    for (int j = 0; j < n_feats_; j++) {
      std::cout << inputs.tensor<float,3>()(0, i, j) << ", ";
    }
    std::cout << "\n";
    std::cout << "KNN indices: \n";
    for (int j = 0; j < n_knns_; j++) {
      std::cout << knn_indices.tensor<float,3>()(0, i, j) << ", ";
    }
    std::cout << "\n";
    }
  }
  std::vector<tensorflow::Tensor> outputs;
  tensorflow::run(session_, { { input_tensor_name_1, inputs }, { input_tensor_name_2, knn_indices } }, { output_tensor_name_ }, &outputs);
  //The output starts with the n_feats_ input features passed through and always ends
  //with the SWD weight and the combined weight, SWD * calibration, in its last two
  //columns (the same convention cluster.py uses: [-2] and [-1]). Domain-adversarial
  //models put one extra column, the adversary score, in between, so the last
  //dimension is n_feats_ + 2 or n_feats_ + 3. Check it so a mismatched n_feats_ fails
  //loudly instead of silently reading a passed-through feature as a weight.
  const auto out = outputs.at(0).tensor<float,3>();
  const int n_out = outputs.at(0).dim_size(2);
  if (n_out != n_feats_ + 2 && n_out != n_feats_ + 3) {
    throw edm::Exception(edm::errors::Configuration, "ABCNetProducer: ")
      << "output tensor has last dimension " << n_out << ", expected n_feats + 2 = " << n_feats_ + 2
      << " (dual-weight model) or n_feats + 3 = " << n_feats_ + 3 << " (with a domain-adversary score)";
  }
  const int swd_col = n_out - 2;
  const int combined_col = n_out - 1;
  if (debug_) {
    std::cout << "PRINTING NETWORK OUTPUTS (swd, combined)" << std::endl;
    for (int i = 0; i < nParticles; i++) std::cout << "(" << out(0, i, swd_col) << ", " << out(0, i, combined_col) << ") ";
    std::cout << std::endl;
  }

  //initialize containers for ABCNet weights and fill them. No threshold is applied:
  //the combined weight is continuous and can exceed 1 by design.
  std::vector<float> weights;
  std::vector<float> swd_weights;

  int PFCounter = 0;
  for(auto const& aPF : *pfCol) {
    const pat::PackedCandidate *lPack = dynamic_cast<const pat::PackedCandidate*>(&aPF);
    float abcweight = -1.;
    float swdweight = -1.;
    if(lPack == nullptr) {
      // throw error
      throw edm::Exception(edm::errors::LogicError,"ABCNetProducer: cannot get weights since inputs are not PackedCandidates");
    }
    else{
      if (indices.at(PFCounter) >= (unsigned)n_pf_cands_) { //if the particle wasn't considered in evaluation, assign 0 weight
	abcweight = 0.0;
	swdweight = 0.0;
      }
      else {
	abcweight = out(0, indices.at(PFCounter), combined_col);
	swdweight = out(0, indices.at(PFCounter), swd_col);
      }
    }
    weights.push_back(abcweight);
    swd_weights.push_back(swdweight);
    PFCounter++;
  }

  edm::ValueMap<float> ABCNetOut;
  edm::ValueMap<float>::Filler ABCNetFiller(ABCNetOut);
  ABCNetFiller.insert(PFCandidates,weights.begin(),weights.end());
  ABCNetFiller.fill();
  iEvent.emplace(ABCNetOut_, ABCNetOut);

  edm::ValueMap<float> ABCNetSWDOut;
  edm::ValueMap<float>::Filler ABCNetSWDFiller(ABCNetSWDOut);
  ABCNetSWDFiller.insert(PFCandidates,swd_weights.begin(),swd_weights.end());
  ABCNetSWDFiller.fill();
  iEvent.emplace(ABCNetSWDOut_, ABCNetSWDOut);

}
//define this as a plug-in
DEFINE_FWK_MODULE(ABCNetProducer);
