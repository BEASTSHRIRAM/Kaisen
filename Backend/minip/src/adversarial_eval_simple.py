"""Adversarial Robustness Evaluation Module"""
import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Optional
import json
import os
from datetime import datetime
from collections import defaultdict


class AdversarialAttacker:
    """Generates adversarial examples against the DQN model."""
    
    def __init__(self, dqn_agent, feature_bounds, epsilon=0.1, num_steps=20, step_size=0.01):
        self.agent = dqn_agent
        self.feature_bounds = feature_bounds
        self.epsilon = epsilon
        self.num_steps = num_steps
        self.step_size = step_size
        self.attack_log = []
        
    def _clip_perturbation(self, original, perturbed, epsilon):
        """Clip perturbation to epsilon-ball."""
        delta = np.clip(perturbed - original, -epsilon, epsilon)
        return original + delta
    
    def _clip_to_bounds(self, state, feature_bounds):
        """Clip state to valid feature ranges."""
        clipped = state.copy()
        for i, (feature_name, (min_val, max_val)) in enumerate(feature_bounds.items()):
            clipped[i] = np.clip(clipped[i], min_val, max_val)
        return clipped
    
    def fgsm(self, state, true_label, target_label=None):
        """Fast Gradient Sign Method attack."""
        state_tensor = tf.convert_to_tensor(state.reshape(1, -1), dtype=tf.float32)
        
        with tf.GradientTape() as tape:
            tape.watch(state_tensor)
            q_values = self.agent.q_network(state_tensor, training=False)
            loss = -q_values[0, target_label] if target_label else q_values[0, true_label]
        
        gradients = tape.gradient(loss, state_tensor)
        if gradients is None:
            return self._clip_to_bounds(state, self.feature_bounds)
        
        perturbation = self.step_size * tf.sign(gradients)
        adversarial = state_tensor + perturbation
        adversarial = tf.cast(adversarial, tf.float32).numpy().flatten()
        
        adversarial = self._clip_perturbation(state, adversarial, self.epsilon)
        return self._clip_to_bounds(adversarial, self.feature_bounds)
    
    def pgd(self, state, true_label, target_label=None, random_init=True):
        """Projected Gradient Descent attack."""
        if random_init:
            delta = np.random.uniform(-self.epsilon, self.epsilon, state.shape)
            adversarial = state + delta
        else:
            adversarial = state.copy()
        
        adversarial = self._clip_to_bounds(adversarial, self.feature_bounds)
        
        for step in range(self.num_steps):
            adversarial_tensor = tf.convert_to_tensor(adversarial.reshape(1, -1), dtype=tf.float32)
            
            with tf.GradientTape() as tape:
                tape.watch(adversarial_tensor)
                q_values = self.agent.q_network(adversarial_tensor, training=False)
                loss = -q_values[0, target_label] if target_label else q_values[0, true_label]
            
            gradients = tape.gradient(loss, adversarial_tensor)
            if gradients is None:
                break
            
            perturbation = self.step_size * tf.sign(gradients)
            adversarial = adversarial + perturbation.numpy().flatten()
            
            adversarial = self._clip_perturbation(state, adversarial, self.epsilon)
            adversarial = self._clip_to_bounds(adversarial, self.feature_bounds)
        
        return adversarial
    
    def feature_clipping(self, state, perturbation_type="maximize"):
        """Feature clipping attack: Set features to extreme values."""
        adversarial = state.copy()
        
        for i, (feature_name, (min_val, max_val)) in enumerate(self.feature_bounds.items()):
            if perturbation_type == "reduce":
                adversarial[i] = min_val
            elif perturbation_type == "maximize":
                adversarial[i] = max_val
            elif perturbation_type == "random":
                adversarial[i] = np.random.uniform(min_val, max_val)
        
        return adversarial
    
    def random_perturbation(self, state, epsilon=None):
        """Random perturbation baseline."""
        if epsilon is None:
            epsilon = self.epsilon
        
        delta = np.random.uniform(-epsilon, epsilon, state.shape)
        adversarial = state + delta
        
        return self._clip_to_bounds(adversarial, self.feature_bounds)


