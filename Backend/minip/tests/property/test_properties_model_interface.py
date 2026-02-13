"""
Property-based tests for ModelInterface.

Tests universal properties that should hold for all valid inputs.
"""

import os
import sys
import pytest
import numpy as np
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings, strategies as st, assume

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.model_interface import ModelInterface
from src.data_models import FeatureVector, PredictionResult


# Strategy for generating valid FeatureVectors
@st.composite
def feature_vector_strategy(draw):
    """Generate random valid FeatureVectors."""
    return FeatureVector(
        cpu_usage=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        memory_usage=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        process_count=draw(st.integers(min_value=0, max_value=1000)),
        network_connections=draw(st.integers(min_value=0, max_value=1000)),
        failed_logins=draw(st.integers(min_value=0, max_value=100)),
        timestamp=datetime.utcnow().isoformat() + 'Z',
        node_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    )


# Strategy for generating invalid FeatureVectors (with NaN or Inf)
@st.composite
def invalid_feature_vector_strategy(draw):
    """Generate FeatureVectors with invalid values (NaN or Inf)."""
    # Choose which field to make invalid
    invalid_field = draw(st.sampled_from(['cpu', 'memory', 'network']))
    invalid_value = draw(st.sampled_from([float('nan'), float('inf'), float('-inf')]))
    
    cpu = invalid_value if invalid_field == 'cpu' else draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    memory = invalid_value if invalid_field == 'memory' else draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    network = invalid_value if invalid_field == 'network' else draw(st.integers(min_value=0, max_value=1000))
    
    return FeatureVector(
        cpu_usage=cpu,
        memory_usage=memory,
        process_count=draw(st.integers(min_value=0, max_value=1000)),
        network_connections=int(network) if not np.isinf(network) and not np.isnan(network) else 0,
        failed_logins=draw(st.integers(min_value=0, max_value=100)),
        timestamp=datetime.utcnow().isoformat() + 'Z'
    )


@pytest.fixture(scope="module")
def model_interface():
    """Fixture to load model once for all tests."""
    project_root = Path(__file__).parent.parent.parent
    model_path = project_root / "models" / "best_model.h5"
    
    if not model_path.exists():
        pytest.skip("Model file not found, skipping property tests")
    
    return ModelInterface(str(model_path))


