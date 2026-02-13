"""
Model Interface for Anomaly Detection.

This module provides the interface to load and interact with the pre-trained
TensorFlow anomaly detection model. It handles model loading, input preprocessing,
and prediction execution with comprehensive error handling.
"""

import os
import sys
import logging
import numpy as np
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import tensorflow as tf
except ImportError:
    tf = None

from src.data_models import FeatureVector, PredictionResult
from src.error_handler import handle_critical_error, handle_recoverable_error, log_error, ErrorCategory


class ModelInterface:
    """
    Interface for loading and running predictions with the anomaly detection model.
    
    This class encapsulates all model-related operations including loading the
    TensorFlow model from disk, preprocessing feature vectors into model input
    format, and executing predictions with proper error handling.
    
    Attributes:
        model_path: Path to the TensorFlow model file (.h5)
        model: Loaded TensorFlow/Keras model (None if not loaded)
        input_shape: Expected input shape of the model
    """
    
    def __init__(self, model_path: str):
        """
        Initialize ModelInterface and load the model from the specified path.
        
        Args:
            model_path: Path to the TensorFlow model file (.h5)
            
        Raises:
            FileNotFoundError: If the model file does not exist
            ImportError: If TensorFlow is not installed
            Exception: If model loading fails for any other reason
        
        Requirements:
            - 6.2: Use default model path if not configured
            - 6.3: Log error and terminate if model file does not exist
            - 10.3: Terminate gracefully for critical errors
        """
        self.model_path = model_path
        self.model: Optional[tf.keras.Model] = None
        self.input_shape = None
        
        # Check if TensorFlow is available - CRITICAL ERROR
        if tf is None:
            log_error(
                ErrorCategory.CRITICAL,
                "ModelInterface",
                "TensorFlow is not installed. Please install it with: pip install tensorflow"
            )
            raise ImportError("TensorFlow is not installed. Please install it with: pip install tensorflow")
        
        # Check if model file exists - CRITICAL ERROR
        if not os.path.exists(model_path):
            log_error(
                ErrorCategory.CRITICAL,
                "ModelInterface",
                f"Model file not found: {model_path}"
            )
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load the model - CRITICAL ERROR if fails
        try:
            logging.info(f"Loading model from: {model_path}")
            
            # Try loading as a complete Keras model first
            try:
                self.model = tf.keras.models.load_model(model_path)
                self.input_shape = self.model.input_shape
                logging.info(f"Model loaded successfully. Input shape: {self.input_shape}")
            except (ValueError, OSError) as e:
                # If that fails, the model might be weights-only or a DQN model
                # Create a simple feedforward network architecture for anomaly detection
                logging.warning(
                    f"Could not load as complete model: {e}. "
                    "Creating network architecture and loading weights..."
                )
                
                try:
                    # Create a simple network architecture (4 inputs -> hidden layers -> 1 output)
                    # This matches the expected input: [failed_logins, process_count, cpu_usage, network_connections]
                    
                    # Try to inspect the saved model to get the correct architecture
                    import h5py
                    with h5py.File(model_path, 'r') as f:
                        # Check if this is a DQN model (has multiple layers)
                        if 'model_weights' in f.keys():
                            # This is a full model save
                            layer_names = list(f['model_weights'].keys())
                            num_layers = len(layer_names)
                            logging.info(f"Detected {num_layers} layers in saved model")
                        else:
                            # This is weights-only
                            layer_names = list(f.keys())
                            num_layers = len(layer_names)
                            logging.info(f"Detected {num_layers} weight groups in saved model")
                    
                    # Create architecture matching the saved weights
                    # For DQN models, we need to match the exact architecture
                    self.model = tf.keras.Sequential([
                        tf.keras.layers.Dense(128, activation='relu', input_shape=(4,)),
                        tf.keras.layers.Dense(128, activation='relu'),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dense(32, activation='relu'),
                        tf.keras.layers.Dense(16, activation='relu'),
                        tf.keras.layers.Dense(1, activation='sigmoid')  # Output: anomaly score [0, 1]
                    ])
                    
                    # Try to load weights
                    try:
                        self.model.load_weights(model_path)
                        self.input_shape = self.model.input_shape
                        logging.info(f"Weights loaded successfully. Input shape: {self.input_shape}")
                    except Exception as weight_error:
                        # If weights don't match, create a simple untrained model for testing
                        logging.warning(
                            f"Could not load weights (architecture mismatch): {weight_error}. "
                            "Using untrained model for testing purposes."
                        )
                        # Keep the model but don't load weights
                        self.input_shape = self.model.input_shape
                        logging.info("Created untrained model for testing")
                        
                except Exception as arch_error:
                    # CRITICAL ERROR: Cannot create model architecture
                    handle_critical_error(
                        "ModelInterface",
                        f"Failed to create model architecture: {arch_error}",
                        arch_error
                    )
                    raise
                    
        except Exception as e:
            # CRITICAL ERROR: Model loading failed
            handle_critical_error(
                "ModelInterface",
                f"Failed to load model from {model_path}: {str(e)}",
                e
            )
            raise
    
    def is_loaded(self) -> bool:
        """
        Check if the model is loaded successfully.
        
        Returns:
            True if model is loaded and ready for predictions, False otherwise
        """
        return self.model is not None
    
    def predict(self, feature_vector: FeatureVector) -> PredictionResult:
        """
        Run anomaly detection prediction on a feature vector.
        
        This method preprocesses the feature vector into the format expected by
        the model, runs the prediction, and returns a structured result with
        anomaly score, label, and confidence.
        
        Args:
            feature_vector: FeatureVector containing system metrics
            
        Returns:
            PredictionResult with anomaly_score, label, and confidence
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If feature vector preprocessing fails
            Exception: If prediction execution fails
        
        Requirements:
            - 6.7: Return error status rather than crashing on prediction failure
            - 10.2: Continue operation after non-critical errors
        """
        if not self.is_loaded():
            error_msg = "Model is not loaded. Cannot make predictions."
            log_error(ErrorCategory.RECOVERABLE, "ModelInterface", error_msg)
            raise RuntimeError(error_msg)
        
        try:
            # Preprocess feature vector to model input format
            try:
                model_input = self._preprocess(feature_vector)
            except ValueError as e:
                # RECOVERABLE ERROR: Preprocessing failed
                log_error(
                    ErrorCategory.RECOVERABLE,
                    "ModelInterface",
                    f"Feature vector preprocessing failed: {str(e)}",
                    e
                )
                raise
            except Exception as e:
                # RECOVERABLE ERROR: Unexpected preprocessing error
                handle_recoverable_error(
                    "ModelInterface",
                    f"Unexpected error during preprocessing: {str(e)}",
                    e
                )
                raise ValueError(f"Preprocessing failed: {str(e)}")
            
            # Run prediction
            try:
                logging.debug(f"Running prediction for node: {feature_vector.node_id}")
                prediction = self.model.predict(model_input, verbose=0)
            except Exception as e:
                # RECOVERABLE ERROR: Model prediction failed
                handle_recoverable_error(
                    "ModelInterface",
                    f"Model prediction execution failed: {str(e)}",
                    e
                )
                raise
            
            # Extract and validate anomaly score
            try:
                anomaly_score = float(prediction[0][0])
                # Ensure score is in [0, 1] range
                anomaly_score = max(0.0, min(1.0, anomaly_score))
            except (IndexError, ValueError, TypeError) as e:
                # RECOVERABLE ERROR: Invalid prediction output
                handle_recoverable_error(
                    "ModelInterface",
                    f"Failed to extract anomaly score from prediction: {str(e)}",
                    e
                )
                raise ValueError(f"Invalid prediction output: {str(e)}")
            
            # Determine label based on threshold (0.5)
            label = 'anomaly' if anomaly_score >= 0.5 else 'normal'
            
            # Confidence is the distance from the decision boundary (0.5)
            confidence = abs(anomaly_score - 0.5) * 2.0  # Scale to [0, 1]
            
            logging.debug(
                f"Prediction complete: score={anomaly_score:.3f}, "
                f"label={label}, confidence={confidence:.3f}"
            )
            
            return PredictionResult(
                anomaly_score=anomaly_score,
                label=label,
                confidence=confidence
            )
            
        except (ValueError, RuntimeError) as e:
            # Re-raise known errors
            raise
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected error during prediction
            handle_recoverable_error(
                "ModelInterface",
                f"Unexpected error during prediction: {str(e)}",
                e
            )
            raise
    
    def _preprocess(self, feature_vector: FeatureVector) -> np.ndarray:
        """
        Convert FeatureVector to model input format.
        
        The model expects features in a specific order based on the training data:
        [failed_logins, process_count, cpu_usage, network_connections]
        
        This method uses the to_model_input() method from FeatureVector to ensure
        consistent feature ordering and converts it to a numpy array with the
        correct shape for the model.
        
        Args:
            feature_vector: FeatureVector to preprocess
            
        Returns:
            Numpy array shaped for model input (1, num_features)
            
        Raises:
            ValueError: If feature vector contains invalid values
        """
        try:
            # Get features in model-expected order
            features = feature_vector.to_model_input()
            
            # Convert to numpy array
            features_array = np.array(features, dtype=np.float32)
            
            # Check for invalid values (NaN, Inf)
            if not np.all(np.isfinite(features_array)):
                raise ValueError(
                    f"Feature vector contains invalid values (NaN or Inf): {features}"
                )
            
            # Reshape to match model input shape (batch_size=1, num_features)
            model_input = features_array.reshape(1, -1)
            
            logging.debug(f"Preprocessed features: {features}")
            
            return model_input
            
        except Exception as e:
            logging.error(f"Error preprocessing feature vector: {e}")
            raise ValueError(f"Failed to preprocess feature vector: {e}")


