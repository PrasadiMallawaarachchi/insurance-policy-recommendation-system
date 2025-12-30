RIDERS = {
    # MEDICAL / HEALTH
    "Hospitalisation": {
        "text": "Covers inpatient hospital expenses including surgery and ICU.",
        "standalone": False,
        "triggers": ["any_medical", "dependents"]
    },
    "OPD": {
        "text": "Covers outpatient consultations and diagnostics.",
        "standalone": True,
        "triggers": ["chronic"]
    },
    "Chronic Medication": {
        "text": "Covers long-term medication for chronic diseases.",
        "standalone": True,
        "triggers": ["chronic"]
    },
    "Maternity": {
        "text": "Covers maternity and newborn expenses.",
        "standalone": False,
        "triggers": ["female_childbearing_age"]
    },
    "Organ Transplant": {
        "text": "Provides financial support for organ transplant procedures.",
        "standalone": True,
        "triggers": ["severe_organ_condition"]
    },
    "Overseas Treatment": {
        "text": "Extends coverage for overseas medical treatment.",
        "standalone": True,
        "triggers": ["frequent_travel", "dual_citizenship"]
    },

    # LIFE / PROTECTION
    "Critical Illness": {
        "text": "Pays lump sum on diagnosis of major critical illnesses.",
        "standalone": False,
        "triggers": ["cardio", "smoker", "bmi_high", "age_above_40"]
    },
    "Cancer Care": {
        "text": "Stage-based payout on cancer diagnosis with income support.",
        "standalone": True,
        "triggers": ["cancer", "age_above_40", "family_cancer_risk"]
    },
    "ADB": {
        "text": "Provides additional payout in case of accidental death.",
        "standalone": False,
        "triggers": ["hazardous_job", "hazardous_activities"]
    },
    "TPD": {
        "text": "Pays lump sum upon total permanent disability.",
        "standalone": False,
        "triggers": ["hazardous_job", "dependents"]
    },
    "Disability Income": {
        "text": "Pays monthly income if unable to work due to disability.",
        "standalone": True,
        "triggers": ["dependents", "high_income"]
    },
    "Income Protection": {
        "text": "Ensures income replacement during disability.",
        "standalone": True,
        "triggers": ["dependents", "high_income"]
    },
    "Premium Waiver": {
        "text": "Waives future premiums in case of disability or death.",
        "standalone": False,
        "triggers": ["dependents", "retirement_goal"]
    },

    # FAMILY
    "Child Health": {
        "text": "Provides health coverage specifically for children.",
        "standalone": False,
        "triggers": ["dependents"]
    },
    "Spouse Benefit": {
        "text": "Provides coverage or benefit for spouse.",
        "standalone": False,
        "triggers": ["married"]
    },
    "Funeral Benefit": {
        "text": "Provides lump sum to cover funeral expenses.",
        "standalone": True,
        "triggers": ["low_income", "dependents"]
    },

    # CASH / DAILY BENEFITS
    "Hospital Cash": {
        "text": "Pays a fixed daily cash amount for hospital stays.",
        "standalone": True,
        "triggers": ["low_income", "medical_risk"]
    },

    # GROUP RIDERS
    "Group ADB": {
        "text": "Accidental death benefit under group policy.",
        "standalone": False,
        "triggers": ["group_policy"]
    },
    "Group Disability": {
        "text": "Disability benefit under employer-sponsored policy.",
        "standalone": False,
        "triggers": ["group_policy"]
    },
    "Group Critical Illness": {
        "text": "Critical illness coverage under group scheme.",
        "standalone": False,
        "triggers": ["group_policy"]
    },
    "Group Hospital Cash": {
        "text": "Hospital cash benefit for group policy members.",
        "standalone": False,
        "triggers": ["group_policy"]
    }
}
