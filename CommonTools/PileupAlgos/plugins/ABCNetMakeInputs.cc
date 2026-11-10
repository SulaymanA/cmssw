#include <iostream>
#include <memory>
#include <cmath>
#include <limits>
#include <numeric>

#include "DataFormats/PatCandidates/interface/PackedCandidate.h" //for pat
#include "DataFormats/Candidate/interface/Candidate.h" // for reco

#include "PhysicsTools/NearestNeighbors/interface/NearestNeighbors.h"

#include "ABCNetMakeInputs.h"

using namespace abcnet;
using PointCloud = cms::nanoflann::PointCloud<float, 2>; //default value for the DIM parameter is 3, but want to gather using 2 dims only (eta, phi). See template definition L11 of PhysicsTools/NearestNeighbors/interface/NearestNeighbors.h

template <typename A, typename B> void zip(const std::vector<A> &a, const std::vector<B> &b, std::vector<std::pair<A,B>> &zipped) {
  for(size_t i=0; i<a.size(); ++i) {
    zipped.push_back(std::make_pair(a[i], b[i]));
  }
}

template <typename A, typename B> void unzip( const std::vector<std::pair<A, B>> &zipped, std::vector<A> &a, std::vector<B> &b) {
  for(size_t i=0; i<a.size(); i++) {
    a[i] = zipped[i].first;
    b[i] = zipped[i].second;
  }
}

template <typename A> std::vector<size_t> get_indices(std::vector<A> & v) {
  //initialize original index locations
  std::vector<size_t> idx(v.size());
  iota(idx.begin(), idx.end(), 0);
  //first, get indices mapping sorted to unsorted elements
  stable_sort(idx.begin(), idx.end(), [&v](size_t i1, size_t i2) {return v[i1] > v[i2];});
  //then, invert the mapping to get unsorted ---> sorted mapping
  std::vector<size_t> idx_inverse(idx.size());
  for (size_t i = 0; i < idx.size(); ++i) idx_inverse[idx[i]] = i;
  
  return idx_inverse;
}

