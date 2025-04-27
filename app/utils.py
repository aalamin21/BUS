import itertools
import numpy as np
from .models import User
from .availability_utils import flatten_availability
from .module_utils import module_list

NUM_SLOTS = 70  # 7 days * 10 time slots
MODULE_WEIGHT = 0.5
AVAILABILITY_WEIGHT = 0.3
OVERLAP_WEIGHT = 0.2


def get_user_modules(user):
    """Get valid modules for a user, ignoring unselected (-1)"""
    return [module_list[i] for i in [user.module1, user.module2, user.module3] if i >= 0]


def jaccard_similarity(vec1, vec2):
    """Now handles both availability vectors and module sets"""
    if isinstance(vec1, np.ndarray):  # Availability vectors
        intersection = np.sum(np.minimum(vec1, vec2))
        union = np.sum(np.maximum(vec1, vec2))
    else:  # Module sets
        intersection = len(vec1 & vec2)
        union = len(vec1 | vec2)
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


        group_members = [current_user] + [u for u in other_users if u.id in group_ids]

        # Calculate module compatibility
        module_scores = []
        for u1, u2 in itertools.combinations(group_members, 2):
            mods1 = set(get_user_modules(u1))
            mods2 = set(get_user_modules(u2))
            module_scores.append(jaccard_similarity(mods1, mods2))
        module_score = np.mean(module_scores) if module_scores else 0

        sim_scores = [
            jaccard_similarity(group_vecs[i], group_vecs[j])
            for i in range(len(group_vecs))
            for j in range(i + 1, len(group_vecs))
        ]
        avg_similarity = np.mean(sim_scores)
        match_score = AVAILABILITY_WEIGHT * avg_similarity + MODULE_WEIGHT * module_score + OVERLAP_WEIGHT * overlap_score

        scored_groups.append({
            "group_members": [all_users[uid] for uid in group_ids],
            "shared_slots": np.where(shared == 1)[0].tolist(),
            "match_score": round(match_score, 2),
            # MODULE INFO
            "common_modules": list(set.intersection(
                *[set(get_user_modules(u)) for u in group_members]
            )) if group_members else []
        })

    return sorted(scored_groups, key=lambda g: g["match_score"], reverse=True)[:top_n]

