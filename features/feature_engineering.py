def derive_features(user):
    features = {}

    # -----------------------
    # AGE & LIFE STAGE
    # -----------------------
    age = user["age_nearest_bday"]
    features["age"] = age
    features["age_above_40"] = age >= 40
    features["age_above_45"] = age >= 45
    features["young"] = age < 35
    features["senior"] = age >= 60

    # -----------------------
    # INCOME & FINANCIAL
    # -----------------------
    income = user["monthly_income"]
    if income < 50000:
        features["income_band"] = "Low"
    elif income < 150000:
        features["income_band"] = "Mid"
    else:
        features["income_band"] = "High"

    features["low_income"] = features["income_band"] == "Low"
    features["mid_income"] = features["income_band"] == "Mid"
    features["high_income"] = features["income_band"] == "High"

    # -----------------------
    # FAMILY & DEMOGRAPHIC
    # -----------------------
    features["dependents"] = user["dependents_count"] > 0
    features["dependents_count"] = user["dependents_count"]
    features["married"] = user["marital_status"] == "Married"
    features["family_responsibility"] = (
        features["married"] or features["dependents"]
    )

    # -----------------------
    # OCCUPATION & WORK
    # -----------------------
    features["employment_type"] = user["employment_type"]
    features["hazardous_job"] = user["hazardous_level"] in ["Medium", "High"]
    features["hazardous_activities"] = bool(user["hazardous_activities"])

    # Employer / group scheme flag
    features["group_policy"] = (
        user["employment_type"] == "Permanent"
        and user.get("employer_scheme", False)
    )

    # -----------------------
    # MEDICAL CONDITIONS
    # -----------------------
    features["chronic"] = user["chronic_disease"]
    features["cardio"] = user["cardiovascular_health_issue"]
    features["cancer"] = user["cancer_or_tumors"]
    features["respiratory"] = user["respiratory_conditions"]
    features["neuro_mental"] = user["neurological_or_mental_health_conditions"]
    features["gastro"] = user["gastrointestinal_conditions"]
    features["musculoskeletal"] = user["musculoskeletal_conditions"]
    features["infectious"] = user["infectious_or_sexual_health_conditions"]

    medical_flags = [
        features["chronic"],
        features["cardio"],
        features["cancer"],
        features["respiratory"],
        features["neuro_mental"],
        features["gastro"],
        features["musculoskeletal"],
        features["infectious"]
    ]

    features["any_medical"] = any(medical_flags)

    if features["cancer"] or features["cardio"]:
        features["medical_risk"] = "Very High"
    elif features["chronic"] or features["respiratory"]:
        features["medical_risk"] = "High"
    elif features["any_medical"]:
        features["medical_risk"] = "Medium"
    else:
        features["medical_risk"] = "Low"

    # -----------------------
    # LIFESTYLE
    # -----------------------
    features["bmi"] = user["bmi"]
    features["bmi_high"] = user["bmi"] >= 30
    features["underweight"] = user["bmi"] < 18.5
    features["smoker"] = user["smoker"] == "Yes"
    features["alcohol_consumer"] = user["alcohol_consumer"] == "Yes"

    # -----------------------
    # GENDER-SPECIFIC
    # -----------------------
    features["female"] = user["gender"] == "Female"
    features["female_childbearing_age"] = (
        features["female"] and 22 <= age <= 42
    )

    # -----------------------
    # GOALS
    # -----------------------
    features["primary_goal"] = user["primary_goal"]
    features["secondary_goal"] = user.get("secondary_goal")

    features["goal_family_protection"] = user["primary_goal"] in [
        "Family protection", "Income replacement"
    ]
    features["goal_retirement"] = user["primary_goal"] == "Retirement"
    features["goal_savings"] = user["primary_goal"] in [
        "Savings", "Stable income", "Retirement with liquidity"
    ]
    features["goal_medical"] = user["primary_goal"] == "Medical coverage"

    # -----------------------
    # TRAVEL & REGULATORY
    # -----------------------
    features["frequent_travel"] = user["travel_history_high_risk_countries"]
    features["dual_citizenship"] = user["dual_citizenship"]
    features["tax_or_regulatory_flags"] = user["tax_or_regulatory_flags"]

    # -----------------------
    # INSURANCE HISTORY
    # -----------------------
    features["existing_insurance"] = user["existing_insurance"] == "Yes"
    features["insurance_history_issues"] = user["insurance_history_issues"]
    features["current_insurance_status"] = user["current_insurance_status"]

    return features