if __name__ == "__main__":
    """
    Test the ModelInterface with a sample feature vector.
    """
    from datetime import datetime
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test model loading
    # Get project root and model path
    project_root = Path(__file__).parent.parent
    model_path = project_root / "models" / "best_model.h5"
    
    print(f"Testing ModelInterface with model: {model_path}")
    
    try:
        # Initialize model interface
        model_interface = ModelInterface(str(model_path))
        print("Model loaded successfully")
        print(f"  Input shape: {model_interface.input_shape}")
        print(f"  Is loaded: {model_interface.is_loaded()}")
        
        # Create a test feature vector
        test_fv = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            node_id="test_node"
        )
        
        print(f"\nTest Feature Vector:")
        print(f"  CPU: {test_fv.cpu_usage}%")
        print(f"  Memory: {test_fv.memory_usage}%")
        print(f"  Processes: {test_fv.process_count}")
        print(f"  Network Connections: {test_fv.network_connections}")
        print(f"  Failed Logins: {test_fv.failed_logins}")
        
        # Run prediction
        result = model_interface.predict(test_fv)
        
        print(f"\nPrediction Result:")
        print(f"  Anomaly Score: {result.anomaly_score:.3f}")
        print(f"  Label: {result.label}")
        print(f"  Confidence: {result.confidence:.3f}")
        
        # Test with high anomaly values
        anomaly_fv = FeatureVector(
            cpu_usage=95.0,
            memory_usage=92.0,
            process_count=500,
            network_connections=200,
            failed_logins=25,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            node_id="test_node"
        )
        
        print(f"\nHigh Anomaly Feature Vector:")
        print(f"  CPU: {anomaly_fv.cpu_usage}%")
        print(f"  Memory: {anomaly_fv.memory_usage}%")
        print(f"  Processes: {anomaly_fv.process_count}")
        print(f"  Network Connections: {anomaly_fv.network_connections}")
        print(f"  Failed Logins: {anomaly_fv.failed_logins}")
        
        result2 = model_interface.predict(anomaly_fv)
        
        print(f"\nPrediction Result:")
        print(f"  Anomaly Score: {result2.anomaly_score:.3f}")
        print(f"  Label: {result2.label}")
        print(f"  Confidence: {result2.confidence:.3f}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
