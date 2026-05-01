"""
FIXED Diagnostic Script - Corrects the pipeline issue
"""

import sys
import os
import numpy as np

sys.path.append('backend')

def diagnose_model_fixed():
    print("=" * 60)
    print("FIXED CYBERBULLYING MODEL DIAGNOSTIC")
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
        
        # CORRECT: Use the full pipeline
        pipeline = detector.pipeline
        print(f"Pipeline steps: {list(pipeline.named_steps.keys())}")
        
        # Test the full pipeline (this is what should work)
        try:
            pipeline_prediction = pipeline.predict([cleaned])[0]
            pipeline_proba = pipeline.predict_proba([cleaned])[0]
            print(f"\n✓ PIPELINE WORKS:")
            print(f"  Prediction: {pipeline_prediction}")
            print(f"  Probabilities: {pipeline_proba}")
            print(f"  Cyberbullying probability: {pipeline_proba[1]:.4f}")
        except Exception as e:
            print(f"✗ PIPELINE BROKEN: {e}")
            return
        
        # Test individual components correctly
        vectorizer = pipeline.named_steps['vectorizer']
        ensemble = pipeline.named_steps['ensemble']
        
        # CORRECT: Vectorize first, then predict
        text_vector = vectorizer.transform([cleaned])
        print(f"\nVectorization:")
        print(f"  Input: '{cleaned}'")
        print(f"  Output shape: {text_vector.shape}")
        print(f"  Non-zero features: {text_vector.nnz}")
        
        # Now test ensemble with correct vectorized input
        ensemble_prediction = ensemble.predict(text_vector)[0]
        ensemble_proba = ensemble.predict_proba(text_vector)[0]
        print(f"\nEnsemble (with correct input):")
        print(f"  Prediction: {ensemble_prediction}")
        print(f"  Probabilities: {ensemble_proba}")
        print(f"  Cyberbullying probability: {ensemble_proba[1]:.4f}")
        
        # Check individual classifiers
        print(f"\nIndividual Classifiers:")
        for name, clf in ensemble.named_estimators_.items():
            try:
                pred = clf.predict(text_vector)[0]
                proba = clf.predict_proba(text_vector)[0]
                print(f"  {name:20}: prediction={pred}, proba={proba[1]:.4f}")
            except Exception as e:
                print(f"  {name:20}: ERROR - {e}")
        
        # Test the detector's full predict method
        print(f"\n" + "=" * 40)
        print("DETECTOR'S PREDICT METHOD TEST")
        print("=" * 40)
        
        result = detector.predict(test_text)
        print(f"Full prediction result:")
        for key, value in result.items():
            if key not in ['severity_indicators', 'analysis']:
                print(f"  {key}: {value}")
        
        # Compare pipeline vs detector results
        detector_confidence = result.get('confidence', 0)
        pipeline_confidence = pipeline_proba[1]
        
        print(f"\nCOMPARISON:")
        print(f"  Pipeline confidence:  {pipeline_confidence:.4f}")
        print(f"  Detector confidence:  {detector_confidence:.4f}")
        print(f"  Match: {abs(pipeline_confidence - detector_confidence) < 0.01}")
        
        # Final diagnosis
        print(f"\n" + "=" * 60)
        print("DIAGNOSIS")
        print("=" * 60)
        
        if pipeline_confidence > 0.7:
            print("✓ Model predictions look correct")
        elif pipeline_confidence > 0.5:
            print("⚠ Model gives medium confidence - may need better training")  
        else:
            print("✗ Model confidence too low - serious training issue")
            
        if abs(pipeline_confidence - detector_confidence) < 0.01:
            print("✓ Pipeline and detector match - no integration bug")
        else:
            print("✗ Pipeline vs detector mismatch - integration bug detected")
            
    except Exception as e:
        print(f"Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_model_fixed()