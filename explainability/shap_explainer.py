"""
SHAP-based explainability for recommendation scores.
Provides feature importance analysis for transparent recommendations.
"""

import numpy as np


class RecommendationExplainer:
    """
    Generate SHAP-like explanations for recommendation scores.
    Analyzes feature contributions to final recommendation scores.
    """
    
    def __init__(self, ensemble_scorer=None):
        """
        Initialize explainer with optional ensemble scorer reference.
        
        Args:
            ensemble_scorer: EnsembleScorer instance
        """
        self.scorer = ensemble_scorer
    
    def create_feature_vector(self, user, features, scores):
        """
        Convert user profile and scores into numeric feature vector for SHAP analysis.
        
        Args:
            user: Raw user dict
            features: Derived features dict
            scores: Score breakdown dict
        
        Returns:
            np.array: Feature vector for SHAP analysis
        """
        # Normalize all features to 0-1 scale for consistent SHAP values
        feature_vec = [
            features['age'] / 100,  # Age normalized
            self._encode_income(features['income_band']),
            1.0 if features['dependents'] else 0.0,
            features['dependents_count'] / 5,  # Normalize to 0-1 (max 5 dependents)
            1.0 if features['hazardous_job'] else 0.0,
            1.0 if features['any_medical'] else 0.0,
            1.0 if features['smoker'] else 0.0,
            features['bmi'] / 50,  # Normalize BMI
            1.0 if features['married'] else 0.0,
            1.0 if features['age_above_40'] else 0.0,
            1.0 if features['chronic'] else 0.0,
            1.0 if features['cardio'] else 0.0,
            scores.get('rule_score', 0.5),
            scores.get('nlp_score', 0.5),
            scores.get('trigger_score', 0.5),
            scores.get('financial_score', 0.5)
        ]
        
        return np.array(feature_vec)
    
    def get_feature_names(self):
        """
        Get human-readable names for all features.
        
        Returns:
            list: Feature names corresponding to feature vector
        """
        return [
            'Age',
            'Income Level',
            'Has Dependents',
            'Number of Dependents',
            'Hazardous Job',
            'Medical Conditions',
            'Smoker',
            'BMI',
            'Married',
            'Age Above 40',
            'Chronic Disease',
            'Cardiovascular',
            'Rule Match Score',
            'Semantic Similarity',
            'Trigger Match',
            'Affordability'
        ]
    
    def compute_shap_values(self, feature_vector, scores, weights):
        """
        Compute SHAP-like contribution values for each feature.
        This is a simplified attribution method based on component scores.
        
        Args:
            feature_vector: Normalized feature vector
            scores: Score breakdown dict
            weights: Ensemble weights dict
        
        Returns:
            np.array: Contribution values for each feature
        """
        # Initialize contributions
        contributions = np.zeros(len(feature_vector))
        
        # Age contribution (affects rule score and financial score)
        age_weight = weights.get('rule', 0.35) * 0.25 + weights.get('financial', 0.10) * 0.3
        contributions[0] = (feature_vector[0] - 0.45) * age_weight  # 45 is baseline age
        
        # Income contribution (affects rule and financial)
        income_weight = weights.get('rule', 0.35) * 0.20 + weights.get('financial', 0.10) * 0.7
        contributions[1] = (feature_vector[1] - 0.5) * income_weight
        
        # Dependents contribution
        dep_weight = weights.get('rule', 0.35) * 0.15 + weights.get('trigger', 0.20) * 0.3
        contributions[2] = feature_vector[2] * dep_weight * 0.5
        contributions[3] = feature_vector[3] * dep_weight * 0.3
        
        # Hazardous job contribution
        hazard_weight = weights.get('trigger', 0.20) * 0.2
        contributions[4] = feature_vector[4] * hazard_weight * 0.3
        
        # Medical conditions contribution
        medical_weight = weights.get('rule', 0.35) * 0.10 + weights.get('trigger', 0.20) * 0.4
        contributions[5] = feature_vector[5] * medical_weight * 0.4
        contributions[10] = feature_vector[10] * medical_weight * 0.25  # Chronic
        contributions[11] = feature_vector[11] * medical_weight * 0.25  # Cardio
        
        # Lifestyle factors
        lifestyle_weight = weights.get('financial', 0.10) * 0.2 + weights.get('rule', 0.35) * 0.05
        contributions[6] = feature_vector[6] * lifestyle_weight * 0.3  # Smoker
        contributions[7] = (feature_vector[7] - 0.5) * lifestyle_weight * 0.2  # BMI
        
        # Marital status
        contributions[8] = feature_vector[8] * weights.get('rule', 0.35) * 0.1
        
        # Age milestone
        contributions[9] = feature_vector[9] * weights.get('trigger', 0.20) * 0.3
        
        # Component scores direct contributions
        rule_score = scores.get('rule_score', 0.5)
        contributions[12] = (rule_score - 0.5) * weights.get('rule', 0.35)
        
        nlp_score = scores.get('nlp_score', 0.5)
        contributions[13] = (nlp_score - 0.5) * weights.get('nlp', 0.35)
        
        trigger_score = scores.get('trigger_score', 0.5)
        contributions[14] = (trigger_score - 0.5) * weights.get('trigger', 0.20)
        
        financial_score = scores.get('financial_score', 0.5)
        contributions[15] = (financial_score - 0.5) * weights.get('financial', 0.10)
        
        return contributions
    
    def explain_recommendation(self, user, features, recommendation_scores):
        """
        Generate comprehensive SHAP explanation for a recommendation.
        
        Args:
            user: Raw user dict
            features: Derived features dict
            recommendation_scores: Score dict with components and final_score
        
        Returns:
            dict: Explanation with SHAP values, feature names, and scores
        """
        # Extract components
        components = recommendation_scores.get('components', {})
        weights = recommendation_scores.get('weights', {})
        
        # Create feature vector
        feature_vector = self.create_feature_vector(user, features, components)
        
        # Compute SHAP values
        shap_values = self.compute_shap_values(feature_vector, components, weights)
        
        # Baseline (neutral) score
        base_value = 0.5
        
        # Get feature names
        feature_names = self.get_feature_names()
        
        # Identify top positive and negative contributors
        top_positive, top_negative = self._get_top_contributors(
            feature_names, shap_values, feature_vector
        )
        
        return {
            'base_value': base_value,
            'shap_values': shap_values,
            'feature_names': feature_names,
            'feature_values': feature_vector,
            'final_score': recommendation_scores['final_score'],
            'top_positive_contributors': top_positive,
            'top_negative_contributors': top_negative,
            'component_scores': components
        }
    
    def _encode_income(self, income_band):
        """Encode income band to 0-1 scale."""
        mapping = {"Low": 0.2, "Mid": 0.5, "High": 0.9}
        return mapping.get(income_band, 0.5)
    
    def _get_top_contributors(self, feature_names, shap_values, feature_values, top_n=5):
        """
        Identify top positive and negative feature contributors.
        
        Returns:
            tuple: (top_positive, top_negative) lists of dicts
        """
        # Create list of (name, shap_value, feature_value) tuples
        contributions = [
            {
                'feature': name,
                'contribution': float(shap_val),
                'value': float(feat_val)
            }
            for name, shap_val, feat_val in zip(feature_names, shap_values, feature_values)
        ]
        
        # Sort by contribution
        positive = sorted(
            [c for c in contributions if c['contribution'] > 0.01],
            key=lambda x: x['contribution'],
            reverse=True
        )[:top_n]
        
        negative = sorted(
            [c for c in contributions if c['contribution'] < -0.01],
            key=lambda x: x['contribution']
        )[:top_n]
        
        return positive, negative
    
    def generate_explanation_summary(self, explanation):
        """
        Generate text summary of SHAP explanation.
        
        Args:
            explanation: Dict from explain_recommendation
        
        Returns:
            str: Human-readable explanation summary
        """
        summary = "\nFEATURE CONTRIBUTION ANALYSIS\n"
        summary += "="*60 + "\n"
        summary += f"Base Score: {explanation['base_value']:.3f}\n"
        summary += f"Final Score: {explanation['final_score']:.3f}\n"
        summary += f"Net Contribution: {explanation['final_score'] - explanation['base_value']:+.3f}\n\n"
        
        # Top positive contributors
        if explanation['top_positive_contributors']:
            summary += "TOP POSITIVE FACTORS:\n"
            for contrib in explanation['top_positive_contributors']:
                summary += f"  + {contrib['feature']}: {contrib['contribution']:+.3f} (value: {contrib['value']:.2f})\n"
            summary += "\n"
        
        # Top negative contributors
        if explanation['top_negative_contributors']:
            summary += "TOP NEGATIVE FACTORS:\n"
            for contrib in explanation['top_negative_contributors']:
                summary += f"  - {contrib['feature']}: {contrib['contribution']:+.3f} (value: {contrib['value']:.2f})\n"
            summary += "\n"
        
        return summary
    
    def _encode_income(self, income_band):
        """Encode income band to 0-1 scale."""
        mapping = {"Low": 0.2, "Mid": 0.5, "High": 0.9}
        return mapping.get(income_band, 0.5)
