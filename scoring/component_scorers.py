"""
Component-level scoring functions for ensemble recommendation system.
Each function returns (score: float, breakdown: dict) for explainability.
"""

def rule_based_score_policy(user, features, policy_data):
    """
    Calculate rule-based score for a policy based on feature matching.
    
    Returns:
        tuple: (final_score: float, breakdown: dict)
    """
    scores = {}
    
    # Age fit score (distance from optimal age)
    min_age, max_age = policy_data["age_range"]
    age = features["age"]
    age_range = max_age - min_age
    
    if min_age <= age <= max_age:
        # Calculate how centered the age is
        midpoint = (min_age + max_age) / 2
        distance = abs(age - midpoint)
        max_distance = age_range / 2
        scores['age_fit'] = 1.0 - (distance / max_distance * 0.3)  # Max penalty 30%
    else:
        scores['age_fit'] = 0.0
    
    # Income fit score
    if features["income_band"] in policy_data["income_band"]:
        scores['income_fit'] = 1.0
    else:
        # Check if adjacent band
        income_order = ["Low", "Mid", "High"]
        user_idx = income_order.index(features["income_band"])
        policy_bands_idx = [income_order.index(b) for b in policy_data["income_band"]]
        
        min_distance = min(abs(user_idx - idx) for idx in policy_bands_idx)
        if min_distance == 1:
            scores['income_fit'] = 0.7  # Adjacent band
        else:
            scores['income_fit'] = 0.3
    
    # Goal alignment score
    if features["primary_goal"] in policy_data["goals"]:
        scores['goal_alignment'] = 1.0
    elif features.get("secondary_goal") in policy_data["goals"]:
        scores['goal_alignment'] = 0.5
    else:
        scores['goal_alignment'] = 0.1
    
    # Employment type fit
    employment_types = policy_data.get("employment_types", ["Any"])
    if "Any" in employment_types:
        scores['employment_fit'] = 1.0
    elif features["employment_type"] in employment_types:
        scores['employment_fit'] = 1.0
    else:
        scores['employment_fit'] = 0.2
    
    # Medical eligibility score
    medical_risk = features["medical_risk"]
    
    # Policy-specific medical logic
    if "ClickLife" in str(policy_data.get("text", "")):
        if medical_risk == "Low":
            scores['medical_eligibility'] = 1.0
        else:
            scores['medical_eligibility'] = 0.0
    elif "FlexLife" in str(policy_data.get("text", "")):
        if medical_risk == "Very High":
            scores['medical_eligibility'] = 0.0
        elif medical_risk == "High":
            scores['medical_eligibility'] = 0.5
        else:
            scores['medical_eligibility'] = 1.0
    else:
        # Most policies accept various medical risks with underwriting
        risk_scores = {
            "Low": 1.0,
            "Medium": 0.9,
            "High": 0.7,
            "Very High": 0.5
        }
        scores['medical_eligibility'] = risk_scores.get(medical_risk, 0.8)
    
    # Weighted average of all components
    weights = {
        'age_fit': 0.25,
        'income_fit': 0.20,
        'goal_alignment': 0.35,
        'employment_fit': 0.10,
        'medical_eligibility': 0.10
    }
    
    final_score = sum(scores[key] * weights[key] for key in scores)
    
    return final_score, scores


def rule_based_score_rider(user, features, rider_data):
    """
    Calculate rule-based score for a rider.
    Riders have simpler rules - mainly trigger matching.
    
    Returns:
        tuple: (final_score: float, breakdown: dict)
    """
    scores = {}
    
    # Trigger strength is the main component for riders
    triggers = rider_data.get("triggers", [])
    if triggers:
        matched_triggers = [t for t in triggers if features.get(t, False)]
        trigger_ratio = len(matched_triggers) / len(triggers)
        scores['trigger_match'] = trigger_ratio
        scores['matched_triggers'] = matched_triggers
    else:
        scores['trigger_match'] = 0.5  # No triggers means generally applicable
        scores['matched_triggers'] = []
    
    # Medical relevance for health-related riders
    rider_text = rider_data.get("text", "").lower()
    if any(word in rider_text for word in ["hospital", "medical", "health", "chronic", "illness"]):
        if features["any_medical"] or features["age_above_40"]:
            scores['medical_relevance'] = 1.0
        else:
            scores['medical_relevance'] = 0.5
    else:
        scores['medical_relevance'] = 0.8  # Non-medical riders
    
    # Family relevance
    if any(word in rider_text for word in ["child", "spouse", "family", "dependent"]):
        if features["dependents"] or features["married"]:
            scores['family_relevance'] = 1.0
        else:
            scores['family_relevance'] = 0.3
    else:
        scores['family_relevance'] = 0.8
    
    # Weighted combination
    weights = {
        'trigger_match': 0.6,
        'medical_relevance': 0.25,
        'family_relevance': 0.15
    }
    
    final_score = sum(scores.get(key, 0.5) * weights[key] for key in weights)
    
    return final_score, scores


