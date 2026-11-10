"""Closure test: ABCNetProducer weights vs the Keras SavedModel run on inputs built in Python
following the NanoAOD PFCands table (custom_btv_cff.py) + clean_nano.py.

Rebuilds the 23 input features from packedPFCandidates independently of ABCNetMakeInputs.cc,
pT-sorts, takes the 15 nearest neighbours in (eta, phi) with a k-d tree (as the C++ nanoflann
kNN), runs the SavedModel and prints, per event, the max and 99th-percentile |C++ - Python| of the
SWD and combined weights over all candidates.

    cmsenv; export X509_USER_PROXY=...
    cmsRun runABCNet_closure_cfg.py maxEvents=6 outputFile=closure.root \
        [graph=CommonTools/PileupAlgos/data/<frozen graph>.pb]     # default: ABCNet_cff.py's graph
    python3 validateABCNet_closure.py closure_numEvent6.root <SavedModel dir of the same model> 6 [knn]

knn selects how the Python side builds the neighbours:
  kdtree (default)  as the C++: k-d tree in plain (eta, phi), no phi wrapping -> pure closure test
  dr                as the training h5 (batch.py): nearest by dR with phi wrapped to [-pi, pi],
                    every particle with the same eta as itself excluded, first 15 of 20 -> measures
                    what the C++ kNN (no wrapping) does to the weights and MET vs training
  dr_nowrap         as dr but without the phi wrapping, to separate the wrapping from the
                    same-eta exclusion
"""
import sys
import numpy as np
import ROOT
from DataFormats.FWLite import Events, Handle
import tensorflow as tf
from scipy.spatial import cKDTree

fname, model_dir, nev = sys.argv[1], sys.argv[2], int(sys.argv[3])
knn_mode = sys.argv[4] if len(sys.argv) > 4 else 'kdtree'
model = tf.saved_model.load(model_dir).signatures['serving_default']
K = 15


def knn_training(eta, phi, wrap=True):
    """kNN as batch.py builds it: argsort of dR with phi wrapping, same-eta entries (self) set to inf.
    wrap=False drops only the phi wrapping, to separate its effect from the same-eta exclusion."""
    deta = eta[:, None] - eta[None, :]
    dphi = phi[:, None] - phi[None, :]
    if wrap:
        dphi = np.where(dphi > np.pi, dphi - 2 * np.pi, dphi)
        dphi = np.where(dphi < -np.pi, dphi + 2 * np.pi, dphi)
    dr = np.sqrt(deta ** 2 + dphi ** 2)
    dr[deta == 0] = np.inf
    return np.argsort(dr, axis=1, kind='stable')[:, :K]

hc = Handle('std::vector<pat::PackedCandidate>')
hw = Handle('edm::ValueMap<float>')
hs = Handle('edm::ValueMap<float>')
HP = ROOT.reco.TrackBase.highPurity


def feats(c):
    t = c.pseudoTrack() if c.hasTrackDetails() else None
    lg = lambda x: np.log(x) if x > 0 else 0.
    sub = lambda x, r: r if x == -1 else x
    absid = abs(c.pdgId())
    d0 = sub(c.dxy() if t else -1, 0)
    dz = sub(c.dz() if t else -1, 0)
    chi2 = sub(t.normalizedChi2() if t else -1, 100)
    return [lg(c.pt()), c.eta(), c.phi(), c.mass(), c.charge(),
            np.clip(d0, -40, 40) / 40, lg(c.dxyError() if t else -1),
            np.clip(dz, -40, 40) / 40, lg(c.dzError() if t else -1),
            lg(t.pt() if t else -1), t.eta() if t else -1, t.phi() if t else -1, lg(t.p() if t else -1),
            np.clip(chi2, 0, 100) / 100,
            c.pvAssociationQuality(), float(t.quality(HP)) if t else 0., c.lostInnerHits(),
            t.qualityMask() if t else 0,
            float(absid in (211, 1, 2)), float(absid == 11), float(absid == 130), float(absid == 13), float(absid == 22)]


for i, ev in enumerate(Events(fname)):
    if i == nev:
        break
    ev.getByLabel('packedPFCandidates', hc)
    ev.getByLabel('abc', hw)
    ev.getByLabel(('abc', 'swd'), hs)
    cands = hc.product()
    n = cands.size()
    cpp_w = np.array([hw.product().get(j) for j in range(n)])
    cpp_s = np.array([hs.product().get(j) for j in range(n)])
    pts = np.array([cands[j].pt() for j in range(n)])
    order = np.argsort(-pts, kind='stable')
    x = np.array([feats(cands[int(j)]) for j in order], dtype=np.float32)
    if knn_mode in ('dr', 'dr_nowrap'):
        nn = knn_training(x[:, 1].astype(np.float64), x[:, 2].astype(np.float64),
                          wrap=(knn_mode == 'dr')).astype(np.float32)
    else:
        # same kNN as the C++ (k-d tree in plain eta, phi; first neighbour is the particle itself)
        _, nn = cKDTree(x[:, 1:3]).query(x[:, 1:3], k=K + 1)
        nn = nn[:, 1:].astype(np.float32)
    y = model(input_1=tf.constant(x[None]), input_2=tf.constant(nn[None]))['concatenate'].numpy()[0]
    py_s, py_w = np.empty(n), np.empty(n)
    py_s[order], py_w[order] = y[:, -2], y[:, -1]   # SWD and combined are always the last two
    dw, ds = np.abs(cpp_w - py_w), np.abs(cpp_s - py_s)
    print(f'event {i} [{knn_mode}]: nPF={n}  combined: max|diff|={dw.max():.2e} (99%={np.percentile(dw, 99):.1e})  '
          f'swd: max|diff|={ds.max():.2e}  | mean swd={cpp_s.mean():.3f} mean comb={cpp_w.mean():.3f} '
          f'max comb={cpp_w.max():.2f}')
    if knn_mode in ('dr', 'dr_nowrap'):
        # where the differences sit, and what they do to the MET (|sum w pT|, as cluster.py)
        phi = np.array([cands[j].phi() for j in range(n)])
        pxy = np.array([[cands[j].px(), cands[j].py()] for j in range(n)])
        met = lambda w: np.hypot(*(w[:, None] * pxy).sum(axis=0))
        big = dw > 1e-3
        print(f'    candidates with |diff| > 1e-3: {big.sum()} ({100 * big.mean():.1f}%), of which '
              f'{(np.abs(phi[big]) > np.pi - 0.5).sum()} at |phi| > pi - 0.5 '
              f'(all cands there: {(np.abs(phi) > np.pi - 0.5).sum()}) | '
              f'MET C++ {met(cpp_w):.2f} GeV vs training-kNN {met(py_w):.2f} GeV')
    if i == 0:
        pvq = np.array([cands[j].pvAssociationQuality() for j in range(n)])
        ch = np.array([cands[j].charge() for j in range(n)]) != 0
        print('  charged PV-fit (pvAssocQ 7) mean swd:', cpp_s[ch & (pvq == 7)].mean(),
              '| charged not-PV (pvAssocQ<=1) mean swd:', cpp_s[ch & (pvq <= 1)].mean(),
              '| neutrals mean swd / comb:', cpp_s[~ch].mean(), cpp_w[~ch].mean())
