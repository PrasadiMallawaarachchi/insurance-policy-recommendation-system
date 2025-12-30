from recommender import recommend

# -------------------------------------------------
# FULL USER OBJECT (matches derive_features exactly)
# -------------------------------------------------
user = {
    # -----------------------
    # BASIC DEMOGRAPHIC
    # -----------------------
    "age_nearest_bday": 35,
    "gender": "Male",
    "marital_status": "Married",

    # -----------------------
    # LOCATION
    # -----------------------
    "nationality": "Sri Lankan",
    "country": "Sri Lanka",
    "district": "Colombo",
    "city": "Dehiwala",

    # -----------------------
    # OCCUPATION & FINANCIAL
    # -----------------------
    "occupation": "Software Engineer",
    "employment_type": "Permanent",
    "designation": "Senior Engineer",
    "hazardous_level": "Low",
    "hazardous_activities": "",

    "monthly_income": 200000,
    "existing_insurance": "Yes",
    "dependents_count": 2,

    # -----------------------
    # GOALS
    # -----------------------
    "primary_goal": "Savings",
    "secondary_goal": "Retirement with liquidity",

    # -----------------------
    # MEDICAL CONDITIONS
    # -----------------------
    "chronic_disease": False,
    "cardiovascular_health_issue": False,
    "cancer_or_tumors": False,
    "respiratory_conditions": False,
    "neurological_or_mental_health_conditions": False,
    "gastrointestinal_conditions": False,
    "musculoskeletal_conditions": False,
    "infectious_or_sexual_health_conditions": False,

    # -----------------------
    # MEDICAL HISTORY
    # -----------------------
    "recent_treatment_or_surgery": False,
    "covid19_related_conditions": False,

    # -----------------------
    # LIFESTYLE
    # -----------------------
    "bmi": 24.8,
    "smoker": "No",
    "alcohol_consumer": "Occasionally",

    # -----------------------
    # TRAVEL & REGULATORY
    # -----------------------
    "travel_history_high_risk_countries": False,
    "dual_citizenship": False,
    "tax_or_regulatory_flags": False,

    # -----------------------
    # INSURANCE HISTORY
    # -----------------------
    "insurance_history_issues": False,
    "current_insurance_status": "Active personal policy",

    # -----------------------
    # GROUP SCHEME
    # -----------------------
    "employer_scheme": True
}



# -------------------------------------------------
# RUN ENHANCED RECOMMENDER
# -------------------------------------------------
from analysis.coverage_gaps import get_coverage_summary_text
from explainability.explanation_generator import ExplanationGenerator

print("\n" + "="*80)
print("INSURANCE RECOMMENDATION SYSTEM - PHASE 2 ENHANCED")
print("="*80)

result = recommend(user, explain=True)

if 'error' in result:
    print(f"\nERROR: {result['error']}")
    exit()

# ============================================================================
# POLICY RECOMMENDATION
# ============================================================================
print("\n" + "="*80)
print("RECOMMENDED POLICY")
print("="*80)
print(f"\nPolicy: {result['policy']}")
print(f"Confidence Score: {result['policy_score']:.1%}")

# Policy Explanation
if 'policy_explanation' in result:
    exp_gen = ExplanationGenerator()
    explanation_text = exp_gen.format_policy_explanation_text(result['policy_explanation'])
    print(explanation_text)

# ============================================================================
# COVERAGE ANALYSIS
# ============================================================================
if 'coverage_analysis' in result:
    coverage_summary = get_coverage_summary_text(result['coverage_analysis'])
    print(coverage_summary)

# ============================================================================
# PRIMARY RIDERS (High Priority)
# ============================================================================
print("\n" + "="*80)
print("PRIMARY RIDERS - High Priority (Score ≥ 65%)")
print("="*80)

if result['primary_riders']:
    for rider_name, scores in result['primary_riders']:
        print(f"\n{rider_name}")
        print("-" * len(rider_name))
        print(f"  Score: {scores['final_score']:.1%}")
        
        # Show component breakdown
        components = scores['components']
        print(f"  Rule: {components.get('rule_score', 0):.1%} | " +
              f"NLP: {components.get('nlp_score', 0):.1%} | " +
              f"Trigger: {components.get('trigger_score', 0):.1%} | " +
              f"Financial: {components.get('financial_score', 0):.1%}")
        
        # Show if it fills gaps
        if 'fills_gaps' in scores:
            from data.coverage_mapping import RISK_TYPES
            gap_names = [RISK_TYPES.get(g, g) for g in scores['fills_gaps']]
            print(f"  Fills gaps: {', '.join(gap_names)}")
else:
    print("\nNo high-priority riders identified for your profile.")

# ============================================================================
# DETAILED RIDER EXPLANATIONS
# ============================================================================
if 'rider_explanations' in result and result['rider_explanations']:
    print("\n" + "="*80)
    print("DETAILED RIDER EXPLANATIONS (Top 5)")
    print("="*80)
    
    exp_gen = ExplanationGenerator()
    for rider_exp in result['rider_explanations']:
        rider_text = exp_gen.format_rider_explanation_text(rider_exp)
        print(rider_text)

# ============================================================================
# ALTERNATE RIDERS (Medium Priority)
# ============================================================================
if result['alternate_riders']:
    print("\n" + "="*80)
    print("ALTERNATE RIDERS - Consider These (Score 45-65%)")
    print("="*80)
    
    for rider_name, scores in result['alternate_riders'][:5]:  # Show top 5
        print(f"  • {rider_name} - Score: {scores['final_score']:.1%}")

# ============================================================================
# FEATURE CONTRIBUTION ANALYSIS (SHAP)
# ============================================================================
if 'policy_shap' in result:
    print("\n" + "="*80)
    print("FEATURE CONTRIBUTION ANALYSIS")
    print("="*80)
    
    from explainability.shap_explainer import RecommendationExplainer
    explainer = RecommendationExplainer()
    shap_summary = explainer.generate_explanation_summary(result['policy_shap'])
    print(shap_summary)

# ============================================================================
# POLICY COMPARISON
# ============================================================================
if 'all_policy_scores' in result:
    print("\n" + "="*80)
    print("ALL CANDIDATE POLICIES COMPARISON")
    print("="*80)
    
    sorted_policies = sorted(
        result['all_policy_scores'].items(),
        key=lambda x: x[1]['final_score'],
        reverse=True
    )
    
    for policy_name, scores in sorted_policies:
        print(f"\n{policy_name}: {scores['final_score']:.1%}")
        components = scores['components']
        print(f"  Rule: {components.get('rule_score', 0):.1%} | " +
              f"NLP: {components.get('nlp_score', 0):.1%} | " +
              f"Financial: {components.get('financial_score', 0):.1%}")

print("\n" + "="*80)
print("RECOMMENDATION COMPLETE")
print("="*80)