def trigger_strength_score(features, triggers):
    """
    Calculate how strongly user features match trigger conditions.
    
    Args:
        features: User feature dict
        triggers: List of trigger feature names
    
    Returns:
        tuple: (strength: float, breakdown: dict)
    """
    if not triggers:
        return 0.5, {'matched_triggers': [], 'total_triggers': 0, 'match_ratio': 0.5}
    
    matched = [t for t in triggers if features.get(t, False)]
    strength = len(matched) / len(triggers)
    
    breakdown = {
        'matched_triggers': matched,
        'unmatched_triggers': [t for t in triggers if t not in matched],
        'total_triggers': len(triggers),
        'match_ratio': strength
    }
    
    return strength, breakdown


def financial_fit_score(monthly_income, estimated_premium_percentage=5.0):
    """
    Calculate affordability score based on income and estimated premium.
    
    Args:
        monthly_income: User's monthly income
        estimated_premium_percentage: Estimated premium as % of income (default 5%)
    
    Returns:
        tuple: (score: float, breakdown: dict)
    """
    # Premium ratio to income
    premium_ratio = estimated_premium_percentage / 100
    
    # Scoring based on affordability guidelines
    # Ideal: < 5% of income
    # Acceptable: 5-10% of income
    # Moderate: 10-15% of income
    # Expensive: > 15% of income
    
    if premium_ratio < 0.05:
        score = 1.0
        status = 'highly_affordable'
    elif premium_ratio < 0.10:
        score = 0.8
        status = 'affordable'
    elif premium_ratio < 0.15:
        score = 0.5
        status = 'moderate'
    else:
        score = 0.2
        status = 'expensive'
    
    breakdown = {
        'status': status,
        'premium_ratio': premium_ratio,
        'monthly_income': monthly_income,
        'estimated_premium': monthly_income * premium_ratio
    }
    
    return score, breakdown


def estimate_policy_premium_percentage(policy_name, features):
    """
    Estimate premium as percentage of monthly income for a policy.
    This is a simplified estimation - in production, use actuarial calculations.
    
    Args:
        policy_name: Name of the policy
        features: User features dict
    
    Returns:
        float: Estimated premium as percentage of monthly income
    """
    # Base percentages by policy type
    base_rates = {
        "FlexLife": 7.0,
        "Life+": 5.0,
        "Health360": 6.0,
        "Pension Advantage": 8.0,
        "ClickLife": 3.0,
        "Union Protect": 2.0  # Employer-subsidized
    }
    
    base_rate = base_rates.get(policy_name, 5.0)
    
    # Adjust for age (older = more expensive)
    age = features["age"]
    if age > 50:
        base_rate *= 1.4
    elif age > 40:
        base_rate *= 1.2
    elif age < 30:
        base_rate *= 0.8
    
    # Adjust for medical risk
    risk_multipliers = {
        "Low": 1.0,
        "Medium": 1.2,
        "High": 1.5,
        "Very High": 2.0
    }
    base_rate *= risk_multipliers.get(features["medical_risk"], 1.0)
    
    # Adjust for smoker
    if features["smoker"]:
        base_rate *= 1.3
    
    # Adjust for hazardous job
    if features["hazardous_job"]:
        base_rate *= 1.2
    
    # Cap at reasonable maximum (20% of income)
    return min(base_rate, 20.0)


def estimate_rider_premium_percentage(rider_name):
    """
    Estimate additional premium for a rider as percentage of monthly income.
    
    Args:
        rider_name: Name of the rider
    
    Returns:
        float: Estimated premium as percentage of monthly income
    """
    # Riders typically add 0.5-2% of income
    rider_costs = {
        "Critical Illness": 1.5,
        "Hospitalisation": 1.8,
        "TPD": 1.2,
        "ADB": 0.5,
        "Disability Income": 2.0,
        "Income Protection": 2.0,
        "Chronic Medication": 1.5,
        "Maternity": 1.0,
        "OPD": 1.2,
        "Hospital Cash": 0.8,
        "Child Health": 1.0,
        "Spouse Benefit": 1.0,
        "Premium Waiver": 0.5,
        "Funeral Benefit": 0.3,
        "Cancer Care": 1.5,
        "Organ Transplant": 1.0,
        "Overseas Treatment": 0.8,
        "Group ADB": 0.3,
        "Group Disability": 0.8,
        "Group Critical Illness": 1.0,
        "Group Hospital Cash": 0.5,
        "Surgery Benefit": 1.0
    }
    
    return rider_costs.get(rider_name, 1.0)
