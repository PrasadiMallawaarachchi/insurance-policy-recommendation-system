from data.policies import POLICIES

def filter_policies(user, features):
    candidates = []

    for policy_name, policy in POLICIES.items():

        # -----------------------
        # AGE ELIGIBILITY
        # -----------------------
        min_age, max_age = policy["age_range"]
        if not (min_age <= features["age"] <= max_age):
            continue

        # -----------------------
        # INCOME BAND CHECK
        # -----------------------
        if features["income_band"] not in policy["income_band"]:
            continue

        # -----------------------
        # EMPLOYMENT TYPE CHECK
        # -----------------------
        if policy.get("employment_types") and "Any" not in policy["employment_types"]:
            if features["employment_type"] not in policy["employment_types"]:
                continue

        # -----------------------
        # GOAL MATCHING
        # -----------------------
        if features["primary_goal"] not in policy["goals"]:
            continue

        # -----------------------
        # MEDICAL RISK FILTERING
        # -----------------------
        if policy_name == "ClickLife" and features["medical_risk"] != "Low":
            continue

        if policy_name == "FlexLife" and features["medical_risk"] == "Very High":
            continue

        # -----------------------
        # FAMILY REQUIREMENTS
        # -----------------------
        if policy_name == "Life+" and not features["family_responsibility"]:
            continue

        # -----------------------
        # RETIREMENT POLICY LOGIC
        # -----------------------
        if policy_name == "Pension Advantage":
            if not features["goal_retirement"] and not features["age_above_45"]:
                continue

        # -----------------------
        # GROUP POLICY LOGIC (Union Protect)
        # -----------------------
        if policy.get("requires_employer"):
            if not features["group_policy"]:
                continue

        # -----------------------
        # MEDICAL-ONLY POLICY LOGIC
        # -----------------------
        if policy_name == "Health360":
            # Allow even if no medical condition but no existing cover
            if not features["goal_medical"] and features["existing_insurance"]:
                continue

        candidates.append(policy_name)

    return candidates
