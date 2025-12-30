POLICIES = {
    "FlexLife": {
        "text": """
        Hybrid life insurance combining investment and protection.
        Short premium payment terms with long coverage.
        Provides liquidity through partial withdrawals and top-ups.
        Suitable for stable income earners seeking savings and flexibility.
        """,
        "age_range": (25, 60),
        "income_band": ["Mid", "High"],
        "goals": ["Savings", "Stable income", "Retirement with liquidity"],
        "employment_types": ["Permanent", "Self-Employed"],
        "attachable_riders": [
            "Hospitalisation", "Critical Illness", "TPD", "ADB",
            "Spouse Benefit", "Child Health",
            "Income Protection", "Premium Waiver"
        ]
    },

    "Life+": {
        "text": """
        Protection-focused life insurance.
        Designed for family protection and income replacement.
        Highly customizable with a wide range of riders.
        """,
        "age_range": (18, 65),
        "income_band": ["Low", "Mid", "High"],
        "goals": ["Family protection", "Income replacement"],
        "employment_types": ["Permanent", "Self-Employed", "Contract"],
        "attachable_riders": [
            "Hospital Cash", "Critical Illness", "Surgery Benefit",
            "Disability Income", "ADB", "Child Health",
            "Spouse Benefit", "Funeral Benefit"
        ]
    },

    "Health360": {
        "text": """
        Comprehensive health insurance with high annual limits.
        Covers hospitalization, surgery, ICU, and overseas treatment.
        Suitable for individuals and families with medical risk.
        """,
        "age_range": (0, 80),
        "income_band": ["Low", "Mid", "High"],
        "goals": ["Medical coverage"],
        "employment_types": ["Any"],
        "attachable_riders": [
            "OPD", "Maternity", "Organ Transplant",
            "Overseas Treatment", "Chronic Medication"
        ]
    },

    "Pension Advantage": {
        "text": """
        Retirement-focused pension plan.
        Accumulates retirement income with premium waiver on disability.
        Can integrate health coverage during accumulation phase.
        """,
        "age_range": (40, 65),
        "income_band": ["Mid", "High"],
        "goals": ["Retirement"],
        "employment_types": ["Permanent", "Self-Employed"],
        "attachable_riders": [
            "Health360 Add-on", "Critical Illness", "Premium Waiver"
        ]
    },

    "ClickLife": {
        "text": """
        Simple digital life insurance.
        Paperless onboarding with quick approval.
        Designed for young and healthy individuals.
        """,
        "age_range": (18, 40),
        "income_band": ["Low", "Mid"],
        "goals": ["Simple life cover", "Cheap & quick"],
        "employment_types": ["Any"],
        "attachable_riders": [
            "ADB", "Cancer Care"
        ]
    },

    "Union Protect": {
        "text": """
        Group life insurance scheme for employees or members.
        Employer-sponsored master policy with simplified underwriting.
        Provides affordable base life cover with optional group riders.
        """,
        "age_range": (18, 65),
        "income_band": ["Low", "Mid", "High"],
        "goals": ["Employer benefits", "Group coverage"],
        "employment_types": ["Permanent"],
        "requires_employer": True,
        "attachable_riders": [
            "Group ADB", "Group Disability",
            "Group Critical Illness", "Group Hospital Cash"
        ]
    }
}
