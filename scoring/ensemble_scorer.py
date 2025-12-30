"""
Ensemble scorer that combines multiple scoring components for recommendation.
Integrates rule-based, NLP similarity, trigger strength, and financial fit scores.
"""

import numpy as np
from scoring.component_scorers import (
    rule_based_score_policy,
    rule_based_score_rider,
    trigger_strength_score,
    financial_fit_score,
    estimate_policy_premium_percentage,
    estimate_rider_premium_percentage
)


class EnsembleScorer:
    """
    Combines multiple scoring methods into a weighted ensemble.
    Provides transparent breakdown of component scores for explainability.
    """
    
    def __init__(self, weights=None):
        """
        Initialize ensemble scorer with component weights.
        
        Args:
            weights: Dict with keys: 'rule', 'nlp', 'trigger', 'financial'
                    Default: {'rule': 0.35, 'nlp': 0.35, 'trigger': 0.20, 'financial': 0.10}
        """
        self.weights = weights or {
            'rule': 0.35,
            'nlp': 0.35,
            'trigger': 0.00,  # Not used for policies
            'financial': 0.30
        }
        
        self.rider_weights = {
            'rule': 0.30,
            'nlp': 0.35,
            'trigger': 0.25,
            'financial': 0.10
        }
    
    def compute_nlp_similarity(self, user_vec, item_text, embedder):
        """
        Compute cosine similarity between user and policy/rider text.
        
        Args:
            user_vec: User embedding vector
            item_text: Policy or rider text description
            embedder: EmbeddingEngine instance
        
        Returns:
            float: Cosine similarity score (0-1)
        """
        item_vec = embedder.encode([item_text])[0]
        similarity = np.dot(user_vec, item_vec)
        return float(similarity)
    
    def score_policy(self, user, features, policy_name, policy_data, user_vec, embedder):
        """
        Generate comprehensive ensemble score for a policy.
        
        Args:
            user: Raw user dict
            features: Derived features dict
            policy_name: Name of the policy
            policy_data: Policy configuration dict
            user_vec: User embedding vector
            embedder: EmbeddingEngine instance
        
        Returns:
            dict: Contains final_score and detailed component breakdown
        """
        # Component 1: Rule-based score
        rule_score, rule_breakdown = rule_based_score_policy(user, features, policy_data)
        
        # Component 2: NLP similarity score
        nlp_score = self.compute_nlp_similarity(user_vec, policy_data["text"], embedder)
        
        # Component 3: Financial fit score
        premium_pct = estimate_policy_premium_percentage(policy_name, features)
        financial_score, fin_breakdown = financial_fit_score(user["monthly_income"], premium_pct)
        
        # Calculate weighted ensemble score
        final_score = (
            self.weights['rule'] * rule_score +
            self.weights['nlp'] * nlp_score +
            self.weights['financial'] * financial_score
        )
        
        # Return comprehensive breakdown for explainability
        return {
            'final_score': final_score,
            'components': {
                'rule_score': rule_score,
                'nlp_score': nlp_score,
                'financial_score': financial_score,
                'rule_breakdown': rule_breakdown,
                'financial_breakdown': fin_breakdown
            },
            'weights': self.weights,
            'policy_name': policy_name
        }
    
    def score_rider(self, user, features, rider_name, rider_data, user_vec, embedder):
        """
        Generate comprehensive ensemble score for a rider.
        
        Args:
            user: Raw user dict
            features: Derived features dict
            rider_name: Name of the rider
            rider_data: Rider configuration dict
            user_vec: User embedding vector
            embedder: EmbeddingEngine instance
        
        Returns:
            dict: Contains final_score and detailed component breakdown
        """
        # Component 1: Rule-based score (includes trigger matching)
        rule_score, rule_breakdown = rule_based_score_rider(user, features, rider_data)
        
        # Component 2: NLP similarity score
        nlp_score = self.compute_nlp_similarity(user_vec, rider_data["text"], embedder)
        
        # Component 3: Trigger strength score (explicit)
        triggers = rider_data.get("triggers", [])
        trigger_score, trigger_breakdown = trigger_strength_score(features, triggers)
        
        # Component 4: Financial fit score (riders add cost)
        rider_premium_pct = estimate_rider_premium_percentage(rider_name)
        financial_score, fin_breakdown = financial_fit_score(user["monthly_income"], rider_premium_pct)
        
        # Calculate weighted ensemble score
        final_score = (
            self.rider_weights['rule'] * rule_score +
            self.rider_weights['nlp'] * nlp_score +
            self.rider_weights['trigger'] * trigger_score +
            self.rider_weights['financial'] * financial_score
        )
        
        # Return comprehensive breakdown
        return {
            'final_score': final_score,
            'components': {
                'rule_score': rule_score,
                'nlp_score': nlp_score,
                'trigger_score': trigger_score,
                'financial_score': financial_score,
                'rule_breakdown': rule_breakdown,
                'trigger_breakdown': trigger_breakdown,
                'financial_breakdown': fin_breakdown
            },
            'weights': self.rider_weights,
            'rider_name': rider_name
        }
    
    def batch_score_policies(self, user, features, policy_names, policies_data, user_vec, embedder):
        """
        Score multiple policies at once.
        
        Returns:
            dict: Policy names mapped to their scores
        """
        scores = {}
        for policy_name in policy_names:
            policy_data = policies_data[policy_name]
            scores[policy_name] = self.score_policy(
                user, features, policy_name, policy_data, user_vec, embedder
            )
        return scores
    
    def batch_score_riders(self, user, features, rider_names, riders_data, user_vec, embedder):
        """
        Score multiple riders at once.
        
        Returns:
            dict: Rider names mapped to their scores
        """
        scores = {}
        for rider_name in rider_names:
            rider_data = riders_data[rider_name]
            scores[rider_name] = self.score_rider(
                user, features, rider_name, rider_data, user_vec, embedder
            )
        return scores
