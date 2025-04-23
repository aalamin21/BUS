import itertools
import numpy as np
from .models import User  # or adjust import path
from .availability_utils import flatten_availability
NUM_SLOTS = 70  # 7 days * 10 time slots


def jaccard_similarity(vec1, vec2):
    intersection = np.sum(np.minimum(vec1, vec2))
    union = np.sum(np.maximum(vec1, vec2))
    return intersection / union if union != 0 else 0


def suggest_groups_for_user(current_user, group_size=4, top_n=3):
    user_vec = np.array(flatten_availability(current_user.availability))
    print("Current user availability:", current_user.availability)
    print("Flattened vector:", user_vec)

    other_users = User.query.filter(User.id != current_user.id).all()

    all_users = {u.id: "{} {}".format(u.first_name, u.last_name) for u in User.query.all()}  # ✅ CORRECTLY PLACED

    user_data = {
        u.id: np.array(flatten_availability(u.availability))
        for u in other_users
    }

    #group_candidates = list(itertools.combinations(user_data.keys(), group_size - 1))
    group_candidates = []
    for size in range(3, 6):  # 3 others + current user = 4 to 6
        group_candidates += list(itertools.combinations(user_data.keys(), size))

    scored_groups = []

    for group_ids in group_candidates:
        group_users = [current_user.id] + list(group_ids)
        group_vecs = [user_vec] + [user_data[uid] for uid in group_ids]
        group_matrix = np.stack(group_vecs)

        shared = np.all(group_matrix == 1, axis=0)
        overlap_score = np.sum(shared) / NUM_SLOTS
        #  Skip groups with no shared time slots at all
        if np.sum(shared) == 0:
            continue

        sim_scores = [
            jaccard_similarity(group_vecs[i], group_vecs[j])
            for i in range(len(group_vecs))
            for j in range(i + 1, len(group_vecs))
        ]
        avg_similarity = np.mean(sim_scores)
        match_score = 0.7 * avg_similarity + 0.3 * overlap_score

        scored_groups.append({
            "group_members": [all_users[uid] for uid in group_ids],
            "shared_slots": np.where(shared == 1)[0].tolist(),
            "match_score": round(match_score, 2)
        })

    return sorted(scored_groups, key=lambda g: g["match_score"], reverse=True)[:top_n]

