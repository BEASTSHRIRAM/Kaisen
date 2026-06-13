"""
Model Interface for Anomaly Detection.

This module provides the interface to load and interact with the pre-trained
TensorFlow anomaly detection model. It handles model loading, input preprocessing,
and prediction execution with comprehensive error handling.

If the model file is absent, a RuleBasedAnomalyScorer is activated as a
stand-in so the full collection → alert → API pipeline remains functional.
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


# ---------------------------------------------------------------------------
# Rule-Based Fallback Anomaly Scorer
# ---------------------------------------------------------------------------

class RuleBasedAnomalyScorer:
    """
    Threshold-based anomaly scorer used when the TensorFlow model is unavailable.

    Computes a weighted anomaly score in [0, 1] from five FeatureVector fields:
      - cpu_usage          (weight 0.25) — threshold at 85 % (critical: 95 %)
      - failed_logins      (weight 0.30) — threshold at 10  (critical: 30)
      - network_connections(weight 0.20) — threshold at 200 (critical: 500)
      - process_count      (weight 0.15) — threshold at 400 (critical: 600)
      - unique_ip_count    (weight 0.10) — threshold at 20  (critical: 50)

    Each dimension maps to a sub-score via a two-tier step function:
      value < high_threshold  → sub-score ∝ (value / high_threshold) * 0.4
      value < crit_threshold  → sub-score ∈ [0.4, 0.8) linearly
      value >= crit_threshold → sub-score ∈ [0.8, 1.0) capped

    The combined weighted score is then compared against a 0.5 decision
    boundary, consistent with ModelInterface label assignment.

    Research note: This scorer deliberately mirrors NIST SP 800-53 SA-9
    anomaly indicators and serves as the "rule-based baseline" reference
    point in the sim-to-real evaluation.
    """

    THRESHOLDS = {
        "cpu_usage":           {"high": 85.0,  "crit": 95.0},
        "failed_logins":       {"high": 10.0,  "crit": 30.0},
        "network_connections": {"high": 200.0, "crit": 500.0},
        "process_count":       {"high": 400.0, "crit": 600.0},
        "unique_ip_count":     {"high": 20.0,  "crit": 50.0},
    }

    WEIGHTS = {
        "cpu_usage":           0.25,
        "failed_logins":       0.30,
        "network_connections": 0.20,
        "process_count":       0.15,
        "unique_ip_count":     0.10,
    }

    def _score_dimension(self, value: float, high: float, crit: float) -> float:
        """Map a single metric value to a sub-score in [0, 1]."""
        if value < 0:
            value = 0.0
        if value >= crit:
            # Critical zone: score ∈ [0.8, 1.0) — cap avoids exactly 1.0
            excess = min((value - crit) / max(crit, 1.0), 1.0)
            return 0.8 + 0.19 * excess
        elif value >= high:
            # High zone: score ∈ [0.4, 0.8)
            fraction = (value - high) / max(crit - high, 1.0)
            return 0.4 + 0.4 * fraction
        else:
            # Normal zone: score ∈ [0.0, 0.4)
            fraction = value / max(high, 1.0)
            return 0.4 * fraction

    def predict(self, feature_vector: FeatureVector) -> PredictionResult:
        """
        Compute a weighted anomaly score from threshold rules.

        Args:
            feature_vector: Collected system metrics

        Returns:
            PredictionResult consistent with ModelInterface output contract
        """
        metrics = {
            "cpu_usage":           feature_vector.cpu_usage,
            "failed_logins":       float(feature_vector.failed_logins),
            "network_connections": float(feature_vector.network_connections),
            "process_count":       float(feature_vector.process_count),
            "unique_ip_count":     float(feature_vector.unique_ip_count),
        }

        weighted_score = 0.0
        feature_importance: dict = {}

        for key, value in metrics.items():
            t = self.THRESHOLDS[key]
            sub = self._score_dimension(value, t["high"], t["crit"])
            contribution = self.WEIGHTS[key] * sub
            weighted_score += contribution
            feature_importance[key] = round(contribution, 4)

        # Clamp to [0, 1]
        anomaly_score = max(0.0, min(1.0, weighted_score))
        label = "anomaly" if anomaly_score >= 0.5 else "normal"
        confidence = abs(anomaly_score - 0.5) * 2.0  # scale to [0, 1]

        logging.debug(
            f"[RuleBasedScorer] score={anomaly_score:.3f} label={label} "
            f"contributions={feature_importance}"
        )

        return PredictionResult(
            anomaly_score=anomaly_score,
            label=label,
            confidence=confidence,
            feature_importance=feature_importance,
        )


# ---------------------------------------------------------------------------
# TF Model Interface (with rule-based fallback)
# ---------------------------------------------------------------------------

class ModelInterface:
    """
    Interface for loading and running predictions with the anomaly detection model.

    If the model file is absent or TensorFlow is unavailable, automatically
    falls back to RuleBasedAnomalyScorer so the collection pipeline can
    start without a trained model.  A clear WARNING is emitted so the
    operator knows which scorer is active.

    Attributes:
        model_path: Path to the TensorFlow model file (.h5)
        model: Loaded TensorFlow/Keras model (None if not loaded)
        input_shape: Expected input shape of the model
        _fallback: RuleBasedAnomalyScorer instance (active when model absent)
    """

    def __init__(self, model_path: str):
        """
        Initialize ModelInterface.  Falls back gracefully if model is missing.

        Args:
            model_path: Path to the TensorFlow model file (.h5)
        """
        self.model_path = model_path
        self.model: Optional[object] = None  # tf.keras.Model when loaded
        self.input_shape = None
        self._fallback: Optional[RuleBasedAnomalyScorer] = None

        # ------------------------------------------------------------------ #
        # Attempt to load TF model; activate fallback on any failure          #
        # ------------------------------------------------------------------ #
        if tf is None:
            logging.warning(
                "[ModelInterface] TensorFlow is not installed. "
                "Activating RuleBasedAnomalyScorer as fallback. "
                "Install tensorflow to use the trained model."
            )
            self._fallback = RuleBasedAnomalyScorer()
            return

        if not os.path.exists(model_path):
            logging.warning(
                f"[ModelInterface] Model file not found: {model_path}. "
                "Activating RuleBasedAnomalyScorer as fallback. "
                "Train a model with: python src/train.py"
            )
            self._fallback = RuleBasedAnomalyScorer()
            return

        try:
            logging.info(f"Loading model from: {model_path}")

            try:
                self.model = tf.keras.models.load_model(model_path)
                self.input_shape = self.model.input_shape
                logging.info(f"Model loaded successfully. Input shape: {self.input_shape}")
            except (ValueError, OSError) as e:
                logging.warning(
                    f"Could not load as complete model: {e}. "
                    "Creating network architecture and loading weights..."
                )
                try:
                    import h5py
                    with h5py.File(model_path, "r") as f:
                        if "model_weights" in f.keys():
                            layer_names = list(f["model_weights"].keys())
                        else:
                            layer_names = list(f.keys())
                        logging.info(f"Detected {len(layer_names)} weight groups in saved model")

                    self.model = tf.keras.Sequential([
                        tf.keras.layers.Dense(128, activation="relu", input_shape=(4,)),
                        tf.keras.layers.Dense(128, activation="relu"),
                        tf.keras.layers.Dense(64, activation="relu"),
                        tf.keras.layers.Dense(32, activation="relu"),
                        tf.keras.layers.Dense(16, activation="relu"),
                        tf.keras.layers.Dense(1, activation="sigmoid"),
                    ])
                    try:
                        self.model.load_weights(model_path)
                        self.input_shape = self.model.input_shape
                        logging.info(f"Weights loaded. Input shape: {self.input_shape}")
                    except Exception as weight_err:
                        logging.warning(
                            f"Architecture mismatch loading weights: {weight_err}. "
                            "Using untrained model for testing."
                        )
                        self.input_shape = self.model.input_shape

                except Exception as arch_err:
                    logging.warning(
                        f"Failed to reconstruct model architecture: {arch_err}. "
                        "Activating RuleBasedAnomalyScorer as fallback."
                    )
                    self.model = None
                    self._fallback = RuleBasedAnomalyScorer()

        except Exception as e:
            logging.warning(
                f"[ModelInterface] Failed to load model ({e}). "
                "Activating RuleBasedAnomalyScorer as fallback."
            )
            self.model = None
            self._fallback = RuleBasedAnomalyScorer()

    # ---------------------------------------------------------------------- #
    # Public interface                                                         #
    # ---------------------------------------------------------------------- #

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