std::tuple< std::unordered_map<std::string, std::vector<float>>, std::vector<float> > ABCNetMakeInputs::makeFeatureMap (const reco::CandidateView * pfCol, std::vector<size_t> & indices, int n_pf_cands, int n_knns, bool debug) {
  
  //store PF candidates and their pts into vectors
  std::vector<pat::PackedCandidate> PFCands;
  std::vector<float> Pts;
  
  for (auto const & aPF : *pfCol ) {
    const pat::PackedCandidate *lPack = dynamic_cast<const pat::PackedCandidate*>(&aPF);    
    PFCands.push_back(*lPack);
    Pts.push_back(lPack->pt());
  } // end loop over PF candidates
  
  //get indices mapping unsorted and sorted PF candidates
  indices = get_indices(Pts);
  
  //sort PF candidates based on their Pt
  //zip the vectors
  std::vector<std::pair<pat::PackedCandidate,float>> zipped_vec;
  zip(PFCands, Pts, zipped_vec);
  // Sort the vector of pairs
  std::stable_sort(std::begin(zipped_vec), std::end(zipped_vec), [&](const auto& a, const auto& b) { return a.second > b.second; });
  // Write the sorted pairs back to the original vectors
  unzip(zipped_vec, PFCands, Pts);

  //fill feature map
  //
  //The keys below must match "input_names" in the preprocessing JSON exactly, and
  //their ORDER there is what defines the column order of the network's input
  //tensor (see ABCNetProducer::produce, which fills column j from
  //input_names_.at(j)). The Run 3 dual-weight (no PUPPI, one-hot pdgId) ordering
  //is --input_feats 0 1 2 3 16 6 7 8 9 10 11 12 13 14 18 20 21 24 25 26 27 28 29;
  //the j-numbers in the comments are the tensor columns, the (c) numbers the
  //columns of the training h5 (see the table at the top of clean_nano.py).
  //
  //The raw values mirror the NanoAOD PFCands table the training h5 files were
  //made from (addPFCands in PhysicsTools/NanoAOD/python/custom_btv_cff.py, read by
  //batch.py), including its sentinels for candidates without track details. The
  //transformations then mirror clean_nano.py: the log and -1 substitution are
  //done here, the clamp and division by preprocess_json in the producer.
  std::unordered_map<std::string, std::vector<float>> fts;
  PointCloud::Points points;

  //clean_nano.py sets +inf to 0 before any transformation
  auto noInf = [](double x) { return x == std::numeric_limits<double>::infinity() ? 0. : x; };
  //log with a floor at 1, matching log_scale() in clean_nano.py: non-positive
  //inputs (including the -1 sentinel) are replaced by 1 before the log, so they
  //map to 0 rather than -inf.
  auto logFloored = [&](double x) { x = noInf(x); return float(std::log(x > 0. ? x : 1.)); };
  //clamp_scale() in clean_nano.py replaces every -1 by `replace` before clamping
  auto subSentinel = [&](double x, double replace) { x = noInf(x); return float(x == -1. ? replace : x); };

  int nStored = 0;
  for (auto const & aPF : PFCands) {

    points.push_back({{float(aPF.eta()), float(aPF.phi())}});

    //PFCands table: ?hasTrackDetails()?<track quantity>:<sentinel>
    const bool hasTrk = aPF.hasTrackDetails();
    const reco::Track *trk = hasTrk ? &aPF.pseudoTrack() : nullptr;

    //--- kinematics ---------------------------------------------------------
    fts["PFCandLogPt"].push_back(logFloored(aPF.pt()));                                   //j0  (c0)
    fts["PFCandEta"].push_back(noInf(aPF.eta()));                                         //j1  (c1)
    fts["PFCandPhi"].push_back(noInf(aPF.phi()));                                         //j2  (c2)
    fts["PFCandMass"].push_back(noInf(aPF.mass()));                                       //j3  (c3)
    fts["PFCandCharge"].push_back(aPF.charge());                                          //j4  (c16)
    //--- track (sentinel -1 without track details) --------------------------
    fts["PFCandD0"].push_back(subSentinel(hasTrk ? aPF.dxy() : -1., 0.));                 //j5  (c6)
    fts["PFCandLogD0Err"].push_back(logFloored(hasTrk ? aPF.dxyError() : -1.));           //j6  (c7)
    fts["PFCandDz"].push_back(subSentinel(hasTrk ? aPF.dz() : -1., 0.));                  //j7  (c8)
    fts["PFCandLogDzErr"].push_back(logFloored(hasTrk ? aPF.dzError() : -1.));            //j8  (c9)
    fts["PFCandLogTrkPt"].push_back(logFloored(hasTrk ? trk->pt() : -1.));                //j9  (c10)
    fts["PFCandTrkEta"].push_back(noInf(hasTrk ? trk->eta() : -1.));                      //j10 (c11)
    fts["PFCandTrkPhi"].push_back(noInf(hasTrk ? trk->phi() : -1.));                      //j11 (c12)
    fts["PFCandLogTrkP"].push_back(logFloored(hasTrk ? trk->p() : -1.));                  //j12 (c13)
    fts["PFCandTrkChi2"].push_back(subSentinel(hasTrk ? trk->normalizedChi2() : -1., 100.)); //j13 (c14)
    //--- vertex association and hits ---------------------------------------
    fts["PFCandPvAssocQuality"].push_back(aPF.pvAssociationQuality());                    //j14 (c18)
    fts["PFCandTrkHighPurity"].push_back(hasTrk ? trk->quality(reco::TrackBase::highPurity) : 0); //j15 (c20)
    fts["PFCandLostInnerHits"].push_back(aPF.lostInnerHits());                            //j16 (c21)
    fts["PFCandTrkQuality"].push_back(hasTrk ? trk->qualityMask() : 0);                   //j17 (c24)
    //--- one-hot particle type, from one_hot_encode_pdgid() in clean_nano.py --
    //charged hadrons, HF hadronic (1) and HF EM (2) share the hadron category
    const int absId = std::abs(aPF.pdgId());
    fts["PFCandIsHadron"].push_back(absId == 211 || absId == 1 || absId == 2);            //j18 (c25)
    fts["PFCandIsElectron"].push_back(absId == 11);                                       //j19 (c26)
    fts["PFCandIsNeutralHadron"].push_back(absId == 130);                                 //j20 (c27)
    fts["PFCandIsMuon"].push_back(absId == 13);                                           //j21 (c28)
    fts["PFCandIsPhoton"].push_back(absId == 22);                                         //j22 (c29)

    //n_pf_cands is a truncation cap only. Candidates are pt-sorted above, so this
    //keeps the hardest n_pf_cands; the graph takes a dynamic particle axis, so
    //there is nothing to pad when the event has fewer.
    if (++nStored == n_pf_cands) break;
  }
  if (debug) {
    std::cout << "*** NOW CHECKING THE SORTING OF PF CANDIDATES ***" << std::endl;
    if ( !std::is_sorted(fts["PFCandLogPt"].begin(), fts["PFCandLogPt"].end(), std::greater<float>() ) ) std::cout << "*** WARNING *** PFCandidates are not sorted in Pt!!!" << std::endl;
    else std::cout << "No issues with the sorting of PF candidates detected" << std::endl;
  }
  
  // method to gather kNN indices
  auto knn = [&](size_t num_neighbors, size_t max_support_size, size_t max_query_size = 0) {
    if (max_query_size == 0)
      max_query_size = max_support_size;

    PointCloud::Points supports(points.begin(), points.begin() + std::min(max_support_size, points.size()));
    PointCloud::Points queries(points.begin(), points.begin() + std::min(max_query_size, points.size()));
    auto result = PointCloud::knn<float>(supports, queries, num_neighbors);  // queries.size() * num_neighbors
    std::vector<float> output(max_query_size * num_neighbors, max_support_size - 1);
    std::copy(result.begin(), result.begin() + std::min(result.size(), output.size()), output.begin());

    //std::cout << "[knn] k=" << num_neighbors << ", num_points=" << points.size()
    //<< ", max_support_size=" << max_support_size << ", max_query_size=" << max_query_size
    //<< ", knn_result_size=" << result.size() << ", final_output_size=" << output.size() << std::endl;
    return output;
  };

  std::vector<float> KNNs = knn(n_knns+1, points.size(), points.size()); //gather n_knns+1 k-nearest neighbors. This vector has size (n_particles * (n_knns+1))
  //std::cout << "size of KNNs is " << KNNs.size() << std::endl;
  //for each particle, the first KNN is the particle itself. The training was done excluding this first KNN. Exclude it during evaluation as well
  for (int i = points.size()-1; i >= 0; i--) KNNs.erase(KNNs.begin()+i*(n_knns+1)); //remove elements starting from the end
  return {fts,KNNs};

};
