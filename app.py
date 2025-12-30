from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend
import traceback
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Flask
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def convert_to_json_serializable(obj):
    """
    Recursively convert non-JSON-serializable objects to serializable types.
    Handles: sets, numpy arrays, numpy types, and nested structures.
    """
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

@app.route('/api/recommend', methods=['POST'])
def get_recommendation():
    """
    API endpoint to get insurance recommendations
    Expects JSON body with user profile data
    """
    try:
        # Get user data from request
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({'error': 'No user data provided'}), 400

        print(f"Received user data: {user_data}")
        # Validate required fields
        required_fields = ['age_nearest_bday', 'gender', 'monthly_income', 'primary_goal']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Set defaults for optional fields
        defaults = {
            'marital_status': 'Single',
            'nationality': 'Sri Lankan',
            'country': 'Sri Lanka',
            'district': 'Colombo',
            'city': 'Colombo',
            'occupation': 'Professional',
            'employment_type': 'Permanent',
            'designation': 'Staff',
            'hazardous_level': 'Low',
            'hazardous_activities': '',
            'existing_insurance': 'No',
            'dependents_count': 0,
            'secondary_goal': 'None',
            'chronic_disease': False,
            'cardiovascular_health_issue': False,
            'cancer_or_tumors': False,
            'respiratory_conditions': False,
            'neurological_or_mental_health_conditions': False,
            'gastrointestinal_conditions': False,
            'musculoskeletal_conditions': False,
            'infectious_or_sexual_health_conditions': False,
            'recent_treatment_or_surgery': False,
            'covid19_related_conditions': False,
            'bmi': 22.0,
            'smoker': 'No',
            'alcohol_consumer': 'No',
            'travel_history_high_risk_countries': False,
            'dual_citizenship': False,
            'tax_or_regulatory_flags': False,
            'insurance_history_issues': False,
            'current_insurance_status': 'None',
            'employer_scheme': False
        }
        
        # Merge defaults with user data
        for key, value in defaults.items():
            if key not in user_data:
                user_data[key] = value
        
        # Get recommendations
        result = recommend(user_data, explain=True)
        print("Generated recommendation result.", result)
        
        # Check if recommendation was successful
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Convert all non-serializable types to JSON-serializable types
        result = convert_to_json_serializable(result)
        
        # Format response for frontend
        response = {
            'success': True,
            'policy': {
                'name': result['policy'],
                'score': round(result['policy_score'] * 100, 1),
                'explanation': result.get('policy_explanation', {})
            },
            'primary_riders': [
                {
                    'name': name,
                    'score': round(scores['final_score'] * 100, 1),
                    'scores': scores
                }
                for name, scores in result.get('primary_riders', [])
            ],
            'alternate_riders': [
                {
                    'name': name,
                    'score': round(scores['final_score'] * 100, 1),
                    'scores': scores
                }
                for name, scores in result.get('alternate_riders', [])
            ],
            'coverage_analysis': result.get('coverage_analysis', {}),
            'rider_explanations': result.get('rider_explanations', []),
            'all_policy_scores': result.get('all_policy_scores', {}),
            'policy_shap': result.get('policy_shap', {})
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        # Log the error and return a user-friendly message
        print(f"Error in /api/recommend: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred while processing your request: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Insurance Recommendation API is running'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("INSURANCE RECOMMENDATION SYSTEM - API SERVER")
    print("="*80)
    print("\nStarting Flask API server...")
    print("API Endpoint: http://127.0.0.1:5000/api/recommend (POST)")
    print("Health Check: http://127.0.0.1:5000/api/health (GET)")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
