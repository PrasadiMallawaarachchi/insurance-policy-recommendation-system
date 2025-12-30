"""
Coverage mapping: Define risk types and map policies/riders to coverage.
Used for gap analysis to identify unmet insurance needs.
"""

# Define all possible risk types a user might face
RISK_TYPES = {
    'death': 'Death benefit / Life cover',
    'critical_illness': 'Critical illness coverage',
    'disability': 'Disability income protection',
    'hospitalization': 'Hospital expenses',
    'surgery': 'Surgical procedures',
    'chronic_care': 'Chronic disease management',
    'family_protection': 'Family income protection',
    'retirement': 'Retirement income',
    'outpatient': 'Outpatient medical care',
    'maternity': 'Maternity and childbirth',
    'accident': 'Accidental death/injury',
    'overseas_medical': 'Overseas medical treatment',
    'organ_transplant': 'Organ transplant support',
    'child_health': 'Children healthcare',
    'funeral': 'Funeral expenses'
}


# Map each policy to the risk types it covers
POLICY_COVERAGE = {
    'FlexLife': {
        'death', 
        'retirement', 
        'family_protection'
    },
    
    'Life+': {
        'death', 
        'family_protection'
    },
    
    'Health360': {
        'hospitalization', 
        'surgery', 
        'chronic_care', 
        'critical_illness',
        'family_protection'  # Can cover family members
    },
    
    'Pension Advantage': {
        'retirement', 
        'death',
        'disability'  # Has premium waiver on disability
    },
    
    'ClickLife': {
        'death'
    },
    
    'Union Protect': {
        'death', 
        'family_protection'
    }
}


# Map each rider to the risk types it covers
RIDER_COVERAGE = {
    # Medical/Health Riders
    'Hospitalisation': {
        'hospitalization', 
        'surgery'
    },
    
    'OPD': {
        'outpatient'
    },
    
    'Chronic Medication': {
        'chronic_care'
    },
    
    'Maternity': {
        'maternity'
    },
    
    'Organ Transplant': {
        'organ_transplant'
    },
    
    'Overseas Treatment': {
        'overseas_medical'
    },
    
    # Life/Protection Riders
    'Critical Illness': {
        'critical_illness'
    },
    
    'Cancer Care': {
        'critical_illness',  # Cancer is a critical illness
        'chronic_care'
    },
    
    'ADB': {
        'accident',
        'death'  # Enhanced death benefit
    },
    
    'TPD': {
        'disability'
    },
    
    'Disability Income': {
        'disability',
        'family_protection'
    },
    
    'Income Protection': {
        'disability',
        'family_protection'
    },
    
    'Premium Waiver': {
        'disability'  # Maintains coverage if disabled
    },
    
    # Family Riders
    'Child Health': {
        'child_health',
        'family_protection'
    },
    
    'Spouse Benefit': {
        'family_protection'
    },
    
    'Funeral Benefit': {
        'funeral',
        'family_protection'
    },
    
    # Cash Benefits
    'Hospital Cash': {
        'hospitalization'
    },
    
    'Surgery Benefit': {
        'surgery'
    },
    
    # Group Riders
    'Group ADB': {
        'accident',
        'death'
    },
    
    'Group Disability': {
        'disability'
    },
    
    'Group Critical Illness': {
        'critical_illness'
    },
    
    'Group Hospital Cash': {
        'hospitalization'
    }
}


def get_policy_coverage(policy_name):
    """
    Get the set of risk types covered by a policy.
    
    Args:
        policy_name: Name of the policy
    
    Returns:
        set: Risk types covered by this policy
    """
    return POLICY_COVERAGE.get(policy_name, set())


def get_rider_coverage(rider_name):
    """
    Get the set of risk types covered by a rider.
    
    Args:
        rider_name: Name of the rider
    
    Returns:
        set: Risk types covered by this rider
    """
    return RIDER_COVERAGE.get(rider_name, set())


def get_combined_coverage(policy_name, rider_names):
    """
    Get total coverage when combining a policy with riders.
    
    Args:
        policy_name: Name of the base policy
        rider_names: List of rider names
    
    Returns:
        set: All risk types covered by policy + riders
    """
    coverage = get_policy_coverage(policy_name).copy()
    
    for rider_name in rider_names:
        coverage.update(get_rider_coverage(rider_name))
    
    return coverage


def get_coverage_completeness_score(covered_risks, total_risks):
    """
    Calculate what percentage of user risks are covered.
    
    Args:
        covered_risks: Set of risks currently covered
        total_risks: Set of all risks user faces
    
    Returns:
        float: Coverage completeness (0-1)
    """
    if not total_risks:
        return 1.0
    
    coverage_ratio = len(covered_risks & total_risks) / len(total_risks)
    return coverage_ratio
