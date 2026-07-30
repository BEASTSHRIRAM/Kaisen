#!/usr/bin/env python3
"""
Quick Runner for Adversarial Robustness Evaluation

Usage:
    python run_adversarial_eval.py --model models/best_model.weights.h5
    python run_adversarial_eval.py --epsilon 0.2 --samples 500
"""

import argparse
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from adversarial_eval_simple import AdversarialEvaluator
from agent import DQNAgent
from config import get_config


def main():
    parser = argparse.ArgumentParser(
        description="Run adversarial robustness evaluation on DQN-IDS"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/best_model.weights.h5",
        help="Path to trained DQN model weights"
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.15,
        help="Maximum perturbation magnitude (L-infinity norm)"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of test samples to evaluate"
    )
    parser.add_argument(
        "--attacks",
        type=str,
        nargs="+",
        default=["fgsm", "pgd", "feature_clipping", "random"],
        help="Attack methods to test"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="logs/adversarial_eval_report.json",
        help="Output path for JSON report"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    print("🔬 Kaisen Adversarial Robustness Evaluation")
    print("=" * 60)
    
    # Set seed
    np.random.seed(args.seed)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = get_config()
    
    # Initialize agent
    print(f"🤖 Initializing DQN agent...")
    agent = DQNAgent(
        state_size=13,
        action_size=5,
        config=config.agent
    )
    
    # Load model
    if os.path.exists(args.model):
        print(f"📂 Loading model: {args.model}")
        agent.load(args.model)
    else:
        print(f"⚠️  Model not found: {args.model}")
        print(f"   Training small model for demonstration...")
        # Train on dummy data
        for _ in range(10):
            state = np.random.randn(13)
            action = agent.select_action(state, training=True)
            reward = 1.0 if action == 0 else -0.5
            next_state = np.random.randn(13)
            agent.store_experience(state, action, reward, next_state, False)
            agent.train_step()
    
    # Generate test dataset
    print(f"\n📊 Generating {args.samples} test samples...")
    test_states = np.random.randn(args.samples, 13).astype(np.float32)
    test_labels = np.random.randint(0, 5, args.samples)
    
    # Normalize to reasonable ranges (OS metrics)
    test_states[:, 0] = np.clip(test_states[:, 0] * 20 + 50, 0, 100)      # CPU: 0-100
    test_states[:, 1] = np.clip(test_states[:, 1] * 20 + 50, 0, 100)      # Memory: 0-100
    test_states[:, 2] = np.clip(test_states[:, 2] * 50 + 200, 0, 500)     # Processes
    test_states[:, 3] = np.clip(test_states[:, 3] * 100 + 200, 0, 1000)   # Connections
    test_states[:, 4] = np.clip(test_states[:, 4] * 10 + 15, 0, 50)       # Unique IPs
    test_states[:, 5] = np.clip(test_states[:, 5] * 10 + 5, 0, 100)       # Failed logins
    
    # Run evaluation
    print(f"\n🎯 Running adversarial evaluation...")
    print(f"   Epsilon: {args.epsilon}")
    print(f"   Attacks: {', '.join(args.attacks)}")
    
    evaluator = AdversarialEvaluator(
        agent,
        feature_bounds=None,
        epsilon=args.epsilon
    )
    
    metrics = evaluator.evaluate_on_dataset(
        test_states,
        test_labels,
        attack_methods=args.attacks
    )
    
    # Generate report
    print(f"\n📁 Generating report...")
    report_path = evaluator.generate_report(metrics, output_path=args.output)
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("📈 DETAILED RESULTS")
    print("=" * 60)
    
    for attack_name, attack_metrics in metrics['attack_results'].items():
        print(f"\n🔴 {attack_name.upper()}:")
        print(f"   Success Rate:       {attack_metrics['attack_success_rate']:.1%}")
        print(f"   Successful:         {attack_metrics['successful_attacks']}/{attack_metrics['total_attacks']}")
        print(f"   Avg L2 Distance:    {attack_metrics['avg_perturbation_l2']:.6f}")
        print(f"   Avg L-inf Distance: {attack_metrics['avg_perturbation_linf']:.6f}")
    
    print(f"\n✅ SUMMARY STATS:")
    summary = metrics['summary']
    print(f"   Avg Attack Success:    {summary['average_attack_success_rate']:.1%}")
    print(f"   Robustness Score:      {summary['robustness_score']:.1%}")
    print(f"   Avg L2 Perturbation:   {summary['average_l2_perturbation']:.6f}")
    print(f"   Avg L-inf Perturbation: {summary['average_linf_perturbation']:.6f}")
    
    print(f"\n💾 Report saved to: {report_path}")
    print("=" * 60)
    
    # Return non-zero if robustness is too low
    if summary['robustness_score'] < 0.5:
        print("\n⚠️  WARNING: Robustness score is below 50%!")
        print("   Consider adversarial training or defense mechanisms.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
