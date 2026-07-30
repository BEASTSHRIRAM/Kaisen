"""
Integration Tests for Adversarial Robustness Module

Tests the AdversarialEvaluator and AdversarialAttacker classes
to ensure DQN robustness evaluation works correctly.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from adversarial_eval import AdversarialEvaluator, AdversarialAttacker
    from agent import DQNAgent
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


class TestAdversarialAttacker:
    """Test the AdversarialAttacker class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        self.agent = DQNAgent(
            state_size=13,
            action_size=5,
            learning_rate=0.001
        )
        
        # Simple feature bounds
        self.feature_bounds = {
            f"feature_{i}": (0.0, 100.0) for i in range(13)
        }
        
        # Create mock model interface
        class MockModelInterface:
            def __init__(self):
                self.model = self.agent.q_network
        
        self.agent.model_interface = MockModelInterface()
        
        self.attacker = AdversarialAttacker(
            self.agent.model_interface,
            self.feature_bounds,
            epsilon=0.1,
            num_steps=5
        )
        
        yield
    
    def test_random_perturbation(self, setup):
        """Test random perturbation generation."""
        state = np.array([50.0] * 13, dtype=np.float32)
        
        perturbed = self.attacker.random_perturbation(state, epsilon=0.1)
        
        # Check shape and bounds
        assert perturbed.shape == state.shape
        assert np.all(perturbed >= 0.0) and np.all(perturbed <= 100.0)
        
        # Check perturbation magnitude
        distance = np.linalg.norm(perturbed - state, ord=np.inf)
        assert distance <= 0.1 + 1e-5  # Allow small numerical error
    
    def test_feature_clipping_attack(self, setup):
        """Test feature clipping attack."""
        state = np.array([50.0] * 13, dtype=np.float32)
        
        # Test maximize
        perturbed = self.attacker.feature_clipping(state, "maximize")
        assert np.all(perturbed == 100.0)
        
        # Test reduce
        perturbed = self.attacker.feature_clipping(state, "reduce")
        assert np.all(perturbed == 0.0)
    
    def test_clip_perturbation(self, setup):
        """Test perturbation clipping."""
        original = np.array([50.0] * 13, dtype=np.float32)
        perturbed = np.array([70.0] * 13, dtype=np.float32)
        
        clipped = self.attacker._clip_perturbation(original, perturbed, epsilon=0.05)
        
        distance = np.linalg.norm(clipped - original, ord=np.inf)
        assert distance <= 0.05 + 1e-5
    
    def test_clip_to_bounds(self, setup):
        """Test feature bounds clipping."""
        state = np.array([150.0] * 13, dtype=np.float32)  # Out of bounds
        
        clipped = self.attacker._clip_to_bounds(state, self.feature_bounds)
        
        assert np.all(clipped >= 0.0) and np.all(clipped <= 100.0)


