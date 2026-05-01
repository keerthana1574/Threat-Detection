"""
Comprehensive model diagnostic script
Identifies exactly what's wrong with the cyberbullying model
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.append('backend')

def diagnose_model():
    print("=" * 60)
    print("CYBERBULLYING MODEL DIAGNOSTIC")
    print("=" * 60)
    
    try:
        from modules.cyberbullying.detector import EnhancedCyberbullyingDetector
        detector = EnhancedCyberbullyingDetector()
        
        print("✓ Detector imported successfully")
        
        # Load model
        if detector.load_model():
            print("✓ Model loaded successfully")
        else:
            print("✗ Model failed to load")
            return
        
        # Test preprocessing
        test_text = "you stupid idiot useless"
        cleaned = detector.enhanced_preprocess_text(test_text)
        print(f"\nPreprocessing Test:")
        print(f"Original: '{test_text}'")
        print(f"Cleaned:  '{cleaned}'")
        
        # Get raw model scores
        pipeline = detector.pipeline
        print(f"\nPipeline steps: {list(pipeline.named_steps.keys())}")
        
        # Get vectorizer output
        vectorizer = pipeline.named_steps['vectorizer']
        text_vector = vectorizer.transform([cleaned])
        print(f"Vectorizer output shape: {text_vector.shape}")
        print(f"Non-zero features: {text_vector.nnz}")
        
        # Get raw ensemble predictions
        ensemble = pipeline.named_steps['ensemble']
        raw_prediction = ensemble.predict([cleaned])[0]
        raw_probabilities = ensemble.predict_proba([cleaned])[0]
        
        print(f"\nRaw Ensemble Results:")
        print(f"Raw prediction: {raw_prediction}")
        print(f"Raw probabilities: {raw_probabilities}")
        print(f"Probability of cyberbullying: {raw_probabilities[1]:.4f}")
        
        # Check individual classifiers
        print(f"\nIndividual Classifier Results:")
        for name, clf in ensemble.named_estimators_.items():
            pred = clf.predict(text_vector)[0]
            proba = clf.predict_proba(text_vector)[0]
            print(f"{name:20}: prediction={pred}, proba={proba[1]:.4f}")
        
        # Check threshold logic
        print(f"\nThreshold Analysis:")
        print(f"Optimal threshold: {detector.optimal_threshold}")
        print(f"Raw confidence: {raw_probabilities[1]:.4f}")
        print(f"Above threshold? {raw_probabilities[1] > detector.optimal_threshold}")
        
        # Check severity features
        severity = detector._analyze_severity_features(test_text)
        print(f"\nSeverity Features: {severity}")
        
        # Full prediction with debug
        result = detector.predict(test_text)
        print(f"\nFinal Result: {result}")
        
        # Test with other obvious examples
        print(f"\n" + "=" * 60)
        print("TESTING MULTIPLE OBVIOUS CASES")
        print("=" * 60)
        
        test_cases = [
            ("you stupid idiot useless", True),
            ("I hate you so much", True), 
            ("kill yourself worthless", True),
            ("you are amazing", False),
            ("have a great day", False)
        ]
        
        failures = 0
        for text, expected in test_cases:
            result = detector.predict(text)
            predicted = result.get('is_cyberbullying', False)
            confidence = result.get('confidence', 0)
            
            status = "✓ PASS" if predicted == expected else "✗ FAIL"
            if predicted != expected:
                failures += 1
            
            print(f"{status} '{text}'")
            print(f"    Expected: {expected}, Got: {predicted} ({confidence:.1%})")
        
        print(f"\nSUMMARY:")
        print(f"Failed tests: {failures}/{len(test_cases)}")
        print(f"Success rate: {((len(test_cases) - failures) / len(test_cases)) * 100:.1f}%")
        
        if failures > 0:
            print(f"\n🚨 MODEL IS BROKEN - {failures} obvious cases failed")
            print("RECOMMENDED ACTION: Complete model retrain needed")
        else:
            print(f"\n✅ Model appears to be working correctly")
            
    except Exception as e:
        print(f"Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_model()