class AdversarialEvaluator:
    """Comprehensive evaluation of DQN robustness against adversarial attacks."""
    
    def __init__(self, dqn_agent, baseline_agents=None, feature_bounds=None, epsilon=0.15):
        self.dqn_agent = dqn_agent
        self.baseline_agents = baseline_agents or {}
        
        self.feature_bounds = feature_bounds or {
            "cpu_usage": (0.0, 100.0),
            "memory_usage": (0.0, 100.0),
            "process_count": (0.0, 500.0),
            "network_connections": (0.0, 1000.0),
            "unique_ips": (0.0, 50.0),
            "failed_logins": (0.0, 100.0),
            "lateral_movement": (0.0, 1.0),
            "port_scan_score": (0.0, 1.0),
            "resource_exhaustion": (0.0, 1.0),
            "entropy_spike": (0.0, 1.0),
            "connection_rate": (0.0, 100.0),
            "anomaly_score": (0.0, 1.0),
            "previous_anomaly_score": (0.0, 1.0),
        }
        
        self.epsilon = epsilon
        self.attacker = AdversarialAttacker(
            dqn_agent,
            self.feature_bounds,
            epsilon=epsilon,
            num_steps=20,
            step_size=0.01
        )
        self.results = defaultdict(list)
    
    def evaluate_on_dataset(self, states, labels, attack_methods=None):
        """Evaluate robustness on a dataset of test examples."""
        if attack_methods is None:
            attack_methods = ["fgsm", "pgd", "feature_clipping"]
        
        metrics = {
            "total_samples": len(states),
            "attacks_tested": attack_methods,
            "epsilon": self.epsilon,
            "timestamp": datetime.now().isoformat(),
            "attack_results": {}
        }
        
        for attack_name in attack_methods:
            print(f"\n🔴 Testing {attack_name.upper()} attack...")
            attack_metrics = self._evaluate_attack(states, labels, attack_name)
            metrics["attack_results"][attack_name] = attack_metrics
        
        metrics["summary"] = self._compute_summary(metrics["attack_results"])
        return metrics
    
    def _evaluate_attack(self, states, labels, attack_method):
        """Evaluate a single attack method."""
        metrics = {
            "attack_method": attack_method,
            "successful_attacks": 0,
            "total_attacks": len(states),
            "attack_success_rate": 0.0,
            "avg_perturbation_l2": 0.0,
            "avg_perturbation_linf": 0.0,
        }
        
        perturbation_l2 = []
        perturbation_linf = []
        
        for i, (state, true_label) in enumerate(zip(states, labels)):
            original_q_values = self.dqn_agent.get_q_values(state)
            original_action = np.argmax(original_q_values)
            
            if attack_method == "fgsm":
                adversarial = self.attacker.fgsm(state, true_label)
            elif attack_method == "pgd":
                adversarial = self.attacker.pgd(state, true_label, random_init=True)
            elif attack_method == "feature_clipping":
                adversarial = self.attacker.feature_clipping(state, "maximize")
            elif attack_method == "random":
                adversarial = self.attacker.random_perturbation(state)
            else:
                continue
            
            adversarial_q_values = self.dqn_agent.get_q_values(adversarial)
            adversarial_action = np.argmax(adversarial_q_values)
            
            attack_success = (adversarial_action != original_action)
            
            l2_dist = np.linalg.norm(adversarial - state, ord=2)
            linf_dist = np.linalg.norm(adversarial - state, ord=np.inf)
            
            if attack_success:
                metrics["successful_attacks"] += 1
            
            perturbation_l2.append(l2_dist)
            perturbation_linf.append(linf_dist)
            
            if (i + 1) % max(1, len(states) // 10) == 0:
                print(f"  Progress: {i + 1}/{len(states)}")
        
        metrics["attack_success_rate"] = (metrics["successful_attacks"] / metrics["total_attacks"]) if metrics["total_attacks"] > 0 else 0.0
        metrics["avg_perturbation_l2"] = float(np.mean(perturbation_l2)) if perturbation_l2 else 0.0
        metrics["avg_perturbation_linf"] = float(np.mean(perturbation_linf)) if perturbation_linf else 0.0
        
        print(f"  ✓ Attack Success Rate: {metrics['attack_success_rate']:.2%}")
        print(f"  ✓ Avg L2 Distance: {metrics['avg_perturbation_l2']:.4f}")
        print(f"  ✓ Avg L-inf Distance: {metrics['avg_perturbation_linf']:.4f}")
        
        return metrics
    
    def _compute_summary(self, attack_results):
        """Compute summary statistics across all attacks."""
        summary = {
            "average_attack_success_rate": 0.0,
            "average_l2_perturbation": 0.0,
            "average_linf_perturbation": 0.0,
            "robustness_score": 0.0,
        }
        
        if attack_results:
            asrs = [v["attack_success_rate"] for v in attack_results.values()]
            l2s = [v["avg_perturbation_l2"] for v in attack_results.values()]
            linfs = [v["avg_perturbation_linf"] for v in attack_results.values()]
            
            summary["average_attack_success_rate"] = float(np.mean(asrs))
            summary["average_l2_perturbation"] = float(np.mean(l2s))
            summary["average_linf_perturbation"] = float(np.mean(linfs))
            summary["robustness_score"] = 1.0 - summary["average_attack_success_rate"]
        
        return summary
    
    def generate_report(self, metrics, output_path="logs/adversarial_eval_report.json"):
        """Generate and save evaluation report."""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print("\n" + "="*60)
        print("📊 ADVERSARIAL ROBUSTNESS EVALUATION REPORT")
        print("="*60)
        print(f"Evaluation Time: {metrics['timestamp']}")
        print(f"Total Samples: {metrics['total_samples']}")
        print(f"Epsilon (max perturbation): {metrics['epsilon']}")
        print(f"Attack Methods: {', '.join(metrics['attacks_tested'])}")
        print()
        
        for attack_name, attack_metrics in metrics['attack_results'].items():
            print(f"\n🔴 {attack_name.upper()}:")
            print(f"   Attack Success Rate: {attack_metrics['attack_success_rate']:.2%}")
            print(f"   Successful: {attack_metrics['successful_attacks']}/{attack_metrics['total_attacks']}")
            print(f"   Avg L2 Distance: {attack_metrics['avg_perturbation_l2']:.4f}")
            print(f"   Avg L-inf Distance: {attack_metrics['avg_perturbation_linf']:.4f}")
        
        print(f"\n✅ SUMMARY:")
        summary = metrics['summary']
        print(f"   Average Attack Success Rate: {summary['average_attack_success_rate']:.2%}")
        print(f"   Robustness Score: {summary['robustness_score']:.2%} (1.0 = fully robust)")
        print(f"   Avg L2 Perturbation: {summary['average_l2_perturbation']:.4f}")
        print(f"   Avg L-inf Perturbation: {summary['average_linf_perturbation']:.4f}")
        
        print(f"\n📁 Report saved to: {output_path}")
        print("="*60 + "\n")
        
        return output_path
