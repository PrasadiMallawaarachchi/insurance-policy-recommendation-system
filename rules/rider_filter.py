from data.riders import RIDERS

def filter_riders(policy_name, policy_data, features):
    eligible = []

    for name, rider in RIDERS.items():
        if not rider["standalone"] and name not in policy_data["attachable_riders"]:
            continue

        trigger_hit = any(features.get(t, False) for t in rider["triggers"])
        if trigger_hit:
            eligible.append(name)

    return eligible
