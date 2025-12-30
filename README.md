# Insurance Recommendation System - Phase 2 Enhanced

## Overview

Phase 2 implementation of an advanced insurance recommendation system that combines **rule-based filtering** with **NLP semantic matching** and provides **transparent explainability** through SHAP-like feature importance analysis.

## Key Features

### 1. **Hybrid Ensemble Scoring**

- **Rule-Based Scoring**: Age fit, income match, goal alignment, employment type, medical eligibility
- **NLP Semantic Similarity**: Context-aware matching using sentence transformers
- **Trigger Strength**: Feature-based trigger matching for riders
- **Financial Fit**: Affordability analysis based on income and estimated premiums

### 2. **Coverage Gap Analysis**

- Identifies user-specific insurance risks based on profile
- Maps policies and riders to coverage types
- Detects uncovered risks (coverage gaps)
- Prioritizes riders that fill critical gaps

### 3. **Explainability Layer**

- **SHAP-like feature importance**: Shows which features contributed to recommendations
- **Natural language explanations**: Human-readable reasons for each recommendation
- **Component score breakdown**: Transparent view of all scoring components
- **Confidence levels**: Clear indication of recommendation certainty

### 4. **Primary vs Alternate Riders**

- **Primary Riders**: High-priority (score ≥ 65%) - strongly recommended
- **Alternate Riders**: Medium-priority (45-65%) - optional considerations
- Gap-filling riders receive priority boost

### 5. **Visualization Support**

- SHAP waterfall plots showing feature contributions
- Component score bar charts
- Coverage completeness pie charts
- Rider priority rankings
- Policy comparison charts

## Architecture

```
User Profile
    ↓
Feature Engineering (features/feature_engineering.py)
    ↓
Text Generation (nlp/text_builders.py)
    ↓
Embedding (nlp/embedding.py)
    ↓
Rule Filtering (rules/policy_filter.py, rules/rider_filter.py)
    ↓
Ensemble Scoring (scoring/ensemble_scorer.py)
    ├── Component Scorers (scoring/component_scorers.py)
    ├── Rule Score
    ├── NLP Similarity
    ├── Trigger Strength
    └── Financial Fit
    ↓
Coverage Gap Analysis (analysis/coverage_gaps.py)
    ├── Identify User Risks
    ├── Find Gaps
    └── Prioritize Gap-Filling Riders
    ↓
Explainability (explainability/)
    ├── SHAP Explainer (shap_explainer.py)
    ├── Explanation Generator (explanation_generator.py)
    └── Visualizer (visualizer.py)
    ↓
Comprehensive Recommendations + Explanations
```

## Project Structure

```
Research/
├── main.py                          # Enhanced main entry point
├── recommender.py                   # Core recommendation engine (refactored)
├── requirements.txt                 # Phase 2 dependencies
│
├── features/
│   └── feature_engineering.py       # User feature extraction
│
├── nlp/
│   ├── embedding.py                 # Sentence transformer embeddings
│   └── text_builders.py             # Enhanced user text generation
│
├── rules/
│   ├── policy_filter.py             # Policy eligibility rules
│   └── rider_filter.py              # Rider eligibility rules
│
├── scoring/
│   ├── component_scorers.py         # NEW: Individual scoring components
│   ├── ensemble_scorer.py           # NEW: Ensemble scoring system
│   ├── policy_ranker.py             # Legacy (kept for compatibility)
│   └── rider_ranker.py              # Legacy (kept for compatibility)
│
├── data/
│   ├── policies.py                  # Policy definitions
│   ├── riders.py                    # Rider definitions
│   └── coverage_mapping.py          # NEW: Coverage type mappings
│
├── analysis/
│   └── coverage_gaps.py             # NEW: Coverage gap analysis
│
└── explainability/                  # NEW: Explainability module
    ├── shap_explainer.py            # Feature importance analysis
    ├── explanation_generator.py     # Natural language explanations
    └── visualizer.py                # Visualization functions
```

## Installation

### run the vertual environment
```bash
source venv/Scripts/activate
```

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python main.py
```

## Usage

### Basic Usage

```python
from recommender import recommend

# User profile
user = {
    'age_nearest_bday': 45,
    'gender': 'Male',
    'marital_status': 'Married',
    'monthly_income': 120000,
    'primary_goal': 'Family protection',
    'dependents_count': 2,
    # ... other fields
}

# Get recommendations with explanations
result = recommend(user, explain=True)

print(f"Recommended Policy: {result['policy']}")
print(f"Confidence: {result['policy_score']:.1%}")

# Access primary riders
for rider_name, scores in result['primary_riders']:
    print(f"  - {rider_name}: {scores['final_score']:.1%}")
```

### Output Structure

```python
result = {
    'policy': 'Life+',                      # Best policy name
    'policy_score': 0.76,                   # Final confidence score
    'policy_explanation': {...},            # Detailed explanation dict
    'policy_shap': {...},                   # SHAP feature contributions
    'primary_riders': [...],                # High-priority riders
    'alternate_riders': [...],              # Medium-priority riders
    'rider_explanations': [...],            # Top 5 rider explanations
    'coverage_analysis': {...},             # Coverage gaps and completeness
    'coverage_gaps': [...],                 # List of uncovered risks
    'user_risks': [...],                    # All identified user risks
    'all_policy_scores': {...}              # All candidate policy scores
}
```

### Backward Compatibility

The old API is still supported:

```python
from recommender import recommend_simple

