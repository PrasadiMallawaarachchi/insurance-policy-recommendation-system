import numpy as np
from data.riders import RIDERS

def rank_riders(user_vec, rider_names, embedder):
    texts = [RIDERS[r]["text"] for r in rider_names]
    rider_vecs = embedder.encode(texts)

    scores = np.dot(rider_vecs, user_vec)

    return sorted(
        zip(rider_names, scores),
        key=lambda x: x[1],
        reverse=True
    )
