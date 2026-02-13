"""
Unit tests for ModelInterface.

Tests model loading, prediction, preprocessing, and error handling.
"""

import os
import sys
import pytest
import numpy as np
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.model_interface import ModelInterface
from src.data_models import FeatureVector, PredictionResult


class TestModelInterfaceInit:
    """Test ModelInterface initialization and model loading."""
    
    def test_init_with_valid_model_path(self):
        """Test initialization with a valid model file."""
        # Use the actual model path
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        assert model_interface.is_loaded()
        assert model_interface.model is not None
        assert model_interface.input_shape is not None
    
    def test_init_with_missing_model_file(self):
        """Test initialization with non-existent model file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ModelInterface("/nonexistent/path/model.h5")
        
        assert "Model file not found" in str(exc_info.value)
    
    @patch('src.model_interface.tf', None)
    def test_init_without_tensorflow(self):
        """Test initialization when TensorFlow is not installed."""
        with pytest.raises(ImportError) as exc_info:
            ModelInterface("dummy_path.h5")
        
        assert "TensorFlow is not installed" in str(exc_info.value)


class TestModelInterfaceIsLoaded:
    """Test is_loaded() method."""
    
    def test_is_loaded_returns_true_when_model_loaded(self):
        """Test is_loaded returns True when model is successfully loaded."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        assert model_interface.is_loaded() is True
    
    def test_is_loaded_returns_false_when_model_not_loaded(self):
        """Test is_loaded returns False when model is None."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        model_interface.model = None
        
        assert model_interface.is_loaded() is False


class TestModelInterfacePreprocess:
    """Test _preprocess() method."""
    
    def test_preprocess_converts_feature_vector_to_numpy_array(self):
        """Test preprocessing converts FeatureVector to numpy array."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface._preprocess(fv)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 4)  # Batch size 1, 4 features
        assert result.dtype == np.float32
    
    def test_preprocess_correct_feature_order(self):
        """Test preprocessing uses correct feature order."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=25,
            failed_logins=5,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface._preprocess(fv)
        
        # Expected order: [failed_logins, process_count, cpu_usage, network_connections]
        expected = np.array([[5.0, 100.0, 50.0, 25.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_preprocess_rejects_nan_values(self):
        """Test preprocessing rejects NaN values."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=float('nan'),
            memory_usage=60.0,
            process_count=100,
            network_connections=25,
            failed_logins=5,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        with pytest.raises(ValueError) as exc_info:
            model_interface._preprocess(fv)
        
        assert "invalid values" in str(exc_info.value).lower()
    
    def test_preprocess_rejects_inf_values(self):
        """Test preprocessing rejects infinite values."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=float('inf'),
            failed_logins=5,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        with pytest.raises(ValueError) as exc_info:
            model_interface._preprocess(fv)
        
        assert "invalid values" in str(exc_info.value).lower()


class TestModelInterfacePredict:
    """Test predict() method."""
    
    def test_predict_returns_prediction_result(self):
        """Test predict returns a PredictionResult object."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert isinstance(result, PredictionResult)
        assert hasattr(result, 'anomaly_score')
        assert hasattr(result, 'label')
        assert hasattr(result, 'confidence')
    
    def test_predict_anomaly_score_in_valid_range(self):
        """Test predict returns anomaly score in [0, 1] range."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert 0.0 <= result.anomaly_score <= 1.0
    
    def test_predict_label_is_valid(self):
        """Test predict returns valid label ('normal' or 'anomaly')."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert result.label in ['normal', 'anomaly']
    
    def test_predict_confidence_in_valid_range(self):
        """Test predict returns confidence in [0, 1] range."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert 0.0 <= result.confidence <= 1.0
    
    def test_predict_raises_error_when_model_not_loaded(self):
        """Test predict raises RuntimeError when model is not loaded."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        model_interface.model = None
        
        fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        with pytest.raises(RuntimeError) as exc_info:
            model_interface.predict(fv)
        
        assert "Model is not loaded" in str(exc_info.value)
    
    def test_predict_with_high_anomaly_values(self):
        """Test prediction with high anomaly indicators."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        # High values that should indicate anomaly
        fv = FeatureVector(
            cpu_usage=95.0,
            memory_usage=92.0,
            process_count=500,
            network_connections=200,
            failed_logins=25,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        # Just verify it returns valid results, not testing model accuracy
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.anomaly_score <= 1.0
        assert result.label in ['normal', 'anomaly']
    
    def test_predict_with_normal_values(self):
        """Test prediction with normal system values."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        # Normal values
        fv = FeatureVector(
            cpu_usage=25.0,
            memory_usage=40.0,
            process_count=80,
            network_connections=15,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        # Just verify it returns valid results
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.anomaly_score <= 1.0
        assert result.label in ['normal', 'anomaly']


class TestModelInterfaceEdgeCases:
    """Test edge cases and error handling."""
    
    def test_predict_with_zero_values(self):
        """Test prediction with all zero values."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=0.0,
            memory_usage=0.0,
            process_count=0,
            network_connections=0,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.anomaly_score <= 1.0
    
    def test_predict_with_maximum_values(self):
        """Test prediction with maximum valid values."""
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "best_model.h5"
        
        if not model_path.exists():
            pytest.skip("Model file not found, skipping test")
        
        model_interface = ModelInterface(str(model_path))
        
        fv = FeatureVector(
            cpu_usage=100.0,
            memory_usage=100.0,
            process_count=1000,
            network_connections=1000,
            failed_logins=100,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        result = model_interface.predict(fv)
        
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.anomaly_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
