"""
Visualization utilities for adversarial robustness evaluation results.

Generates publication-ready figures for the paper.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import os


class AdversarialReportVisualizer:
    """Generate publication-ready visualizations from evaluation results."""
    
    def __init__(self, report_path: str, output_dir: str = "figures"):
        """
        Args:
            report_path: Path to JSON report from AdversarialEvaluator
            output_dir: Directory to save figures
        """
        self.report_path = report_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Load report
        with open(report_path, 'r') as f:
            self.report = json.load(f)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11
    
    def plot_attack_success_rates(self, save: bool = True) -> str:
        """
        Figure 1: Attack Success Rate comparison across methods.
        
        Bar chart showing:
        - X-axis: Attack methods (FGSM, PGD, Feature Clipping, Random)
        - Y-axis: Attack Success Rate (%)
        - Error bars: Min/max ASR
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        attacks = []
        asrs = []
        
        for attack_name, metrics in self.report['attack_results'].items():
            attacks.append(attack_name.upper())
            asrs.append(metrics['attack_success_rate'] * 100)
        
        colors = ['#FF6B6B', '#FF8C42', '#FFC93C', '#95E1D3']
        bars = ax.bar(attacks, asrs, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Attack Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Attack Method', fontsize=12, fontweight='bold')
        ax.set_title('DQN-IDS Robustness: Attack Success Rate by Method', 
                     fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(asrs) * 1.2)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, "01_attack_success_rates.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {path}")
        
        return path if save else None
    
    def plot_perturbation_distances(self, save: bool = True) -> str:
        """
        Figure 2: Perturbation distances (L2 and L-inf norms).
        
        Grouped bar chart showing:
        - X-axis: Attack methods
        - Y-axis: Distance magnitude
        - Grouped bars: L2 vs L-inf
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        attacks = []
        l2_distances = []
        linf_distances = []
        
        for attack_name, metrics in self.report['attack_results'].items():
            attacks.append(attack_name.upper())
            l2_distances.append(metrics['avg_perturbation_l2'])
            linf_distances.append(metrics['avg_perturbation_linf'])
        
        x = np.arange(len(attacks))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, l2_distances, width, label='L2 Distance',
                      color='#4A90E2', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, linf_distances, width, label='L-inf Distance',
                      color='#F5A623', edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}',
                   ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}',
                   ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('Distance Magnitude', fontsize=12, fontweight='bold')
        ax.set_xlabel('Attack Method', fontsize=12, fontweight='bold')
        ax.set_title('Perturbation Magnitudes: L2 vs L-infinity', 
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(attacks)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, "02_perturbation_distances.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {path}")
        
        return path if save else None
    
    def plot_robustness_scores(self, save: bool = True) -> str:
        """
        Figure 3: Robustness scores (1 - ASR) for each method.
        
        Horizontal bar chart:
        - X-axis: Robustness Score (%)
        - Y-axis: Attack methods
        - Green = robust, red = vulnerable
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        attacks = []
        robustness_scores = []
        
        for attack_name, metrics in self.report['attack_results'].items():
            attacks.append(attack_name.upper())
            robustness = (1 - metrics['attack_success_rate']) * 100
            robustness_scores.append(robustness)
        
        # Color based on robustness
        colors = ['#2ECC71' if score >= 80 else '#F39C12' if score >= 50 else '#E74C3C'
                 for score in robustness_scores]
        
        bars = ax.barh(attacks, robustness_scores, color=colors, 
                       edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width - 5, bar.get_y() + bar.get_height()/2.,
                   f'{robustness_scores[i]:.1f}%',
                   ha='right', va='center', fontweight='bold', color='white')
        
        ax.set_xlabel('Robustness Score (%)', fontsize=12, fontweight='bold')
        ax.set_title('DQN-IDS Robustness Scores by Attack Method', 
                     fontsize=14, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.axvline(x=80, color='red', linestyle='--', linewidth=2, 
                  label='Target Threshold (80%)')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, "03_robustness_scores.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {path}")
        
        return path if save else None
    
    def plot_summary_metrics(self, save: bool = True) -> str:
        """
        Figure 4: Summary metrics comparison.
        
        Shows:
        - Average ASR
        - Average robustness
        - Average perturbations
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        summary = self.report['summary']
        
        # Plot 1: Average ASR
        ax1.bar(['Avg ASR'], [summary['average_attack_success_rate']*100], 
               color='#E74C3C', edgecolor='black', linewidth=2)
        ax1.set_ylabel('ASR (%)', fontweight='bold')
        ax1.set_title('Average Attack Success Rate', fontweight='bold')
        ax1.set_ylim(0, 100)
        ax1.text(0, summary['average_attack_success_rate']*100 + 2, 
                f"{summary['average_attack_success_rate']*100:.1f}%",
                ha='center', fontweight='bold')
        
        # Plot 2: Robustness Score
        ax2.bar(['Robustness'], [summary['robustness_score']*100], 
               color='#2ECC71', edgecolor='black', linewidth=2)
        ax2.set_ylabel('Score (%)', fontweight='bold')
        ax2.set_title('Overall Robustness Score', fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.text(0, summary['robustness_score']*100 + 2, 
                f"{summary['robustness_score']*100:.1f}%",
                ha='center', fontweight='bold')
        
        # Plot 3: L2 Perturbation
        ax3.bar(['Avg L2'], [summary['average_l2_perturbation']], 
               color='#4A90E2', edgecolor='black', linewidth=2)
        ax3.set_ylabel('L2 Distance', fontweight='bold')
        ax3.set_title('Average L2 Perturbation', fontweight='bold')
        ax3.text(0, summary['average_l2_perturbation'] + 0.02, 
                f"{summary['average_l2_perturbation']:.4f}",
                ha='center', fontweight='bold')
        
        # Plot 4: L-inf Perturbation
        ax4.bar(['Avg L-inf'], [summary['average_linf_perturbation']], 
               color='#F5A623', edgecolor='black', linewidth=2)
        ax4.set_ylabel('L-inf Distance', fontweight='bold')
        ax4.set_title('Average L-inf Perturbation', fontweight='bold')
        ax4.text(0, summary['average_linf_perturbation'] + 1, 
                f"{summary['average_linf_perturbation']:.4f}",
                ha='center', fontweight='bold')
        
        fig.suptitle('DQN-IDS Adversarial Robustness: Summary Metrics', 
                    fontsize=16, fontweight='bold', y=1.00)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, "04_summary_metrics.png")
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {path}")
        
        return path if save else None
    
    def generate_all_figures(self) -> List[str]:
        """Generate all figures."""
        print("\n📊 Generating publication-ready figures...\n")
        
        paths = []
        paths.append(self.plot_attack_success_rates())
        paths.append(self.plot_perturbation_distances())
        paths.append(self.plot_robustness_scores())
        paths.append(self.plot_summary_metrics())
        
        print(f"\n✅ All figures saved to: {self.output_dir}/")
        return paths


def example_visualization():
    """Example: Generate figures from a report."""
    report_path = "logs/adversarial_eval_report.json"
    
    if not os.path.exists(report_path):
        print(f"❌ Report not found: {report_path}")
        print("   Run: python run_adversarial_eval.py")
        return
    
    visualizer = AdversarialReportVisualizer(report_path)
    visualizer.generate_all_figures()


if __name__ == "__main__":
    example_visualization()