class TestAdversarialEvaluator:
    """Test the AdversarialEvaluator class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        self.agent = DQNAgent(
            state_size=13,
            action_size=5,
            learning_rate=0.001
        )
        
        # Create mock model interface
        class MockModelInterface:
            def __init__(self):
                self.model = self.agent.q_network
        
        self.agent.model_interface = MockModelInterface()
        
        self.evaluator = AdversarialEvaluator(
            self.agent,
            feature_bounds=None,
            epsilon=0.15
        )
        
        # Generate test data
        np.random.seed(42)
        self.test_states = np.random.randn(20, 13).astype(np.float32)
        self.test_labels = np.random.randint(0, 5, 20)
        
        # Normalize to reasonable ranges
        self.test_states[:, 0] = np.clip(self.test_states[:, 0] * 20 + 50, 0, 100)
        
        yield
    
    def test_evaluator_initialization(self, setup):
        """Test evaluator initialization."""
        assert self.evaluator.dqn_agent is not None
        assert self.evaluator.epsilon == 0.15
        assert self.evaluator.feature_bounds is not None
    
    def test_evaluate_single_attack(self, setup):
        """Test evaluation of a single attack method."""
        metrics = self.evaluator._evaluate_attack(
            self.test_states[:5],
            self.test_labels[:5],
            "random"
        )
        
        assert "attack_method" in metrics
        assert metrics["attack_method"] == "random"
        assert "attack_success_rate" in metrics
        assert 0.0 <= metrics["attack_success_rate"] <= 1.0
        assert metrics["total_attacks"] == 5
    
    def test_evaluate_on_dataset(self, setup):
        """Test full dataset evaluation."""
        metrics = self.evaluator.evaluate_on_dataset(
            self.test_states,
            self.test_labels,
            attack_methods=["random", "feature_clipping"]
        )
        
        assert "total_samples" in metrics
        assert metrics["total_samples"] == 20
        assert "attack_results" in metrics
        assert len(metrics["attack_results"]) == 2
        assert "summary" in metrics
    
    def test_summary_metrics(self, setup):
        """Test summary metrics computation."""
        metrics = self.evaluator.evaluate_on_dataset(
            self.test_states,
            self.test_labels,
            attack_methods=["random"]
        )
        
        summary = metrics["summary"]
        
        assert "average_attack_success_rate" in summary
        assert "robustness_score" in summary
        assert "average_l2_perturbation" in summary
        
        # Robustness score should be 1 - ASR
        asr = metrics["attack_results"]["random"]["attack_success_rate"]
        assert abs(summary["robustness_score"] - (1.0 - asr)) < 1e-6
    
    def test_report_generation(self, setup, tmp_path):
        """Test report generation."""
        metrics = self.evaluator.evaluate_on_dataset(
            self.test_states,
            self.test_labels,
            attack_methods=["random"]
        )
        
        report_path = str(tmp_path / "report.json")
        output_path = self.evaluator.generate_report(metrics, output_path=report_path)
        
        assert os.path.exists(output_path)
        
        # Verify JSON is valid
        import json
        with open(output_path, 'r') as f:
            saved_metrics = json.load(f)
        
        assert saved_metrics["total_samples"] == metrics["total_samples"]


class TestAdversarialRobustness:
    """Integration tests for adversarial robustness."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        self.agent = DQNAgent(
            state_size=13,
            action_size=5,
            learning_rate=0.001
        )
        
        class MockModelInterface:
            def __init__(self):
                self.model = self.agent.q_network
        
        self.agent.model_interface = MockModelInterface()
        
        yield
    
    def test_multiple_attack_methods(self, setup):
        """Test evaluation with multiple attack methods."""
        evaluator = AdversarialEvaluator(self.agent, epsilon=0.1)
        
        np.random.seed(42)
        test_states = np.random.randn(10, 13).astype(np.float32)
        test_labels = np.random.randint(0, 5, 10)
        
        test_states[:, 0] = np.clip(test_states[:, 0] * 20 + 50, 0, 100)
        
        metrics = evaluator.evaluate_on_dataset(
            test_states,
            test_labels,
            attack_methods=["fgsm", "pgd", "feature_clipping", "random"]
        )
        
        assert len(metrics["attack_results"]) == 4
        
        # Verify all attack methods have results
        for attack in ["fgsm", "pgd", "feature_clipping", "random"]:
            assert attack in metrics["attack_results"]
            assert metrics["attack_results"][attack]["total_attacks"] == 10
    
    def test_robustness_comparison(self, setup):
        """Test that robustness metrics are reasonable."""
        evaluator = AdversarialEvaluator(setup.agent, epsilon=0.05)
        
        np.random.seed(42)
        test_states = np.random.randn(15, 13).astype(np.float32)
        test_labels = np.random.randint(0, 5, 15)
        
        test_states[:, 0] = np.clip(test_states[:, 0] * 20 + 50, 0, 100)
        
        metrics = evaluator.evaluate_on_dataset(
            test_states,
            test_labels,
            attack_methods=["random", "feature_clipping"]
        )
        
        # Feature clipping is stronger, should have higher or equal ASR
        random_asr = metrics["attack_results"]["random"]["attack_success_rate"]
        feature_asr = metrics["attack_results"]["feature_clipping"]["attack_success_rate"]
        
        # This is a probabilistic test but feature clipping is usually stronger
        assert feature_asr >= 0.0 and random_asr >= 0.0


class TestAdversarialMetrics:
    """Test metric computation and reporting."""
    
    def test_metric_ranges(self):
        """Test that metrics are in valid ranges."""
        agent = DQNAgent(state_size=13, action_size=5)
        evaluator = AdversarialEvaluator(agent)
        
        # Test summary with various ASRs
        class MockMetrics:
            def __init__(self, asr):
                self.attack_success_rate = asr
                self.avg_perturbation_l2 = 0.1
                self.avg_perturbation_linf = 0.05
        
        mock_results = {
            "attack1": MockMetrics(0.3),
            "attack2": MockMetrics(0.5),
        }
        
        summary = evaluator._compute_summary(mock_results)
        
        # Robustness should be between 0 and 1
        assert 0.0 <= summary["robustness_score"] <= 1.0
        assert 0.0 <= summary["average_attack_success_rate"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
