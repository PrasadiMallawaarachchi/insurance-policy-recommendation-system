"""
Enhanced recommendation system with ensemble scoring and explainability.
Combines rule-based filtering with NLP similarity and provides transparent explanations.
"""

from features.feature_engineering import derive_features
from nlp.embedding import EmbeddingEngine
from nlp.text_builders import build_user_text
from rules.policy_filter import filter_policies
from rules.rider_filter import filter_riders
from data.policies import POLICIES
from data.riders import RIDERS
from scoring.ensemble_scorer import EnsembleScorer
from analysis.coverage_gaps import (
    identify_user_risks,
    find_coverage_gaps,
    prioritize_riders_for_gaps,
    analyze_coverage_completeness,
    get_coverage_summary_text
)
from data.coverage_mapping import get_policy_coverage
from explainability.shap_explainer import RecommendationExplainer
from explainability.explanation_generator import ExplanationGenerator


def recommend(user, explain=True, top_riders=10):
    """
    Generate comprehensive insurance recommendations with explanations.
    
    Args:
        user: User profile dict
        explain: Whether to generate detailed explanations (default: True)
        top_riders: Maximum number of riders to return (default: 10)
    
    Returns:
        dict: Comprehensive recommendation results including:
            - policy: Best policy name
            - policy_score: Final policy score
            - policy_explanation: Detailed explanation (if explain=True)
            - primary_riders: High-priority riders (score >= 0.65)
            - alternate_riders: Medium-priority riders (0.45 <= score < 0.65)
            - rider_explanations: Detailed rider explanations (if explain=True)
            - coverage_analysis: Coverage gaps and completeness
            - all_policy_scores: Scores for all candidate policies (if explain=True)
    """
    # Phase 1: Feature Engineering
    features = derive_features(user)

    # Phase 2: Text Generation and Embeddings
    embedder = EmbeddingEngine()
    user_text = build_user_text(user, features)
    user_vec = embedder.encode([user_text])[0]

    # Phase 3: Filter Eligible Policies
    candidate_policies = filter_policies(user, features)
    
    if not candidate_policies:
        # No exact match found; attempt a relaxed pass that ignores "goal" matching
        # This helps when medical risk is high (e.g., cancer) but the user's primary
        # goal doesn't directly map to medical policies. We still enforce age,
        # income, employment and policy-specific medical constraints.
        relaxed_candidates = []
        for policy_name, policy in POLICIES.items():
            # Age eligibility
            min_age, max_age = policy["age_range"]
            if not (min_age <= features["age"] <= max_age):
                continue

            # Income band check
            if features["income_band"] not in policy["income_band"]:
                continue

            # Employment type check
            if policy.get("employment_types") and "Any" not in policy["employment_types"]:
                if features["employment_type"] not in policy["employment_types"]:
                    continue

            # Policy-specific medical filters (keep these restrictions)
            if policy_name == "ClickLife" and features["medical_risk"] != "Low":
                continue

            if policy_name == "FlexLife" and features["medical_risk"] == "Very High":
                continue

            # Requires employer
            if policy.get("requires_employer") and not features.get("group_policy"):
                continue

            # If we passed these checks, add as a relaxed candidate (ignore goals)
            relaxed_candidates.append(policy_name)

        if relaxed_candidates:
            candidate_policies = relaxed_candidates
        else:
            return {
                'error': 'No eligible policies found for this user profile',
                'user_risks': identify_user_risks(user, features)
            }

    # Phase 4: Ensemble Scoring for Policies
    ensemble_scorer = EnsembleScorer()
    policy_scores = {}
    
    for policy_name in candidate_policies:
        policy_data = POLICIES[policy_name]
        scores = ensemble_scorer.score_policy(
            user, features, policy_name, policy_data, user_vec, embedder
        )
        policy_scores[policy_name] = scores
    
    # Rank policies by final score
    ranked_policies = sorted(
        policy_scores.items(),
        key=lambda x: x[1]['final_score'],
        reverse=True
    )
    
    best_policy_name, best_policy_scores = ranked_policies[0]
    best_policy_data = POLICIES[best_policy_name]

    # Phase 5: Coverage Gap Analysis
    user_risks = identify_user_risks(user, features)
    policy_coverage = get_policy_coverage(best_policy_name)
    coverage_gaps = find_coverage_gaps(user_risks, policy_coverage)

    # Phase 6: Filter and Score Riders
    eligible_riders = filter_riders(best_policy_name, best_policy_data, features)
    
    if not eligible_riders:
        rider_scores = {}
    else:
        rider_scores = ensemble_scorer.batch_score_riders(
            user, features, eligible_riders, RIDERS, user_vec, embedder
        )
    
    # Phase 7: Prioritize Gap-Filling Riders
    if coverage_gaps and eligible_riders:
        gap_fillers = prioritize_riders_for_gaps(coverage_gaps, eligible_riders, RIDERS)
        
        # Boost scores for gap-filling riders
        for gap_filler in gap_fillers:
            rider_name = gap_filler['rider_name']
            if rider_name in rider_scores:
                # Add bonus for filling gaps (up to 0.15 bonus)
                gap_bonus = min(gap_filler['priority_score'] * 0.05, 0.15)
                rider_scores[rider_name]['final_score'] = min(
                    rider_scores[rider_name]['final_score'] + gap_bonus,
                    1.0
                )
                rider_scores[rider_name]['fills_gaps'] = gap_filler['filled_gaps']
                rider_scores[rider_name]['gap_priority'] = gap_filler['priority_score']

    # Phase 8: Separate Primary vs Alternate Riders
    primary_riders = []
    alternate_riders = []
    
    for rider_name, scores in rider_scores.items():
        if scores['final_score'] >= 0.65:
            primary_riders.append((rider_name, scores))
        elif scores['final_score'] >= 0.45:
            alternate_riders.append((rider_name, scores))
    
    # Sort by score
    primary_riders.sort(key=lambda x: x[1]['final_score'], reverse=True)
    alternate_riders.sort(key=lambda x: x[1]['final_score'], reverse=True)
    
    # Limit to top_riders
    primary_riders = primary_riders[:top_riders]
    alternate_riders = alternate_riders[:top_riders]

    # Phase 9: Generate Explanations (if requested)
    result = {
        'policy': best_policy_name,
        'policy_score': best_policy_scores['final_score'],
        'primary_riders': primary_riders,
        'alternate_riders': alternate_riders,
        'coverage_gaps': list(coverage_gaps),
        'user_risks': list(user_risks)
    }
    
    if explain:
        explainer = RecommendationExplainer(ensemble_scorer)
        exp_generator = ExplanationGenerator()
        
        # Explain policy recommendation
        policy_shap = explainer.explain_recommendation(user, features, best_policy_scores)
        policy_explanation = exp_generator.generate_policy_explanation(
            best_policy_name, best_policy_scores, features, user
        )
        
        result['policy_explanation'] = policy_explanation
        result['policy_shap'] = policy_shap
        
        # Explain top primary riders
        rider_explanations = []
        for rider_name, scores in primary_riders[:5]:  # Top 5 explanations
            filled_gaps = scores.get('fills_gaps', set())
            rider_exp = exp_generator.generate_rider_explanation(
                rider_name, scores, features, filled_gaps
            )
            rider_explanations.append(rider_exp)
        
        result['rider_explanations'] = rider_explanations
        
        # Coverage analysis
        coverage_analysis = analyze_coverage_completeness(
            user, features, best_policy_name, 
            [r[0] for r in primary_riders]
        )
        result['coverage_analysis'] = coverage_analysis
        
        # All policy scores for comparison
        result['all_policy_scores'] = policy_scores

        print("Generated explanations for policy and riders.")
    
    return result


# Backward compatibility function
def recommend_simple(user):
    """
    Simple recommendation function for backward compatibility.
    Returns only policy name and ranked riders (old format).
    
    Args:
        user: User profile dict
    
    Returns:
        tuple: (best_policy_name, list of (rider_name, score) tuples)
    """
    result = recommend(user, explain=False)
    
    if 'error' in result:
        return None, []
    
    # Combine primary and alternate riders
    all_riders = result['primary_riders'] + result['alternate_riders']
    
    # Convert to simple (name, score) tuples
    simple_riders = [(name, scores['final_score']) for name, scores in all_riders]
    
    return result['policy'], simple_riders
