import numpy as np
from data.policies import POLICIES

def rank_policies(user_vec, policy_names, embedder):
    texts = [POLICIES[p]["text"] for p in policy_names]
    policy_vecs = embedder.encode(texts)

    scores = np.dot(policy_vecs, user_vec)

    ranked = sorted(
        zip(policy_names, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked
