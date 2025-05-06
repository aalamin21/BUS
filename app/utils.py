import numpy as np
from .models import User, Group
from .availability_utils import slot_overlap
from .module_utils import module_list

NUM_SLOTS = 70
MODULE_WEIGHT = 0.5
AVAILABILITY_WEIGHT = 0.3
OVERLAP_WEIGHT = 0.2

def get_user_modules(user):
    return set(module_list[i] for i in [user.module1, user.module2, user.module3] if i >= 0)

def jaccard_similarity(vec1, vec2):
    if isinstance(vec1, np.ndarray):
        intersection = np.sum(np.minimum(vec1, vec2))
        union = np.sum(np.maximum(vec1, vec2))
    else:
        intersection = len(vec1 & vec2)
        union = len(vec1 | vec2)
    return intersection / union if union != 0 else 0

def compute_match_score(mod_sim, avail_sim, overlap_sim=1):
    return MODULE_WEIGHT * mod_sim + AVAILABILITY_WEIGHT * avail_sim + OVERLAP_WEIGHT * overlap_sim

def suggest_groups_for_user(current_user, group_size=4, top_n=3):
    user_vec = np.array(current_user.availability)
    user_modules = get_user_modules(current_user)



    existing_groups = Group.query.all()
    scored_groups = []

    for group in existing_groups:
        members = group.users
        if not members:
            continue

        member_scores = []

        for member in members:
            mod_sim = jaccard_similarity(user_modules, get_user_modules(member))
            avail_sim = jaccard_similarity(user_vec, np.array(member.availability))
            overlap_sim = 1 if slot_overlap(current_user.availability, member.availability) else 0

            score = compute_match_score(mod_sim, avail_sim, overlap_sim)
            member_scores.append(score)

        avg_score = sum(member_scores) / len(member_scores)
        scored_groups.append((group, avg_score))

    scored_groups.sort(key=lambda x: x[1], reverse=True)
    top_existing_groups = scored_groups[:top_n]

    # --------------------------
    # SUGGEST NEW GROUP
    # --------------------------
    all_users = User.query.filter(User.id != current_user.id, User.group_id == None).all()
    scored_users = []

    for u in all_users:
        mod_sim = jaccard_similarity(user_modules, get_user_modules(u))
        avail_sim = jaccard_similarity(user_vec, np.array(u.availability))
        overlap_sim = 1 if slot_overlap(current_user.availability, u.availability) else 0
        score = compute_match_score(mod_sim, avail_sim, overlap_sim)
        scored_users.append((u, score))

    scored_users.sort(key=lambda x: x[1], reverse=True)
    top_users = [u for u, _ in scored_users[:group_size - 1]]

    if len(top_users) + 1 < group_size:
        new_group = None
    else:
        group_users = [current_user] + top_users
        final_score = sum(score for _, score in scored_users[:group_size - 1]) / len(group_users)
        new_group = format_group(group_users, score=final_score)


    formatted_existing_groups = [
        format_group(g.users, score=s, group=g) for g, s in top_existing_groups
    ]

    return formatted_existing_groups, new_group

def format_group(users, score=None, group=None):
    member_names = [u.first_name for u in users]
    common_modules = list(set.intersection(*(get_user_modules(u) for u in users)))
    shared_slots = list(set.intersection(*(set(u.availability) for u in users if u.availability)))
    return {
        "group_members": [u.first_name for u in users],
        "common_modules": list(common_modules),
        "shared_slots": shared_slots,
        "match_score": score if score is not None else 0.0,
        "group": group  #  new key
    }


def score_user_to_group(user, group):
    user_modules = get_user_modules(user)
    user_avail = np.array(user.availability)

    group_users = group.users
    if not group_users:
        return 0

    group_modules = set().union(*(get_user_modules(u) for u in group_users))
    group_avail = np.array([u.availability for u in group_users if u.availability])
    if not len(group_avail):
        return 0
    group_avg_avail = np.mean(group_avail, axis=0)

    mod_sim = jaccard_similarity(user_modules, group_modules)
    avail_sim = jaccard_similarity(user_avail, group_avg_avail)
    overlap_sim = 1 if any(slot_overlap(user.availability, u.availability) for u in group_users) else 0

    return compute_match_score(mod_sim, avail_sim, overlap_sim)

def find_existing_group_matches(current_user, all_groups, top_n=3):
    scored = []
    for g in all_groups:
        if current_user.id in [u.id for u in g.users]:
            continue
        score = score_user_to_group(current_user, g)
        if score > 0:
            scored.append((g, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    formatted = []
    for g, score in scored[:top_n]:
        formatted.append(format_group(g.users, score=score))
    return formatted

def get_all_suggestions(current_user):
    all_groups = Group.query.all()
    existing_group_suggestions = find_existing_group_matches(current_user, all_groups)
    new_group_suggestions = suggest_groups_for_user(current_user)
    return existing_group_suggestions + new_group_suggestions

