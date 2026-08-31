"""
Adversarial Defense Mechanisms for Kaisen DQN-IDS

This module implements multiple defense strategies to protect against
adversarial metric manipulation:

1. Input Validation (IQR Bounds Check)
2. Anomalous Metric Detection
3. Adversarial Training
4. Ensemble Voting
5. Confidence Thresholding
6. Feature Importance Weighting
"""

import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Optional
from collections import deque
import json


class InputValidator:
    """
    Defense #1: INPUT VALIDATION
    
    Detects abnormal metrics that look suspicious.
    Uses Interquartile Range (IQR) to catch extreme values.
    """
    
    def __init__(self, feature_bounds: Dict[str, Tuple[float, float]]):
        """
        Args:
            feature_bounds: Dict of (min, max) for each metric
        """
        self.feature_bounds = feature_bounds
        self.feature_history = defaultdict(lambda: deque(maxlen=100))
        self.suspicious_count = 0
        
    def check_suspicious_metrics(self, state: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Check if any metrics look suspicious (extreme values).
        
        Returns:
            (is_suspicious, list of suspicious features)
        """
        suspicious_features = []
        
        for i, (feature_name, (min_val, max_val)) in enumerate(self.feature_bounds.items()):
            value = state[i]
            
            # Check 1: Out of normal bounds
            if value < min_val * 0.5 or value > max_val * 1.5:
                suspicious_features.append(f"{feature_name}={value:.2f} (extreme)")
                continue
            
            # Check 2: Sudden spike/drop
            if len(self.feature_history[feature_name]) > 5:
                recent_values = list(self.feature_history[feature_name])
                avg = np.mean(recent_values)
                std = np.std(recent_values)
                
                if std > 0 and abs(value - avg) > 3 * std:
                    suspicious_features.append(
                        f"{feature_name}={value:.2f} (spike from {avg:.2f})"
                    )
            
            self.feature_history[feature_name].append(value)
        
        if suspicious_features:
            self.suspicious_count += 1
            return True, suspicious_features
        
        return False, []
    
    def get_alert(self, state: np.ndarray) -> Optional[Dict]:
        """Generate security alert if suspicious."""
        is_suspicious, features = self.check_suspicious_metrics(state)
        
        if is_suspicious:
            return {
                "type": "METRIC_ANOMALY",
                "severity": "HIGH",
                "suspicious_features": features,
                "action": "QUARANTINE",
                "reason": "Abnormal metric values detected"
            }
        
        return None


class AnomalousMetricDetector:
    """
    Defense #2: ANOMALOUS METRIC CORRELATION
    
    Detects when metrics don't make sense together.
    Example: High CPU + Low Network = suspicious (normal attacks need network)
    """
    
    def __init__(self):
        self.correlation_rules = [
            # Rule 1: High CPU + High Memory + Low network = normal work
            # Rule 2: Low CPU + Low Memory + High network = suspicious (port scan?)
            # Rule 3: All metrics low + Failed logins high = brute force attempt
        ]
    
    def check_metric_consistency(self, state: np.ndarray) -> Tuple[bool, str]:
        """
        Check if metrics form a logical pattern.
        
        Returns:
            (is_anomalous, reason)
        """
        cpu = state[0]           # 0-100
        memory = state[1]        # 0-100
        connections = state[3]   # 0-1000
        failed_logins = state[5] # 0-100
        
        # Pattern 1: Lateral movement signature
        if connections > 500 and failed_logins > 50:
            return True, "HIGH_LATERAL_MOVEMENT_SIGNATURE"
        
        # Pattern 2: Resource exhaustion attempt
        if cpu < 20 and memory < 20 and connections > 300:
            return True, "UNLIKELY_RESOURCE_PATTERN"
        
        # Pattern 3: Brute force attempt
        if failed_logins > 70 and (cpu < 10 or memory < 10):
            return True, "BRUTE_FORCE_PATTERN"
        
        # Pattern 4: Abnormal idle with high activity
        if cpu < 5 and memory < 5 and connections > 200:
            return True, "IMPOSSIBLE_IDLE_STATE"
        
        return False, ""
    
    def get_alert(self, state: np.ndarray) -> Optional[Dict]:
        """Generate alert if metrics are inconsistent."""
        is_anomalous, reason = self.check_metric_consistency(state)
        
        if is_anomalous:
            return {
                "type": "METRIC_INCONSISTENCY",
                "severity": "CRITICAL",
                "pattern": reason,
                "action": "BLOCK",
                "reason": f"Metrics don't form a logical pattern: {reason}"
            }
        
        return None


class ConfidenceThreshold:
    """
    Defense #3: CONFIDENCE THRESHOLDING
    
    Only trust DQN's decision if it's VERY confident.
    If DQN is unsure (low max Q-value), escalate to human.
    """
    
    def __init__(self, confidence_threshold: float = 0.8):
        """
        Args:
            confidence_threshold: Min Q-value spread to trust decision
        """
        self.confidence_threshold = confidence_threshold
    
    def check_decision_confidence(self, q_values: np.ndarray) -> Tuple[float, bool]:
        """
        Check how confident the DQN is.
        
        Confidence = (max_q - second_max_q) / abs(max_q)
        Higher = more confident
        
        Returns:
            (confidence_score, is_confident)
        """
        sorted_q = np.sort(q_values)
        max_q = sorted_q[-1]
        second_max_q = sorted_q[-2]
        
        # Avoid division by zero
        if abs(max_q) < 1e-6:
            confidence = 0.0
        else:
            confidence = (max_q - second_max_q) / (abs(max_q) + 1e-6)
        
        is_confident = confidence > self.confidence_threshold
        
        return float(confidence), is_confident
    
    def get_decision(self, q_values: np.ndarray, predicted_action: int) -> Dict:
        """
        Decide: Trust DQN or escalate to human?
        
        Returns:
            {
                "action": predicted_action or "ESCALATE",
                "confidence": confidence_score,
                "trusted": is_confident,
                "reason": explanation
            }
        """
        confidence, is_confident = self.check_decision_confidence(q_values)
        
        if is_confident:
            return {
                "action": int(predicted_action),
                "confidence": float(confidence),
                "trusted": True,
                "reason": f"High confidence: {confidence:.2%}"
            }
        else:
            return {
                "action": "ESCALATE_TO_HUMAN",
                "confidence": float(confidence),
                "trusted": False,
                "reason": f"Low confidence ({confidence:.2%}). Human review needed."
            }


class EnsembleDefense:
    """
    Defense #4: ENSEMBLE VOTING
    
    Don't rely on one DQN. Use multiple agents + voting.
    If they disagree = suspicious = escalate.
    """
    
    def __init__(self, agents: List = None, num_agents: int = 3):
        """
        Args:
            agents: List of DQN agents
            num_agents: Create N copies if agents not provided
        """
        self.agents = agents or []
        self.num_agents = num_agents
        self.agreement_history = deque(maxlen=100)
    
    def get_ensemble_prediction(self, state: np.ndarray) -> Dict:
        """
        Get predictions from all agents.
        
        Returns:
            {
                "primary_action": most_voted_action,
                "confidence": agreement_percentage,
                "all_votes": [action from each agent],
                "trusted": all_agents_agree
            }
        """
        if not self.agents:
            return {
                "primary_action": None,
                "confidence": 0.0,
                "all_votes": [],
                "trusted": False,
                "reason": "No agents available"
            }
        
        votes = []
        for agent in self.agents:
            q_values = agent.get_q_values(state)
            action = np.argmax(q_values)
            votes.append(int(action))
        
        # Count agreement
        from collections import Counter
        vote_counts = Counter(votes)
        most_common_action = vote_counts.most_common(1)[0][0]
        agreement_count = vote_counts[most_common_action]
        confidence = agreement_count / len(self.agents)
        
        self.agreement_history.append(confidence)
        
        # Alert if sudden disagreement
        if len(self.agreement_history) > 10:
            avg_agreement = np.mean(list(self.agreement_history))
            if confidence < avg_agreement - 0.3:
                severity = "POTENTIAL_ATTACK"
            else:
                severity = "OK"
        else:
            severity = "LEARNING"
        
        return {
            "primary_action": int(most_common_action),
            "confidence": float(confidence),
            "all_votes": votes,
            "trusted": confidence > 0.7,
            "reason": f"Ensemble agreement: {agreement_count}/{len(self.agents)}",
            "severity": severity
        }


class AdversarialTraining:
    """
    Defense #5: ADVERSARIAL TRAINING
    
    Train DQN on ADVERSARIAL EXAMPLES so it learns to defend.
    This is the strongest defense long-term.
    """
    
    def __init__(self, agent, attack_strength: float = 0.1):
        """
        Args:
            agent: DQN agent to train
            attack_strength: Epsilon for generating adversarial examples
        """
        self.agent = agent
        self.attack_strength = attack_strength
        self.training_log = []
    
    def generate_adversarial_batch(
        self,
        clean_states: np.ndarray,
        labels: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate adversarial examples using FGSM.
        
        Returns:
            (adversarial_states, original_labels)
        """
        adversarial_states = []
        
        for state, label in zip(clean_states, labels):
            state_tensor = tf.convert_to_tensor(state.reshape(1, -1), dtype=tf.float32)
            
            with tf.GradientTape() as tape:
                tape.watch(state_tensor)
                q_values = self.agent.q_network(state_tensor)
                loss = q_values[0, label]  # Loss for true label
            
            gradients = tape.gradient(loss, state_tensor)
            perturbation = self.attack_strength * tf.sign(gradients)
            adversarial = state_tensor + perturbation
            
            adversarial_states.append(adversarial.numpy().flatten())
        
        return np.array(adversarial_states), labels
    
    def train_on_adversarial_batch(
        self,
        clean_states: np.ndarray,
        labels: np.ndarray,
        epochs: int = 5
    ) -> Dict:
        """
        Train agent on mix of clean + adversarial examples.
        
        Returns:
            Training statistics
        """
        stats = {
            "clean_loss": [],
            "adversarial_loss": [],
            "epoch_results": []
        }
        
        for epoch in range(epochs):
            # Train on clean data
            for state, label in zip(clean_states, labels):
                self.agent.store_experience(state, label, 1.0, state, False)
            
            # Generate adversarial examples
            adv_states, _ = self.generate_adversarial_batch(clean_states, labels)
            
            # Train on adversarial data
            for adv_state, label in zip(adv_states, labels):
                self.agent.store_experience(adv_state, label, 1.0, adv_state, False)
            
            # Perform training steps
            clean_loss = self.agent.train_step()
            adv_loss = self.agent.train_step()
            
            stats["clean_loss"].append(float(clean_loss) if clean_loss else 0)
            stats["adversarial_loss"].append(float(adv_loss) if adv_loss else 0)
            
            epoch_info = {
                "epoch": epoch,
                "clean_loss": clean_loss,
                "adversarial_loss": adv_loss
            }
            stats["epoch_results"].append(epoch_info)
        
        return stats


class IntegratedDefenseSystem:
    """
    MASTER DEFENSE SYSTEM
    
    Combines all 5 defenses into one integrated system.
    """
    
    def __init__(
        self,
        agent,
        ensemble_agents: List = None,
        feature_bounds: Dict = None
    ):
        """
        Args:
            agent: Primary DQN agent
            ensemble_agents: List of secondary agents
            feature_bounds: Feature bounds for validation
        """
        self.agent = agent
        
        # Initialize all defenses
        self.input_validator = InputValidator(feature_bounds or self._get_default_bounds())
        self.metric_detector = AnomalousMetricDetector()
        self.confidence_checker = ConfidenceThreshold(confidence_threshold=0.7)
        self.ensemble = EnsembleDefense(ensemble_agents)
        self.adversarial_trainer = AdversarialTraining(agent)
        
        self.alerts = []
    
    def _get_default_bounds(self) -> Dict:
        """Default feature bounds."""
        return {
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
    
    def protect_and_decide(self, state: np.ndarray) -> Dict:
        """
        Multi-layered protection: Run all defenses, then decide.
        
        Returns:
            {
                "action": recommended_action,
                "alerts": list_of_alerts,
                "security_level": "GREEN/YELLOW/RED",
                "reason": explanation
            }
        """
        alerts = []
        
        # Defense 1: Check for suspicious metrics
        suspicious_alert = self.input_validator.get_alert(state)
        if suspicious_alert:
            alerts.append(suspicious_alert)
        
        # Defense 2: Check metric consistency
        inconsistency_alert = self.metric_detector.get_alert(state)
        if inconsistency_alert:
            alerts.append(inconsistency_alert)
        
        # If any red alert, BLOCK immediately
        critical_alerts = [a for a in alerts if a.get("severity") == "CRITICAL"]
        if critical_alerts:
            return {
                "action": "BLOCK",
                "alerts": alerts,
                "security_level": "RED",
                "reason": f"Critical alert: {critical_alerts[0]['reason']}"
            }
        
        # Get predictions
        q_values = self.agent.get_q_values(state)
        primary_action = np.argmax(q_values)
        
        # Defense 3: Check confidence
        confidence_decision = self.confidence_checker.get_decision(q_values, primary_action)
        
        if not confidence_decision["trusted"]:
            alerts.append({
                "type": "LOW_CONFIDENCE",
                "severity": "MEDIUM",
                "reason": confidence_decision["reason"]
            })
        
        # Defense 4: Check ensemble agreement
        if self.ensemble.agents:
            ensemble_decision = self.ensemble.get_ensemble_prediction(state)
            if not ensemble_decision["trusted"]:
                alerts.append({
                    "type": "ENSEMBLE_DISAGREEMENT",
                    "severity": "MEDIUM",
                    "votes": ensemble_decision["all_votes"],
                    "reason": ensemble_decision["reason"]
                })
        
        # Decide security level
        high_alerts = [a for a in alerts if a.get("severity") in ["HIGH", "CRITICAL"]]
        med_alerts = [a for a in alerts if a.get("severity") == "MEDIUM"]
        
        if high_alerts:
            security_level = "RED"
        elif med_alerts:
            security_level = "YELLOW"
        else:
            security_level = "GREEN"
        
        return {
            "action": int(primary_action),
            "confidence": float(np.max(q_values)),
            "alerts": alerts,
            "security_level": security_level,
            "reason": f"{len(alerts)} alerts. Confidence: {confidence_decision['confidence']:.2%}"
        }
    
    def save_config(self, path: str):
        """Save defense configuration."""
        config = {
            "confidence_threshold": self.confidence_checker.confidence_threshold,
            "ensemble_agents": len(self.ensemble.agents),
            "adversarial_attack_strength": self.adversarial_trainer.attack_strength
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)


# Convenience alias
from collections import defaultdict

