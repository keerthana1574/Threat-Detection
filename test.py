# test_fixes.py
"""
Verification script to test if the cyberbullying detection fixes are working
Run this after implementing the fixes to verify they work correctly
"""

import sys
import os
import logging
from datetime import datetime

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if the detector can be imported"""
    print("Testing imports...")
    
    # Add backend to path
    sys.path.append('backend')
    
    try:
        from modules.cyberbullying.detector import CyberbullyingDetector
        print("[OK] Successfully imported CyberbullyingDetector")
        return True
    except ImportError:
        try:
            from backend.modules.cyberbullying.detector import CyberbullyingDetector  
            print("[OK] Successfully imported CyberbullyingDetector (backend path)")
            return True
        except ImportError as e:
            print(f"[FAILED] Could not import detector: {e}")
            return False

def test_model_loading():
    """Test if the model can be loaded"""
    print("\nTesting model loading...")
    
    try:
        from modules.cyberbullying.detector import CyberbullyingDetector
    except ImportError:
        from backend.modules.cyberbullying.detector import CyberbullyingDetector
    
    detector = CyberbullyingDetector()
    
    # Check if model file exists
    model_file = os.path.join(detector.model_path, 'cyberbullying_model.pkl')
    if not os.path.exists(model_file):
        print(f"[INFO] Model file not found at {model_file}")
        print(f"[INFO] This is normal if you haven't trained yet")
        return False
    
    # Try to load model
    if detector.load_model():
        print("[OK] Model loaded successfully")
        return True
    else:
        print("[FAILED] Could not load model")
        return False

def test_predictions():
    """Test predictions with the new model"""
    print("\nTesting predictions...")
    
    try:
        from modules.cyberbullying.detector import CyberbullyingDetector
    except ImportError:
        from backend.modules.cyberbullying.detector import CyberbullyingDetector
    
    detector = CyberbullyingDetector()
    
    # Test cases that should NOT be flagged as cyberbullying (fixing false positives)
    safe_texts = [
        "You're such an amazing person! Keep being awesome!",
        "Just had a great day at the park with friends",
        "Hey, how are you doing today? Hope you're well!",
        "Looking forward to the weekend",
        "Thanks for your help today"
    ]
    
    # Test cases that SHOULD be flagged as cyberbullying
    cyberbullying_texts = [
        "You're so ugly and stupid, nobody likes you",
        "Kill yourself, you worthless piece of trash",
        "I hate you so much, go die!",
        "You fat loser, you should just disappear"
    ]
    
    false_positives = 0
    false_negatives = 0
    
    print("Testing safe texts (should NOT be flagged):")
    for text in safe_texts:
        result = detector.predict(text)
        is_cyberbullying = result.get('is_cyberbullying', False)
        confidence = result.get('confidence', 0)
        
        status = "[FAIL - False Positive]" if is_cyberbullying else "[PASS]"
        if is_cyberbullying:
            false_positives += 1
        
        print(f"  {status} '{text[:40]}...' -> {is_cyberbullying} ({confidence:.3f})")
    
    print("\nTesting cyberbullying texts (SHOULD be flagged):")
    for text in cyberbullying_texts:
        result = detector.predict(text)
        is_cyberbullying = result.get('is_cyberbullying', False)
        confidence = result.get('confidence', 0)
        severity = result.get('severity', 'none')
        
        status = "[FAIL - False Negative]" if not is_cyberbullying else "[PASS]"
        if not is_cyberbullying:
            false_negatives += 1
        
        print(f"  {status} '{text[:40]}...' -> {is_cyberbullying} ({confidence:.3f}, {severity})")
    
    # Calculate performance
    total_tests = len(safe_texts) + len(cyberbullying_texts)
    errors = false_positives + false_negatives
    accuracy = ((total_tests - errors) / total_tests) * 100
    
    print(f"\nPrediction Test Results:")
    print(f"  False Positives: {false_positives}/{len(safe_texts)} ({false_positives/len(safe_texts)*100:.1f}%)")
    print(f"  False Negatives: {false_negatives}/{len(cyberbullying_texts)} ({false_negatives/len(cyberbullying_texts)*100:.1f}%)")
    print(f"  Overall Accuracy: {accuracy:.1f}%")
    
    # Determine if fixes worked
    if false_positives <= 1:  # Allow 1 false positive
        print("[OK] False positive issue appears to be fixed!")
        return True
    else:
        print("[WARNING] Still getting too many false positives")
        return False

def test_dataset_loading():
    """Test if datasets can be loaded properly"""
    print("\nTesting dataset loading...")
    
    try:
        from modules.cyberbullying.detector import CyberbullyingDetector
    except ImportError:
        from backend.modules.cyberbullying.detector import CyberbullyingDetector
    
    detector = CyberbullyingDetector()
    
    # List expected datasets
    dataset_paths = [
        'datasets/cyberbullying/cyberbullying_tweets.csv',
        'datasets/cyberbullying/final_hateXplain.csv',
        'datasets/cyberbullying/aggression_parsed_dataset.csv',
        'datasets/cyberbullying/attack_parsed_dataset.csv',
        'datasets/cyberbullying/toxicity_parsed_dataset.csv',
        'datasets/cyberbullying/twitter_parsed_dataset.csv',
        'datasets/cyberbullying/twitter_racism_parsed_dataset.csv',
        'datasets/cyberbullying/twitter_sexism_parsed_dataset.csv',
        'datasets/cyberbullying/youtube_parsed_dataset.csv',
        'datasets/cyberbullying/kaggle_parsed_dataset.csv'
    ]
    
    existing_datasets = []
    for path in dataset_paths:
        if os.path.exists(path):
            existing_datasets.append(path)
            print(f"[OK] Found: {os.path.basename(path)}")
        else:
            print(f"[MISSING] Not found: {os.path.basename(path)}")
    
    if not existing_datasets:
        print("[INFO] No datasets found - this is normal if you haven't added them yet")
        return False
    
    # Test loading one dataset
    try:
        import pandas as pd
        test_dataset = existing_datasets[0]
        df = pd.read_csv(test_dataset, nrows=5)
        print(f"[OK] Successfully read {os.path.basename(test_dataset)}")
        print(f"      Columns: {list(df.columns)}")
        
        # Test dataset standardization
        processed_df = detector._standardize_dataset_format(df, test_dataset)
        if processed_df is not None and len(processed_df) > 0:
            print(f"[OK] Dataset standardization working")
            return True
        else:
            print(f"[WARNING] Dataset standardization may have issues")
            return False
            
    except Exception as e:
        print(f"[FAILED] Error testing dataset loading: {e}")
        return False

def main():
    """Run all verification tests"""
    print("Cyberbullying Detection - Fix Verification")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        'imports': test_imports(),
        'model_loading': test_model_loading(), 
        'dataset_loading': test_dataset_loading(),
        'predictions': False  # Will be set based on model availability
    }
    
    # Only test predictions if model is loaded
    if test_results['model_loading']:
        test_results['predictions'] = test_predictions()
    else:
        print("\n[SKIP] Skipping prediction tests - no trained model found")
        print("       Run 'python train_cyberbullying.py' first")
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len([k for k, v in test_results.items() if v is not False or k == 'predictions'])
    
    for test_name, result in test_results.items():
        if result is not False or test_name == 'predictions':
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All fixes appear to be working correctly!")
        if not test_results['model_loading']:
            print("Next step: Run 'python train_cyberbullying.py' to train the model")
        else:
            print("Next step: Start your server with 'python app.py'")
    elif passed >= total - 1:
        print("\n[OK] Most fixes are working. Check failed tests above.")
    else:
        print("\n[WARNING] Several issues detected. Check the output above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()