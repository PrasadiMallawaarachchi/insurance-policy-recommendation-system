"""
Visualization module for SHAP explanations and recommendation analysis.
Generates plots and charts to visualize feature importance and comparisons.
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visualizations will be disabled.")

import numpy as np


class RecommendationVisualizer:
    """
    Create visualizations for recommendation explanations.
    Generates SHAP plots, comparison charts, and coverage visualizations.
    """
    
    def __init__(self, output_dir="./outputs"):
        """
        Initialize visualizer with output directory.
        
        Args:
            output_dir: Directory to save generated plots
        """
        self.output_dir = output_dir
        self.matplotlib_available = MATPLOTLIB_AVAILABLE
    
    def plot_shap_waterfall(self, explanation, save_path=None):
        """
        Create SHAP waterfall plot showing feature contributions.
        
        Args:
            explanation: Dict from RecommendationExplainer.explain_recommendation
            save_path: Path to save plot (optional)
        
        Returns:
            str: Path to saved plot or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping waterfall plot")
            return None
        
        # Extract data
        shap_values = explanation['shap_values']
        feature_names = explanation['feature_names']
        base_value = explanation['base_value']
        final_score = explanation['final_score']
        
        # Get top contributors (positive and negative)
        indices = np.argsort(np.abs(shap_values))[-10:]  # Top 10
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot waterfall
        y_pos = np.arange(len(indices))
        colors = ['green' if shap_values[i] > 0 else 'red' for i in indices]
        
        ax.barh(y_pos, [shap_values[i] for i in indices], color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_xlabel('Contribution to Score')
        ax.set_title(f'Feature Contributions (Base: {base_value:.2f} → Final: {final_score:.2f})')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def plot_component_scores(self, scores_dict, title="Score Components", save_path=None):
        """
        Create bar chart of component scores.
        
        Args:
            scores_dict: Dict with component names and scores
            title: Chart title
            save_path: Path to save plot
        
        Returns:
            str: Path to saved plot or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping component scores plot")
            return None
        
        components = list(scores_dict.keys())
        scores = list(scores_dict.values())
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        bars = ax.bar(components, scores, color=colors[:len(components)], alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1%}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylim([0, 1.0])
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def plot_coverage_analysis(self, coverage_data, save_path=None):
        """
        Create visualization of coverage gaps analysis.
        
        Args:
            coverage_data: Dict from analyze_coverage_completeness
            save_path: Path to save plot
        
        Returns:
            str: Path to saved plot or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping coverage analysis plot")
            return None
        
        # Prepare data
        labels = ['Covered', 'Gaps']
        sizes = [len(coverage_data['covered_risks']), len(coverage_data['coverage_gaps'])]
        colors = ['#2E86AB', '#F18F01']
        explode = (0.05, 0.05)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(
                sizes, 
                explode=explode, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                shadow=True, 
                startangle=90
            )
            
            # Enhance text
            for text in texts:
                text.set_fontsize(12)
                text.set_fontweight('bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(11)
                autotext.set_fontweight('bold')
        
        ax.set_title(f"Coverage Completeness: {coverage_data['coverage_percentage']:.1f}%", 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def plot_rider_priority_ranking(self, rider_scores, top_n=10, save_path=None):
        """
        Create horizontal bar chart of rider priority scores.
        
        Args:
            rider_scores: Dict mapping rider names to score dicts
            top_n: Number of top riders to show
            save_path: Path to save plot
        
        Returns:
            str: Path to saved plot or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping rider ranking plot")
            return None
        
        # Sort by final score
        sorted_riders = sorted(
            rider_scores.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )[:top_n]
        
        rider_names = [name for name, _ in sorted_riders]
        scores = [data['final_score'] for _, data in sorted_riders]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        y_pos = np.arange(len(rider_names))
        colors = ['#2E86AB' if s >= 0.65 else '#F18F01' if s >= 0.45 else '#A23B72' 
                 for s in scores]
        
        bars = ax.barh(y_pos, scores, color=colors, alpha=0.8)
        
        # Add value labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{score:.1%}',
                   ha='left', va='center', fontweight='bold', fontsize=9)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(rider_names, fontsize=10)
        ax.set_xlabel('Relevance Score', fontsize=12)
        ax.set_title('Rider Priority Ranking', fontsize=14, fontweight='bold')
        ax.set_xlim([0, 1.0])
        ax.grid(axis='x', alpha=0.3)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2E86AB', label='High Priority (≥65%)'),
            Patch(facecolor='#F18F01', label='Medium Priority (45-65%)'),
            Patch(facecolor='#A23B72', label='Low Priority (<45%)')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def plot_policy_comparison(self, policy_scores, save_path=None):
        """
        Create comparison chart of all candidate policies.
        
        Args:
            policy_scores: Dict mapping policy names to score dicts
            save_path: Path to save plot
        
        Returns:
            str: Path to saved plot or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping policy comparison plot")
            return None
        
        # Sort by final score
        sorted_policies = sorted(
            policy_scores.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )
        
        policy_names = [name for name, _ in sorted_policies]
        final_scores = [data['final_score'] for _, data in sorted_policies]
        
        # Get component scores
        rule_scores = [data['components']['rule_score'] for _, data in sorted_policies]
        nlp_scores = [data['components']['nlp_score'] for _, data in sorted_policies]
        financial_scores = [data['components']['financial_score'] for _, data in sorted_policies]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(policy_names))
        width = 0.2
        
        ax.bar(x - width*1.5, rule_scores, width, label='Rule Score', color='#2E86AB', alpha=0.8)
        ax.bar(x - width*0.5, nlp_scores, width, label='NLP Score', color='#A23B72', alpha=0.8)
        ax.bar(x + width*0.5, financial_scores, width, label='Financial Score', color='#F18F01', alpha=0.8)
        ax.bar(x + width*1.5, final_scores, width, label='Final Score', color='#C73E1D', alpha=0.9)
        
        ax.set_xlabel('Policies', fontsize=12)
        ax.set_ylabel('Scores', fontsize=12)
        ax.set_title('Policy Score Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(policy_names, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim([0, 1.0])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def create_summary_dashboard(self, policy_explanation, coverage_data, 
                                 rider_scores, save_path=None):
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            policy_explanation: Policy explanation dict
            coverage_data: Coverage analysis dict
            rider_scores: Rider scores dict
            save_path: Path to save dashboard
        
        Returns:
            str: Path to saved dashboard or None
        """
        if not self.matplotlib_available:
            print("Matplotlib not available - skipping dashboard creation")
            return None
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Component scores
        ax1 = fig.add_subplot(gs[0, 0])
        components = policy_explanation['component_scores']
        comp_dict = {
            'Rule': components.get('rule_score', 0),
            'NLP': components.get('nlp_score', 0),
            'Financial': components.get('financial_score', 0)
        }
        bars = ax1.bar(comp_dict.keys(), comp_dict.values(), color=['#2E86AB', '#A23B72', '#F18F01'])
        ax1.set_ylim([0, 1.0])
        ax1.set_title('Component Scores', fontweight='bold')
        ax1.set_ylabel('Score')
        
        # Coverage pie chart
        ax2 = fig.add_subplot(gs[0, 1])
        sizes = [len(coverage_data['covered_risks']), len(coverage_data['coverage_gaps'])]
        if sum(sizes) > 0:
            ax2.pie(sizes, labels=['Covered', 'Gaps'], colors=['#2E86AB', '#F18F01'],
                   autopct='%1.1f%%', startangle=90)
        ax2.set_title(f"Coverage: {coverage_data['coverage_percentage']:.1f}%", fontweight='bold')
        
        # Top riders
        ax3 = fig.add_subplot(gs[1, :])
        sorted_riders = sorted(rider_scores.items(), 
                              key=lambda x: x[1]['final_score'], 
                              reverse=True)[:8]
        rider_names = [name for name, _ in sorted_riders]
        scores = [data['final_score'] for _, data in sorted_riders]
        colors = ['#2E86AB' if s >= 0.65 else '#F18F01' for s in scores]
        ax3.barh(rider_names, scores, color=colors, alpha=0.8)
        ax3.set_xlabel('Relevance Score')
        ax3.set_title('Top Recommended Riders', fontweight='bold')
        ax3.set_xlim([0, 1.0])
        
        fig.suptitle(f"Recommendation Dashboard: {policy_explanation['recommendation']}", 
                    fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