class TestModelInterfaceProperties:
    """Property-based tests for ModelInterface."""
    
    @settings(max_examples=50, deadline=500)
    @given(fv=feature_vector_strategy())
    def test_property_13_prediction_score_range(self, model_interface, fv):
        """
        Property 13: Model Prediction Score Range
        
        **Validates: Requirements 6.4, 6.5**
        
        For any valid FeatureVector passed to Model_Interface, 
        the returned anomaly_score should be in the range [0, 1].
        """
        result = model_interface.predict(fv)
        
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.anomaly_score <= 1.0, \
            f"Anomaly score {result.anomaly_score} is outside [0, 1] range"
    
    @settings(max_examples=50, deadline=None)
    @given(fv=feature_vector_strategy())
    def test_property_14_prediction_label_validity(self, model_interface, fv):
        """
        Property 14: Model Prediction Label Validity
        
        **Validates: Requirements 6.6**
        
        For any prediction result, the label should be either 'normal' or 'anomaly'.
        """
        result = model_interface.predict(fv)
        
        assert result.label in ['normal', 'anomaly'], \
            f"Invalid label: {result.label}"
    
    @settings(max_examples=50, deadline=None)
    @given(fv=feature_vector_strategy())
    def test_property_15_prediction_error_handling(self, model_interface, fv):
        """
        Property 15: Model Prediction Error Handling
        
        **Validates: Requirements 6.7**
        
        For any prediction that fails (invalid input, model error), 
        the Model_Interface should return an error status rather than crashing.
        
        This test verifies that valid inputs don't cause crashes.
        """
        try:
            result = model_interface.predict(fv)
            # Should succeed without raising exceptions
            assert isinstance(result, PredictionResult)
        except (ValueError, RuntimeError) as e:
            # These are acceptable error types for invalid inputs
            assert "invalid" in str(e).lower() or "not loaded" in str(e).lower()
        except Exception as e:
            # Any other exception is a failure
            pytest.fail(f"Unexpected exception type: {type(e).__name__}: {e}")
    
    @settings(max_examples=30)
    @given(fv=invalid_feature_vector_strategy())
    def test_property_15_invalid_input_handling(self, model_interface, fv):
        """
        Property 15: Model Prediction Error Handling (Invalid Inputs)
        
        **Validates: Requirements 6.7**
        
        For any prediction with invalid input (NaN, Inf), 
        the Model_Interface should raise ValueError rather than crashing.
        """
        # Check if the feature vector actually has invalid values
        # (the strategy might generate edge cases where conversion makes them valid)
        model_input = fv.to_model_input()
        has_invalid = any(not np.isfinite(x) for x in model_input)
        
        if has_invalid:
            with pytest.raises(ValueError) as exc_info:
                model_interface.predict(fv)
            
            assert "invalid" in str(exc_info.value).lower()
        else:
            # If no invalid values, prediction should succeed
            result = model_interface.predict(fv)
            assert isinstance(result, PredictionResult)
    
    @settings(max_examples=50)
    @given(fv=feature_vector_strategy())
    def test_preprocess_output_shape(self, model_interface, fv):
        """
        Test that preprocessing always produces correct output shape.
        
        For any valid FeatureVector, preprocessing should produce
        a numpy array with shape (1, 4).
        """
        result = model_interface._preprocess(fv)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 4), \
            f"Expected shape (1, 4), got {result.shape}"
        assert result.dtype == np.float32
    
    @settings(max_examples=50)
    @given(fv=feature_vector_strategy())
    def test_preprocess_feature_order_consistency(self, model_interface, fv):
        """
        Test that preprocessing maintains consistent feature order.
        
        For any FeatureVector, the preprocessed array should have features
        in the order: [failed_logins, process_count, cpu_usage, network_connections]
        """
        result = model_interface._preprocess(fv)
        
        expected = np.array([[
            float(fv.failed_logins),
            float(fv.process_count),
            fv.cpu_usage,
            float(fv.network_connections)
        ]], dtype=np.float32)
        
        np.testing.assert_array_almost_equal(result, expected, decimal=5)
    
    @settings(max_examples=50)
    @given(fv=feature_vector_strategy())
    def test_confidence_calculation_consistency(self, model_interface, fv):
        """
        Test that confidence is calculated consistently.
        
        For any prediction, confidence should be the distance from
        the decision boundary (0.5) scaled to [0, 1].
        """
        result = model_interface.predict(fv)
        
        # Confidence should be abs(score - 0.5) * 2
        expected_confidence = abs(result.anomaly_score - 0.5) * 2.0
        
        assert abs(result.confidence - expected_confidence) < 0.001, \
            f"Confidence {result.confidence} doesn't match expected {expected_confidence}"
    
    @settings(max_examples=50, deadline=None)
    @given(fv=feature_vector_strategy())
    def test_label_threshold_consistency(self, model_interface, fv):
        """
        Test that label is determined consistently by threshold.
        
        For any prediction, if score >= 0.5, label should be 'anomaly',
        otherwise 'normal'.
        """
        result = model_interface.predict(fv)
        
        if result.anomaly_score >= 0.5:
            assert result.label == 'anomaly', \
                f"Score {result.anomaly_score} >= 0.5 should be 'anomaly', got '{result.label}'"
        else:
            assert result.label == 'normal', \
                f"Score {result.anomaly_score} < 0.5 should be 'normal', got '{result.label}'"
    
    @settings(max_examples=30, deadline=None)
    @given(
        cpu=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        memory=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        processes=st.integers(min_value=0, max_value=1000),
        connections=st.integers(min_value=0, max_value=1000),
        failed=st.integers(min_value=0, max_value=100)
    )
    def test_prediction_determinism(self, model_interface, cpu, memory, processes, connections, failed):
        """
        Test that predictions are deterministic.
        
        For any given FeatureVector, running prediction twice should
        produce the same result.
        """
        fv = FeatureVector(
            cpu_usage=cpu,
            memory_usage=memory,
            process_count=processes,
            network_connections=connections,
            failed_logins=failed,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result1 = model_interface.predict(fv)
        result2 = model_interface.predict(fv)
        
        assert abs(result1.anomaly_score - result2.anomaly_score) < 0.0001, \
            "Predictions should be deterministic"
        assert result1.label == result2.label
        assert abs(result1.confidence - result2.confidence) < 0.0001


class TestModelInterfaceLoadingProperties:
    """Property-based tests for model loading."""
    
    @settings(max_examples=10)
    @given(invalid_path=st.text(min_size=1, max_size=50))
    def test_invalid_path_raises_error(self, invalid_path):
        """
        Test that invalid model paths raise FileNotFoundError.
        
        For any non-existent path, ModelInterface should raise
        FileNotFoundError rather than crashing.
        """
        # Ensure path doesn't accidentally exist
        assume(not os.path.exists(invalid_path))
        
        with pytest.raises(FileNotFoundError) as exc_info:
            ModelInterface(invalid_path)
        
        assert "Model file not found" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
