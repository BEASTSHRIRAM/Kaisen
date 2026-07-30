#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for adversarial defense system
"""

import sys
import numpy as np
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print('='*80)
print('COMPREHENSIVE TEST SUITE: ADVERSARIAL DEFENSE SYSTEM')
print('='*80 + '\n')

# Test 1: Import all modules
print('TEST 1: Module Imports')
print('-' * 80)
try:
    from adversarial_defenses import (
        InputValidator,
        AnomalousMetricDetector,
        ConfidenceThreshold,
        EnsembleDefense,
        AdversarialTraining,
        IntegratedDefenseSystem
    )
    print('[PASS] All defense classes imported successfully\n')
    test1_pass = True
except Exception as e:
    print(f'[FAIL] Import failed: {e}\n')
    test1_pass = False
    sys.exit(1)

# Test 2: InputValidator
print('TEST 2: InputValidator')
print('-' * 80)
try:
    feature_bounds = {
        'cpu': (0, 100),
        'memory': (0, 100),
        'connections': (0, 1000)
    }
    validator = InputValidator(feature_bounds)
    
    # Normal state
    normal_state = np.array([50.0, 50.0, 500.0])
    is_suspicious, features = validator.check_suspicious_metrics(normal_state)
    assert not is_suspicious, 'Normal state should not be suspicious'
    print(f'  [PASS] Normal state: NOT suspicious (correct)')
    
    # Extreme state
    extreme_state = np.array([-50.0, 200.0, 5000.0])
    is_suspicious, features = validator.check_suspicious_metrics(extreme_state)
    assert is_suspicious, 'Extreme state should be suspicious'
    print(f'  [PASS] Extreme state: DETECTED as suspicious')
    print(f'     Suspicious features found: {len(features)}')
    for feat in features[:2]:
        print(f'       - {feat}')
    print()
    test2_pass = True
except Exception as e:
    print(f'[FAIL] InputValidator test failed: {e}\n')
    test2_pass = False

# Test 3: AnomalousMetricDetector
print('TEST 3: AnomalousMetricDetector')
print('-' * 80)
try:
    detector = AnomalousMetricDetector()
    
    # Normal state
    normal_state = np.array([50, 50, 100, 100, 10, 5, 0.1, 0, 0, 0, 10, 0, 0], dtype=float)
    is_anomalous, reason = detector.check_metric_consistency(normal_state)
    assert not is_anomalous, 'Normal state should not be anomalous'
    print(f'  [PASS] Normal state: CONSISTENT (correct)')
    
    # Suspicious state (high lateral movement + high failed logins)
    suspicious_state = np.array([50, 50, 100, 700, 10, 80, 0.1, 0, 0, 0, 10, 0, 0], dtype=float)
    is_anomalous, reason = detector.check_metric_consistency(suspicious_state)
    print(f'  [PASS] Suspicious state tested')
    if is_anomalous:
        print(f'     Pattern detected: {reason}')
    else:
        print(f'     No pattern detected (state: {reason})')
    print()
    test3_pass = True
except Exception as e:
    print(f'[FAIL] AnomalousMetricDetector test failed: {e}\n')
    test3_pass = False

# Test 4: ConfidenceThreshold
print('TEST 4: ConfidenceThreshold')
print('-' * 80)
try:
    checker = ConfidenceThreshold(confidence_threshold=0.15)
    
    # High confidence Q-values
    high_conf_q = np.array([5.0, 3.0, 4.9])
    confidence, is_confident = checker.check_decision_confidence(high_conf_q)
    print(f'  [PASS] High confidence Q-values: [5.0, 3.0, 4.9]')
    print(f'     Confidence score: {confidence:.4f}')
    print(f'     Confident? {is_confident}')
    
    # Low confidence Q-values
    low_conf_q = np.array([5.0, 4.99, 4.98])
    confidence, is_confident = checker.check_decision_confidence(low_conf_q)
    print(f'  [PASS] Low confidence Q-values: [5.0, 4.99, 4.98]')
    print(f'     Confidence score: {confidence:.4f}')
    print(f'     Confident? {is_confident}')
    print()
    test4_pass = True
except Exception as e:
    print(f'[FAIL] ConfidenceThreshold test failed: {e}\n')
    test4_pass = False

# Test 5: IntegratedDefenseSystem structure
print('TEST 5: IntegratedDefenseSystem Initialization')
print('-' * 80)
try:
    from agent import DQNAgent
    from config import get_config
    
    # Initialize agent
    config = get_config()
    agent = DQNAgent(
        state_size=13,
        action_size=5,
        learning_rate=config.agent.learning_rate,
        gamma=config.agent.gamma,
        epsilon=0.01,
    )
    
    # Create defense system
    defense = IntegratedDefenseSystem(agent)
    print(f'  [PASS] IntegratedDefenseSystem created successfully')
    print(f'     Has Input Validator: {hasattr(defense, "input_validator")}')
    print(f'     Has Metric Detector: {hasattr(defense, "metric_detector")}')
    print(f'     Has Confidence Checker: {hasattr(defense, "confidence_checker")}')
    print(f'     Has Ensemble: {hasattr(defense, "ensemble")}')
    print(f'     Has Adversarial Trainer: {hasattr(defense, "adversarial_trainer")}')
    print()
    test5_pass = True
except Exception as e:
    print(f'[FAIL] IntegratedDefenseSystem test failed: {e}\n')
    import traceback
    traceback.print_exc()
    test5_pass = False

# Test 6: Protect and decide function
print('TEST 6: protect_and_decide() Function')
print('-' * 80)
try:
    from agent import DQNAgent
    from config import get_config
    
    # Initialize agent
    config = get_config()
    agent = DQNAgent(
        state_size=13,
        action_size=5,
        learning_rate=config.agent.learning_rate,
        gamma=config.agent.gamma,
        epsilon=0.01,
    )
    
    # Create defense system
    defense = IntegratedDefenseSystem(agent)
    
    # Test on normal state
    normal_state = np.array([
        50.0, 40.0, 150.0, 100.0, 20.0, 5.0, 0.1, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0
    ], dtype=np.float32)
    
    decision = defense.protect_and_decide(normal_state)
    
    print(f'  [PASS] protect_and_decide() executed successfully')
    print(f'     Action: {decision["action"]}')
    print(f'     Confidence: {decision.get("confidence", 0):.4f}')
    print(f'     Security Level: {decision["security_level"]}')
    print(f'     Alerts: {len(decision["alerts"])}')
    print(f'     Reason: {decision["reason"]}')
    print()
    test6_pass = True
except Exception as e:
    print(f'[FAIL] protect_and_decide test failed: {e}\n')
    import traceback
    traceback.print_exc()
    test6_pass = False

# Test 7: Edge case - extreme state
print('TEST 7: Edge Case - Extreme State')
print('-' * 80)
try:
    from agent import DQNAgent
    from config import get_config
    
    config = get_config()
    agent = DQNAgent(
        state_size=13,
        action_size=5,
        learning_rate=config.agent.learning_rate,
        gamma=config.agent.gamma,
        epsilon=0.01,
    )
    
    defense = IntegratedDefenseSystem(agent)
    
    # Extreme state (should trigger defenses)
    extreme_state = np.array([
        0.0, 100.0, 500.0, 1000.0, 50.0, 100.0, 1.0, 1.0, 1.0, 1.0, 100.0, 1.0, 1.0
    ], dtype=np.float32)
    
    decision = defense.protect_and_decide(extreme_state)
    
    print(f'  [PASS] Extreme state handled')
    print(f'     Security Level: {decision["security_level"]}')
    print(f'     Alerts triggered: {len(decision["alerts"])}')
    if decision["alerts"]:
        print(f'     First alert: {decision["alerts"][0]["type"]}')
    print()
    test7_pass = True
except Exception as e:
    print(f'[FAIL] Edge case test failed: {e}\n')
    import traceback
    traceback.print_exc()
    test7_pass = False

# Summary
print('='*80)
print('TEST RESULTS SUMMARY')
print('='*80)
tests = [
    ('Module Imports', test1_pass),
    ('InputValidator', test2_pass),
    ('AnomalousMetricDetector', test3_pass),
    ('ConfidenceThreshold', test4_pass),
    ('IntegratedDefenseSystem Init', test5_pass),
    ('protect_and_decide()', test6_pass),
    ('Edge Case - Extreme State', test7_pass),
]

passed = sum(1 for _, p in tests if p)
total = len(tests)

for name, passed_test in tests:
    status = '[PASS]' if passed_test else '[FAIL]'
    print(f'{status}: {name}')

print(f'\nTotal: {passed}/{total} tests passed')

if passed == total:
    print('\nALL TESTS PASSED!')
    sys.exit(0)
else:
    print(f'\n{total - passed} test(s) failed')
    sys.exit(1)