policy, riders = recommend_simple(user)
# Returns: ('Life+', [('Child Health', 0.827), ('Spouse Benefit', 0.804), ...])
```

## Key Components

### 1. Component Scorers (`scoring/component_scorers.py`)

Individual scoring functions that return `(score, breakdown)` tuples:

- **`rule_based_score_policy`**: Age fit, income fit, goal alignment, employment fit, medical eligibility
- **`rule_based_score_rider`**: Trigger match, medical relevance, family relevance
- **`trigger_strength_score`**: How strongly features match trigger conditions
- **`financial_fit_score`**: Affordability based on income vs estimated premium

### 2. Ensemble Scorer (`scoring/ensemble_scorer.py`)

Combines all components using configurable weights:

**Policy Weights (default)**:

- Rule: 35%
- NLP: 35%
- Financial: 30%

**Rider Weights (default)**:

- Rule: 30%
- NLP: 35%
- Trigger: 25%
- Financial: 10%

### 3. Coverage Gap Analysis (`analysis/coverage_gaps.py`)

Functions to identify and address coverage gaps:

- `identify_user_risks()`: Determine what risks user faces
- `find_coverage_gaps()`: Compare user risks to policy coverage
- `prioritize_riders_for_gaps()`: Find riders that fill gaps
- `analyze_coverage_completeness()`: Calculate coverage percentage

### 4. Explainability (`explainability/`)

**SHAP Explainer**: Computes feature importance

- Converts user profile to feature vector
- Calculates contribution of each feature to final score
- Identifies top positive/negative contributors

**Explanation Generator**: Creates human-readable explanations

- Policy explanations with primary reasons, supporting factors, concerns
- Rider explanations with trigger analysis and gap-filling info
- Confidence and priority level classification

**Visualizer**: Creates plots (requires matplotlib)

- SHAP waterfall plots
- Component score charts
- Coverage analysis pie charts
- Rider priority rankings
- Policy comparison charts

## Configuration

### Adjusting Ensemble Weights

```python
from scoring.ensemble_scorer import EnsembleScorer

custom_weights = {
    'rule': 0.40,
    'nlp': 0.30,
    'trigger': 0.20,
    'financial': 0.10
}

scorer = EnsembleScorer(weights=custom_weights)
```

### Changing Score Thresholds

Modify in `recommender.py`:

```python
# Primary riders threshold (default: 0.65)
if scores['final_score'] >= 0.70:  # More selective
    primary_riders.append((rider_name, scores))

# Alternate riders threshold (default: 0.45)
elif scores['final_score'] >= 0.50:  # More selective
    alternate_riders.append((rider_name, scores))
```

## Premium Estimation

Simplified premium estimation is included in `component_scorers.py`:

- Base rates by policy type (3-8% of monthly income)
- Age multipliers (older = higher premiums)
- Medical risk multipliers (1.0x to 2.0x)
- Lifestyle factors (smoker: 1.3x, hazardous job: 1.2x)

**Note**: Replace with actuarial calculations in production.

## Coverage Types

Defined in `data/coverage_mapping.py`:

- Death benefit
- Critical illness
- Disability income
- Hospitalization
- Surgery
- Chronic care
- Family protection
- Retirement income
- Outpatient care
- Maternity
- Accident coverage
- Overseas medical
- Organ transplant
- Child health
- Funeral expenses

## Explainability Examples

### Policy Explanation Output

```
WHY THIS POLICY?
  1. Perfect match for your primary goal: Family protection
  2. Ideal age fit for 45 years old

SUPPORTING FACTORS:
  • Designed for your Mid income bracket
  • Provides protection for your 2 dependent(s)
  • Financially suitable - estimated premium is affordable

CONSIDERATIONS:
  ⚠ Premium may be at higher end of budget
```

### SHAP Feature Contributions

```
FEATURE CONTRIBUTION ANALYSIS
Base Score: 0.500
Final Score: 0.760
Net Contribution: +0.260

TOP POSITIVE FACTORS:
  + Rule Match Score: +0.171
  + Affordability: +0.090
  + Married: +0.035

TOP NEGATIVE FACTORS:
  - Age Above 40: -0.015
```

### Coverage Gaps

```
COVERAGE ANALYSIS
Coverage Completeness: 42.9%

Covered Risks (3):
  ✓ Family income protection
  ✓ Death benefit
  ✓ Children healthcare

Coverage Gaps (4):
  ⚠ Hospital expenses
  ⚠ Critical illness coverage
  ⚠ Disability income protection
  ⚠ Retirement income
```

## Testing

Run the complete system:

```bash
python main.py
```

Expected output:

- Policy recommendation with confidence score
- Detailed explanations
- Coverage analysis
- Primary and alternate riders
- Feature contribution analysis
- Policy comparison

## Future Enhancements (Phase 3)

1. **Fine-tuned embeddings**: Train custom sentence-transformer on insurance domain
2. **LLM integration**: Dynamic text generation for personalized descriptions
3. **Predictive recommendations**: Lifecycle-based anticipatory suggestions
4. **Feedback loop**: Continuous learning from user acceptance data
5. **A/B testing**: Experimentation framework for recommendation strategies

## Performance

- **Policy scoring**: ~100ms per candidate policy
- **Rider scoring**: ~50ms per rider
- **Explanation generation**: ~50ms
- **Total recommendation time**: < 1 second for typical user profile

## Dependencies

- **sentence-transformers**: NLP embeddings
- **numpy**: Numerical computations
- **shap**: Feature importance (lightweight, no model training needed)
- **matplotlib**: Visualizations (optional)
- **pandas**: Data handling (optional)

## License

Research project for Prasa Insurance Recommendation System.

## Authors

Enhanced Phase 2 Implementation - December 2025
