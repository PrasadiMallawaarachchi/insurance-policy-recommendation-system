def build_user_text(user, features):
    """
    Build comprehensive natural language description of user profile.
    Enhanced version with richer context for better NLP matching.
    
    Args:
        user: Raw user dict
        features: Derived features dict
    
    Returns:
        str: Natural language user description
    """
    text = f"""
    {user['age_nearest_bday']} year old {user['gender']} {user['marital_status']} person.
    Occupation: {user['occupation']} with {user['employment_type']} employment.
    Income level: {features['income_band']} (Rs. {user['monthly_income']:,} per month).
    Primary goal: {user['primary_goal']}.
    """

    # Secondary goal
    if features.get("secondary_goal"):
        text += f"Secondary goal: {features['secondary_goal']}. "

    # Family details
    if features["dependents"]:
        text += f"Has {user['dependents_count']} dependent(s) requiring family protection. "
    
    if features["married"]:
        text += "Married with family responsibilities. "

    # Medical conditions (detailed)
    if features["any_medical"]:
        text += "Has medical conditions"
        conditions = []
        if features["chronic"]:
            conditions.append("chronic disease")
        if features["cardio"]:
            conditions.append("cardiovascular issues")
        if features["cancer"]:
            conditions.append("cancer history")
        if conditions:
            text += f" including {', '.join(conditions)}"
        text += f". Medical risk level: {features['medical_risk']}. "

    # Lifestyle factors
    if features["smoker"]:
        text += "Smoker with elevated health risks. "
    
    if features["bmi_high"]:
        text += f"BMI of {user['bmi']} indicating health risk factors. "

    # Occupation risks
    if features["hazardous_job"]:
        text += f"Works in hazardous occupation ({user['hazardous_level']} risk level). "
    
    if features["hazardous_activities"]:
        text += "Engages in hazardous work activities. "

    # Age-related context
    if features["age_above_45"]:
        text += "At an age where retirement planning and critical illness coverage become important. "
    elif features["age_above_40"]:
        text += "Age-related health risks require consideration. "
    elif features["young"]:
        text += "Young with opportunity for long-term savings and affordable protection. "

    # Financial context
    if features["existing_insurance"]:
        text += "Has existing insurance coverage. "
    
    # Group policy eligibility
    if features["group_policy"]:
        text += "Eligible for employer-sponsored group insurance benefits. "

    return text.strip()


def build_user_aspects(user, features):
    """
    Build separate text descriptions for different aspects of user profile.
    Enables aspect-level semantic matching.
    
    Args:
        user: Raw user dict
        features: Derived features dict
    
    Returns:
        dict: Aspect names mapped to their text descriptions
    """
    aspects = {}
    
    # Demographic aspect
    aspects['demographic'] = f"""
    {user['age_nearest_bday']} year old {user['gender']}, {user['marital_status']}.
    {user['employment_type']} employment as {user['occupation']}.
    """
    
    # Financial aspect
    aspects['financial'] = f"""
    Income level: {features['income_band']} (Rs. {user['monthly_income']:,}/month).
    {"Has existing insurance. " if features["existing_insurance"] else "No existing insurance. "}
    Seeking {"affordable " if features["low_income"] else ""}insurance solutions.
    """
    
    # Medical/Health aspect
    if features["any_medical"]:
        medical_details = []
        if features["chronic"]:
            medical_details.append("chronic conditions")
        if features["cardio"]:
            medical_details.append("cardiovascular issues")
        if features["cancer"]:
            medical_details.append("cancer history")
        
        aspects['medical'] = f"""
        Medical risk level: {features['medical_risk']}.
        Conditions: {', '.join(medical_details) if medical_details else 'various health issues'}.
        {"Smoker. " if features["smoker"] else "Non-smoker. "}
        BMI: {user['bmi']}.
        """
    else:
        aspects['medical'] = f"""
        Healthy individual with low medical risk.
        {"Smoker. " if features["smoker"] else "Non-smoker. "}
        BMI: {user['bmi']}.
        """
    
    # Goals/Needs aspect
    aspects['goals'] = f"""
    Primary goal: {user['primary_goal']}.
    {f"Secondary goal: {features.get('secondary_goal')}. " if features.get('secondary_goal') else ""}
    {"Needs family protection for dependents. " if features["dependents"] else ""}
    {"Planning for retirement. " if features["goal_retirement"] else ""}
    {"Focus on savings and wealth building. " if features["goal_savings"] else ""}
    """
    
    return aspects
