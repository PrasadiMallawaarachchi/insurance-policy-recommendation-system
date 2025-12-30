"""
Coverage gap analysis: Identify unmet insurance needs and prioritize riders.
Compares user risks against policy coverage to find gaps.
"""

from data.coverage_mapping import (
    get_policy_coverage,
    get_rider_coverage,
    get_combined_coverage,
    RISK_TYPES
)


def identify_user_risks(user, features):
    """
    Identify what insurance risks a user faces based on their profile.
    
    Args:
        user: Raw user dict
        features: Derived features dict
    
    Returns:
        set: Risk types applicable to this user
    """
    risks = set()
    
    # Everyone needs death coverage
    risks.add('death')
    
    # Family protection needs
    if features['dependents'] or features['married']:
        risks.add('family_protection')
    
    # Disability coverage needs
    if features['dependents'] or features['family_responsibility']:
        risks.add('disability')
    
    # Medical/Health risks
    if features['any_medical']:
        risks.add('hospitalization')
        risks.add('surgery')
    
    if features['chronic']:
        risks.add('chronic_care')
        risks.add('outpatient')
    
    # Age-related risks
    if features['age_above_40']:
        risks.add('critical_illness')
        risks.add('hospitalization')
    
    # Critical illness risk factors
    if features['cardio'] or features['cancer'] or features['smoker'] or features['bmi_high']:
        risks.add('critical_illness')
    
    # Hazardous occupation
    if features['hazardous_job'] or features['hazardous_activities']:
        risks.add('accident')
        risks.add('disability')
    
    # Retirement planning
    if features['goal_retirement'] or features['age_above_45']:
        risks.add('retirement')
    
    # Maternity
    if features.get('female_childbearing_age'):
        risks.add('maternity')
    
    # Children healthcare
    if features['dependents']:
        risks.add('child_health')
    
    # Travel-related
    if features.get('frequent_travel') or features.get('dual_citizenship'):
        risks.add('overseas_medical')
    
    # Funeral expenses (especially for low income families)
    if features['low_income'] and features['dependents']:
        risks.add('funeral')
    
    return risks


def find_coverage_gaps(user_risks, policy_coverage):
    """
    Identify gaps between user needs and policy coverage.
    
    Args:
        user_risks: Set of risk types user faces
        policy_coverage: Set of risk types policy covers
    
    Returns:
        set: Uncovered risk types
    """
    gaps = user_risks - policy_coverage
    return gaps


def prioritize_riders_for_gaps(coverage_gaps, available_riders, riders_data):
    """
    Find riders that fill coverage gaps and prioritize them.
    
    Args:
        coverage_gaps: Set of uncovered risk types
        available_riders: List of eligible rider names
        riders_data: Dict mapping rider names to their data
    
    Returns:
        list: Tuples of (rider_name, filled_gaps, priority_score)
    """
    gap_filling_riders = []
    
    for rider_name in available_riders:
        rider_coverage = get_rider_coverage(rider_name)
        
        # Check if this rider fills any gaps
        filled_gaps = rider_coverage & coverage_gaps
        
        if filled_gaps:
            # Priority score based on number and criticality of gaps filled
            priority_score = calculate_gap_priority(filled_gaps)
            
            gap_filling_riders.append({
                'rider_name': rider_name,
                'filled_gaps': filled_gaps,
                'priority_score': priority_score
            })
    
    # Sort by priority score (highest first)
    gap_filling_riders.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return gap_filling_riders


def calculate_gap_priority(gaps):
    """
    Calculate priority score for a set of coverage gaps.
    Some gaps are more critical than others.
    
    Args:
        gaps: Set of risk type strings
    
    Returns:
        float: Priority score (higher = more critical)
    """
    # Define criticality weights for each risk type
    criticality = {
        'death': 1.0,
        'critical_illness': 0.95,
        'disability': 0.9,
        'family_protection': 0.9,
        'hospitalization': 0.85,
        'chronic_care': 0.8,
        'surgery': 0.75,
        'accident': 0.7,
        'retirement': 0.7,
        'maternity': 0.65,
        'child_health': 0.6,
        'outpatient': 0.5,
        'overseas_medical': 0.4,
        'organ_transplant': 0.4,
        'funeral': 0.3
    }
    
    # Sum criticality scores for all gaps
    priority = sum(criticality.get(gap, 0.5) for gap in gaps)
    
    return priority


def analyze_coverage_completeness(user, features, policy_name, selected_riders=None):
    """
    Analyze how complete the coverage is for a user.
    
    Args:
        user: Raw user dict
        features: Derived features dict
        policy_name: Selected policy name
        selected_riders: List of selected rider names (optional)
    
    Returns:
        dict: Analysis results including gaps, coverage ratio, recommendations
    """
    # Identify all risks user faces
    user_risks = identify_user_risks(user, features)
    
    # Get coverage from policy
    policy_coverage = get_policy_coverage(policy_name)
    
    # Get combined coverage if riders selected
    if selected_riders:
        total_coverage = get_combined_coverage(policy_name, selected_riders)
    else:
        total_coverage = policy_coverage
    
    # Find gaps
    gaps = find_coverage_gaps(user_risks, total_coverage)
    
    # Calculate coverage ratio
    if user_risks:
        coverage_ratio = len(total_coverage & user_risks) / len(user_risks)
    else:
        coverage_ratio = 1.0
    
    # Get readable risk names
    user_risk_names = [RISK_TYPES.get(r, r) for r in user_risks]
    covered_risk_names = [RISK_TYPES.get(r, r) for r in (total_coverage & user_risks)]
    gap_names = [RISK_TYPES.get(r, r) for r in gaps]
    
    return {
        'user_risks': user_risks,
        'user_risk_names': user_risk_names,
        'policy_coverage': policy_coverage,
        'total_coverage': total_coverage,
        'covered_risks': total_coverage & user_risks,
        'covered_risk_names': covered_risk_names,
        'coverage_gaps': gaps,
        'gap_names': gap_names,
        'coverage_ratio': coverage_ratio,
        'coverage_percentage': coverage_ratio * 100
    }


def get_coverage_summary_text(analysis_result):
    """
    Generate human-readable summary of coverage analysis.
    
    Args:
        analysis_result: Dict from analyze_coverage_completeness
    
    Returns:
        str: Formatted summary text
    """
    coverage_pct = analysis_result['coverage_percentage']
    
    summary = f"\nCOVERAGE ANALYSIS\n"
    summary += f"{'='*60}\n"
    summary += f"Coverage Completeness: {coverage_pct:.1f}%\n\n"
    
    summary += f"Identified Risks ({len(analysis_result['user_risks'])}):\n"
    for risk in analysis_result['user_risk_names']:
        summary += f"  • {risk}\n"
    
    summary += f"\nCovered Risks ({len(analysis_result['covered_risks'])}):\n"
    for risk in analysis_result['covered_risk_names']:
        summary += f"  ✓ {risk}\n"
    
    if analysis_result['coverage_gaps']:
        summary += f"\nCoverage Gaps ({len(analysis_result['coverage_gaps'])}):\n"
        for risk in analysis_result['gap_names']:
            summary += f"  ⚠ {risk}\n"
    else:
        summary += f"\n✓ All identified risks are covered!\n"
    
    return summary
