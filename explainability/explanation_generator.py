"""
Natural language explanation generator for recommendations.
Creates human-readable explanations from scoring breakdowns.
"""


class ExplanationGenerator:
    """
    Generate clear, user-friendly explanations for recommendations.
    Uses rule-based templates to explain why items were recommended.
    """
    
    def generate_policy_explanation(self, policy_name, scores, features, user):
        """
        Generate comprehensive explanation for why a policy was recommended.
        
        Args:
            policy_name: Name of recommended policy
            scores: Score breakdown dict
            features: User features dict
            user: Raw user dict
        
        Returns:
            dict: Structured explanation with reasons, factors, and concerns
        """
        explanation = {
            'recommendation': policy_name,
            'confidence': scores['final_score'],
            'confidence_level': self._get_confidence_level(scores['final_score']),
            'primary_reasons': [],
            'supporting_factors': [],
            'concerns': [],
            'component_scores': scores['components']
        }
        
        # Extract component breakdowns
        rule_breakdown = scores['components'].get('rule_breakdown', {})
        financial_breakdown = scores['components'].get('financial_breakdown', {})
        
        # PRIMARY REASONS (strongest matches)
        
        # Goal alignment
        if rule_breakdown.get('goal_alignment', 0) >= 0.8:
            explanation['primary_reasons'].append(
                f"Perfect match for your primary goal: {features['primary_goal']}"
            )
        elif rule_breakdown.get('goal_alignment', 0) >= 0.5:
            explanation['primary_reasons'].append(
                f"Aligns with your secondary goal: {features.get('secondary_goal', 'N/A')}"
            )
        
        # Age fit
        if rule_breakdown.get('age_fit', 0) >= 0.9:
            explanation['primary_reasons'].append(
                f"Ideal age fit for {features['age']} years old"
            )
        elif rule_breakdown.get('age_fit', 0) >= 0.7:
            explanation['primary_reasons'].append(
                f"Good age match for your profile ({features['age']} years)"
            )
        
        # NLP semantic match
        nlp_score = scores['components'].get('nlp_score', 0)
        if nlp_score >= 0.75:
            explanation['primary_reasons'].append(
                f"Strong semantic alignment ({nlp_score:.1%}) with your profile and needs"
            )
        elif nlp_score >= 0.65:
            explanation['primary_reasons'].append(
                f"Good match ({nlp_score:.1%}) based on profile analysis"
            )
        
        # SUPPORTING FACTORS
        
        # Income fit
        if rule_breakdown.get('income_fit', 0) >= 0.9:
            explanation['supporting_factors'].append(
                f"Designed for your {features['income_band']} income bracket"
            )
        
        # Employment fit
        if rule_breakdown.get('employment_fit', 0) >= 0.9:
            explanation['supporting_factors'].append(
                f"Suitable for {features['employment_type']} employment type"
            )
        
        # Family protection
        if features['dependents'] and 'protection' in policy_name.lower() or 'life' in policy_name.lower():
            explanation['supporting_factors'].append(
                f"Provides protection for your {features['dependents_count']} dependent(s)"
            )
        
        # Medical eligibility
        if rule_breakdown.get('medical_eligibility', 0) >= 0.8:
            explanation['supporting_factors'].append(
                f"Accepts your medical risk profile ({features['medical_risk']} risk)"
            )
        
        # Affordability
        fin_status = financial_breakdown.get('status', 'moderate')
        if fin_status in ['highly_affordable', 'affordable']:
            explanation['supporting_factors'].append(
                f"Financially suitable - estimated premium is {fin_status}"
            )
        
        # CONCERNS (potential issues)
        
        # Medical concerns
        if rule_breakdown.get('medical_eligibility', 0) < 0.6:
            explanation['concerns'].append(
                "May require additional medical underwriting due to health conditions"
            )
        
        # Financial concerns
        if fin_status in ['moderate', 'expensive']:
            est_premium = financial_breakdown.get('estimated_premium', 0)
            explanation['concerns'].append(
                f"Premium may be at higher end of budget (estimated: Rs. {est_premium:,.0f}/month)"
            )
        
        # Age concerns
        if rule_breakdown.get('age_fit', 0) < 0.5:
            explanation['concerns'].append(
                "Age is outside optimal range - may have higher premiums or limited coverage"
            )
        
        return explanation
    
    def generate_rider_explanation(self, rider_name, scores, features, coverage_gap=None):
        """
        Generate explanation for why a rider is recommended.
        
        Args:
            rider_name: Name of the rider
            scores: Score breakdown dict
            features: User features dict
            coverage_gap: Set of coverage gaps this rider fills (optional)
        
        Returns:
            dict: Structured rider explanation
        """
        explanation = {
            'rider': rider_name,
            'score': scores['final_score'],
            'priority': self._get_priority_level(scores['final_score']),
            'relevance_score': scores['final_score'],
            'reasons': [],
            'fills_gaps': list(coverage_gap) if coverage_gap else [],
            'component_scores': scores['components']
        }
        
        # Extract breakdowns
        trigger_breakdown = scores['components'].get('trigger_breakdown', {})
        rule_breakdown = scores['components'].get('rule_breakdown', {})
        
        # TRIGGER-BASED REASONS
        matched_triggers = trigger_breakdown.get('matched_triggers', [])
        
        trigger_explanations = {
            'dependents': f"You have {features['dependents_count']} dependent(s) who need protection",
            'married': "Provides coverage for your spouse",
            'hazardous_job': "Your occupation involves hazardous activities",
            'hazardous_activities': "Your work activities carry elevated risk",
            'any_medical': "Your medical history indicates need for additional coverage",
            'age_above_40': "Age-related health risks increase after 40",
            'age_above_45': "Important coverage milestone at your age",
            'smoker': "Smoking increases health risks significantly",
            'chronic': "Chronic conditions require ongoing coverage",
            'cardio': "Cardiovascular issues need specialized protection",
            'cancer': "Cancer history requires comprehensive coverage",
            'bmi_high': "Elevated BMI increases health risk factors",
            'female_childbearing_age': "Relevant for your age and family planning stage",
            'group_policy': "Available as part of your employer's group scheme",
            'frequent_travel': "Provides coverage for international travel",
            'low_income': "Affordable option for budget-conscious planning",
            'high_income': "Premium coverage suited to your income level"
        }
        
        for trigger in matched_triggers:
            if trigger in trigger_explanations:
                explanation['reasons'].append(trigger_explanations[trigger])
        
        # NLP-BASED REASON
        nlp_score = scores['components'].get('nlp_score', 0)
        if nlp_score >= 0.65:
            explanation['reasons'].append(
                f"Strong relevance match ({nlp_score:.1%}) based on your profile needs"
            )
        
        # COVERAGE GAP REASON
        if coverage_gap:
            from data.coverage_mapping import RISK_TYPES
            gap_names = [RISK_TYPES.get(g, g) for g in coverage_gap]
            explanation['reasons'].append(
                f"Fills critical coverage gap: {', '.join(gap_names)}"
            )
        
        # RULE-BASED REASONS
        if rule_breakdown.get('medical_relevance', 0) >= 0.8:
            explanation['reasons'].append(
                "Medically relevant given your health profile"
            )
        
        if rule_breakdown.get('family_relevance', 0) >= 0.8:
            explanation['reasons'].append(
                "Provides important family protection benefits"
            )
        
        # If no specific reasons, add generic based on score
        if not explanation['reasons']:
            if scores['final_score'] >= 0.6:
                explanation['reasons'].append(
                    "Generally beneficial addition to your coverage"
                )
            else:
                explanation['reasons'].append(
                    "Optional coverage - consider based on personal preference"
                )
        
        return explanation
    
    def format_policy_explanation_text(self, explanation):
        """
        Convert policy explanation dict to formatted text.
        
        Args:
            explanation: Dict from generate_policy_explanation
        
        Returns:
            str: Formatted explanation text
        """
        text = f"\n{'='*70}\n"
        text += f"RECOMMENDED POLICY: {explanation['recommendation']}\n"
        text += f"{'='*70}\n"
        text += f"Confidence: {explanation['confidence']:.1%} ({explanation['confidence_level']})\n"
        text += f"\n"
        
        if explanation['primary_reasons']:
            text += "WHY THIS POLICY?\n"
            text += "-" * 70 + "\n"
            for i, reason in enumerate(explanation['primary_reasons'], 1):
                text += f"  {i}. {reason}\n"
            text += "\n"
        
        if explanation['supporting_factors']:
            text += "SUPPORTING FACTORS:\n"
            text += "-" * 70 + "\n"
            for factor in explanation['supporting_factors']:
                text += f"  • {factor}\n"
            text += "\n"
        
        if explanation['concerns']:
            text += "CONSIDERATIONS:\n"
            text += "-" * 70 + "\n"
            for concern in explanation['concerns']:
                text += f"  ⚠  {concern}\n"
            text += "\n"
        
        # Component scores
        text += "COMPONENT SCORES:\n"
        text += "-" * 70 + "\n"
        components = explanation['component_scores']
        text += f"  Rule Match:          {components.get('rule_score', 0):.1%}\n"
        text += f"  Semantic Similarity: {components.get('nlp_score', 0):.1%}\n"
        text += f"  Financial Fit:       {components.get('financial_score', 0):.1%}\n"
        
        return text
    
    def format_rider_explanation_text(self, explanation):
        """
        Convert rider explanation dict to formatted text.
        
        Args:
            explanation: Dict from generate_rider_explanation
        
        Returns:
            str: Formatted explanation text
        """
        text = f"\n{explanation['rider']}\n"
        text += f"{'-' * len(explanation['rider'])}\n"
        text += f"Priority: {explanation['priority']} | Relevance: {explanation['relevance_score']:.1%}\n"
        
        if explanation['fills_gaps']:
            text += f"Fills Coverage Gaps: {', '.join(explanation['fills_gaps'])}\n"
        
        text += "\nReasons:\n"
        for reason in explanation['reasons']:
            text += f"  • {reason}\n"
        
        return text
    
    def format_rider_list(self, rider_explanations, title="RECOMMENDED RIDERS"):
        """
        Format multiple rider explanations into a list.
        
        Args:
            rider_explanations: List of rider explanation dicts
            title: Section title
        
        Returns:
            str: Formatted rider list
        """
        text = f"\n{'='*70}\n"
        text += f"{title}\n"
        text += f"{'='*70}\n"
        
        for explanation in rider_explanations:
            text += self.format_rider_explanation_text(explanation)
            text += "\n"
        
        return text
    
    def _get_confidence_level(self, score):
        """Convert numeric score to confidence level text."""
        if score >= 0.85:
            return "Very High"
        elif score >= 0.70:
            return "High"
        elif score >= 0.55:
            return "Moderate"
        else:
            return "Low"
    
    def _get_priority_level(self, score):
        """Convert numeric score to priority level text."""
        if score >= 0.70:
            return "High"
        elif score >= 0.50:
            return "Medium"
        else:
            return "Low"
    
    def generate_alternatives_explanation(self, rejected_policies, reason="lower score"):
        """
        Explain why alternative policies were not selected.
        
        Args:
            rejected_policies: List of (policy_name, score) tuples
            reason: General reason for rejection
        
        Returns:
            str: Formatted explanation of alternatives
        """
        text = f"\n{'='*70}\n"
        text += "ALTERNATIVE POLICIES CONSIDERED\n"
        text += f"{'='*70}\n"
        
        for policy_name, score in rejected_policies[:3]:  # Show top 3
            text += f"\n{policy_name} (Score: {score:.1%})\n"
            text += f"  Not selected due to {reason}\n"
        
        return text
