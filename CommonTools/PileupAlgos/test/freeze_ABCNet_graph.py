"""Freeze a trained ABCNet SavedModel into the .pb graph ABCNetProducer loads.

    source /vols/cms/saa220/.pyenvs/tf215env/bin/activate
    python3 freeze_ABCNet_graph.py <SavedModel dir> <output .pb> [cleaned h5 .tar.gz for the check]

Uses the serving_default signature: its inputs become the placeholders input_1 (1, N, n_feats) and
input_2 (1, N, n_knns), its output is renamed Identity, as ABCNetProducer expects. With a cleaned h5 file
the frozen graph and the SavedModel are run on its first event and their outputs compared.
"""
import io
import sys
import tarfile

import numpy as np
import tensorflow as tf
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

INPUT_FEATS = [0, 1, 2, 3, 16, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 20, 21, 24, 25, 26, 27, 28, 29]
N_KNNS = 15

model_dir, out_pb = sys.argv[1], sys.argv[2]
model = tf.saved_model.load(model_dir)
sig = model.signatures["serving_default"]
inputs = sig.structured_input_signature[1]
outputs = sig.structured_outputs
print("signature inputs:", {k: (v.shape, v.dtype.name) for k, v in inputs.items()})
print("signature outputs:", {k: (v.shape, v.dtype.name) for k, v in outputs.items()})
if sorted(inputs) != ["input_1", "input_2"] or len(outputs) != 1:
    sys.exit("expected inputs input_1, input_2 and a single output")
out_key = next(iter(outputs))


@tf.function(input_signature=[tf.TensorSpec(inputs["input_1"].shape, inputs["input_1"].dtype, name="input_1"),
                              tf.TensorSpec(inputs["input_2"].shape, inputs["input_2"].dtype, name="input_2")])
def serve(input_1, input_2):
    return tf.identity(sig(input_1=input_1, input_2=input_2)[out_key], name="Identity")


frozen = convert_variables_to_constants_v2(serve.get_concrete_function())
graph_def = frozen.graph.as_graph_def()
names = {n.name for n in graph_def.node}
for needed in ("input_1", "input_2", "Identity"):
    if needed not in names:
        sys.exit(f"node {needed} missing from the frozen graph")
tf.io.write_graph(graph_def, ".", out_pb, as_text=False)
print(f"wrote {out_pb}: {len(graph_def.node)} nodes")

if len(sys.argv) > 3:
    with tarfile.open(sys.argv[3], "r:gz") as tar:
        member = next(m for m in tar if m.name.endswith(".h5"))
        import h5py
        with h5py.File(io.BytesIO(tar.extractfile(member).read()), "r") as h:
            x = np.take(np.array(h["data"][:1]), INPUT_FEATS, axis=-1).astype(np.float32)
            idx = np.array(h["indices"][:1, :, :N_KNNS]).astype(inputs["input_2"].dtype.as_numpy_dtype)
    ref = sig(input_1=tf.constant(x), input_2=tf.constant(idx))[out_key].numpy()
    got = frozen(tf.constant(x), tf.constant(idx))
    got = (got[0] if isinstance(got, (list, tuple)) else got).numpy()
    valid = x[0, :, 1] > -900
    print(f"output shape {ref.shape} (n_feats {len(INPUT_FEATS)} + {ref.shape[-1] - len(INPUT_FEATS)} extra columns)")
    print(f"frozen vs SavedModel, {valid.sum()} real candidates: max |diff| SWD {np.abs(ref - got)[0, valid, -2].max():.2e}, "
          f"combined {np.abs(ref - got)[0, valid, -1].max():.2e}")
