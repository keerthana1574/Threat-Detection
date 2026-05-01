# backend/modules/network_security/nsl_train.py
import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from nsl_data_preprocessor import NSLKDDPreprocessor
from nsl_model_trainer import NSLKDDModelTrainer

def main():
    print("NSL-KDD Network Intrusion Detection Training")
    print("="*60)
    
    start_total = time.time()
    
    # Initialize components
    preprocessor = NSLKDDPreprocessor()
    trainer = NSLKDDModelTrainer()
    
    # FIXED: Handle path properly from any working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    dataset_dir = os.path.join(project_root, 'datasets', 'network_security', 'NSL-KDD')
    
    # Alternative: If running from project root
    if not os.path.exists(dataset_dir):
        dataset_dir = os.path.join(os.getcwd(), 'datasets', 'network_security', 'NSL-KDD')

    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for dataset at: {dataset_dir}")
    print(f"Absolute path: {os.path.abspath(dataset_dir)}")
    print(f"Directory exists: {os.path.exists(dataset_dir)}")
    
    # List files if directory exists
    if os.path.exists(dataset_dir):
        print(f"Files in directory: {os.listdir(dataset_dir)}")
    else:
        print(f"Error: Dataset directory '{dataset_dir}' not found!")
        print("\nTrying alternate paths...")
        
        # Try other common paths
        alternate_paths = [
            'datasets/network_security/NSL-KDD',
            './datasets/network_security/NSL-KDD',
            '../../../datasets/network_security/NSL-KDD'
        ]
        
        for alt_path in alternate_paths:
            if os.path.exists(alt_path):
                dataset_dir = alt_path
                print(f"Found dataset at: {dataset_dir}")
                break
        else:
            print("Could not find dataset in any expected location!")
            return
    
    
    try:
        # Load dataset
        print("Step 1: Loading NSL-KDD dataset...")
        df = preprocessor.load_nsl_kdd_files(dataset_dir)
        
        # Preprocess data
        print("\nStep 2: Preprocessing data...")
        X, y_binary, y_multi = preprocessor.preprocess_data(df)
        
        # Split data
        print("\nStep 3: Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_binary,
            test_size=0.2,
            random_state=42,
            stratify=y_binary
        )
        
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        print(f"Training distribution: {np.bincount(y_train)}")
        print(f"Test distribution: {np.bincount(y_test)}")
        
        # Train models
        print("\n" + "="*60)
        print("MODEL TRAINING")
        print("="*60)
        
        all_results = {}
        
        # Traditional models
        traditional_results = trainer.train_traditional_models(X_train, X_test, y_train, y_test)
        all_results.update(traditional_results)
        
        # Anomaly detection
        anomaly_result = trainer.train_anomaly_detection(X_train, y_train, X_test, y_test)
        all_results['isolation_forest'] = anomaly_result
        
        # Neural network
        nn_result = trainer.train_neural_network(X_train, X_test, y_train, y_test)
        all_results['neural_network'] = nn_result
        
        # Save models and preprocessor
        model_dir = 'backend/models/network_security'
        print(f"\nSaving models to {model_dir}...")
        trainer.save_models(model_dir)
        preprocessor.save_preprocessor(model_dir)
        
        # Print final summary
        total_time = time.time() - start_total
        print("\n" + "="*60)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Total training time: {total_time:.2f} seconds")
        
        print("\nModel Performance Summary:")
        print("-" * 50)
        for model_name, results in all_results.items():
            acc = results.get('accuracy', 0)
            auc = results.get('auc', 0)
            print(f"{model_name:20s}: Accuracy={acc:.4f}, AUC={auc:.4f}")
        
        # Find best model
        best_model = max(all_results.items(), key=lambda x: x[1].get('accuracy', 0))
        print(f"\nBest performing model: {best_model[0]} ({best_model[1]['accuracy']:.4f})")
        
        print(f"\nAll models and preprocessor saved to: {model_dir}")
        print("Ready for network intrusion detection!")
        
    except FileNotFoundError as e:
        print(f"Dataset error: {e}")
        print("\nPlease ensure your NSL-KDD files are in the correct format:")
        print("  datasets/nsl/KDDTrain+.txt (or .csv)")
        print("  datasets/nsl/KDDTest+.txt (or .csv)")
        
    except Exception as e:
        print(f"Training error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()