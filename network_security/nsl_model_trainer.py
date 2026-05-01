# backend/modules/network_security/nsl_model_trainer.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import cross_val_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os
import time

class NSLKDDModelTrainer:
    def __init__(self):
        self.models = {}
        
    def train_traditional_models(self, X_train, X_test, y_train, y_test):
        """Train traditional machine learning models"""
        print("\nTraining Traditional ML Models")
        print("="*50)
        
        results = {}
        
        # 1. Random Forest
        print("1. Training Random Forest...")
        start_time = time.time()
        
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_proba = rf_model.predict_proba(X_test)[:, 1]
        
        rf_accuracy = accuracy_score(y_test, rf_pred)
        rf_auc = roc_auc_score(y_test, rf_proba)
        
        print(f"Random Forest completed in {time.time() - start_time:.2f}s")
        print(f"Accuracy: {rf_accuracy:.4f}, AUC: {rf_auc:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, rf_pred, target_names=['Normal', 'Attack']))
        
        self.models['random_forest'] = rf_model
        results['random_forest'] = {'accuracy': rf_accuracy, 'auc': rf_auc}
        
        # 2. Logistic Regression
        print("\n2. Training Logistic Regression...")
        start_time = time.time()
        
        lr_model = LogisticRegression(
            class_weight='balanced',
            random_state=42,
            max_iter=1000,
            solver='liblinear'
        )
        
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)
        lr_proba = lr_model.predict_proba(X_test)[:, 1]
        
        lr_accuracy = accuracy_score(y_test, lr_pred)
        lr_auc = roc_auc_score(y_test, lr_proba)
        
        print(f"Logistic Regression completed in {time.time() - start_time:.2f}s")
        print(f"Accuracy: {lr_accuracy:.4f}, AUC: {lr_auc:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, lr_pred, target_names=['Normal', 'Attack']))
        
        self.models['logistic_regression'] = lr_model
        results['logistic_regression'] = {'accuracy': lr_accuracy, 'auc': lr_auc}
        
        # 3. Support Vector Machine (on subset for speed)
        print("\n3. Training SVM (on subset)...")
        start_time = time.time()
        
        # Use smaller subset for SVM due to computational complexity
        subset_size = min(10000, len(X_train))
        indices = np.random.choice(len(X_train), subset_size, replace=False)
        X_train_subset = X_train.iloc[indices]
        y_train_subset = y_train.iloc[indices]
        
        svm_model = SVC(
            kernel='rbf',
            class_weight='balanced',
            probability=True,
            random_state=42,
            C=1.0,
            gamma='scale'
        )
        
        svm_model.fit(X_train_subset, y_train_subset)
        svm_pred = svm_model.predict(X_test)
        svm_proba = svm_model.predict_proba(X_test)[:, 1]
        
        svm_accuracy = accuracy_score(y_test, svm_pred)
        svm_auc = roc_auc_score(y_test, svm_proba)
        
        print(f"SVM completed in {time.time() - start_time:.2f}s")
        print(f"Accuracy: {svm_accuracy:.4f}, AUC: {svm_auc:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, svm_pred, target_names=['Normal', 'Attack']))
        
        self.models['svm'] = svm_model
        results['svm'] = {'accuracy': svm_accuracy, 'auc': svm_auc}
        
        return results
    
    def train_anomaly_detection(self, X_train, y_train, X_test, y_test):
        """Train anomaly detection model"""
        print("\n4. Training Isolation Forest...")
        start_time = time.time()
        
        # Train on normal traffic only
        X_normal = X_train[y_train == 0]
        
        # Use subset if too large
        if len(X_normal) > 15000:
            X_normal = X_normal.sample(15000, random_state=42)
        
        iso_forest = IsolationForest(
            contamination=0.1,
            n_estimators=100,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        
        iso_forest.fit(X_normal)
        
        # Predict on test set
        anomaly_pred = iso_forest.predict(X_test)
        anomaly_scores = iso_forest.decision_function(X_test)
        
        # Convert predictions (-1 = anomaly, 1 = normal)
        anomaly_pred_binary = (anomaly_pred == -1).astype(int)
        
        iso_accuracy = accuracy_score(y_test, anomaly_pred_binary)
        iso_auc = roc_auc_score(y_test, -anomaly_scores)  # Negative because lower scores = anomalous
        
        print(f"Isolation Forest completed in {time.time() - start_time:.2f}s")
        print(f"Accuracy: {iso_accuracy:.4f}, AUC: {iso_auc:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, anomaly_pred_binary, target_names=['Normal', 'Anomaly']))
        
        self.models['isolation_forest'] = iso_forest
        
        return {'accuracy': iso_accuracy, 'auc': iso_auc}
    
    def train_neural_network(self, X_train, X_test, y_train, y_test):
        """Train neural network"""
        print("\n5. Training Neural Network...")
        start_time = time.time()
        
        # Build model
        model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(32, activation='relu'),
            Dropout(0.2),
            
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Train with early stopping
        early_stop = EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        )
        
        history = model.fit(
            X_train, y_train,
            batch_size=256,
            epochs=30,
            validation_data=(X_test, y_test),
            callbacks=[early_stop],
            verbose=1
        )
        
        # Evaluate
        nn_pred_proba = model.predict(X_test, verbose=0).flatten()
        nn_pred = (nn_pred_proba > 0.5).astype(int)
        
        nn_accuracy = accuracy_score(y_test, nn_pred)
        nn_auc = roc_auc_score(y_test, nn_pred_proba)
        
        print(f"Neural Network completed in {time.time() - start_time:.2f}s")
        print(f"Accuracy: {nn_accuracy:.4f}, AUC: {nn_auc:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, nn_pred, target_names=['Normal', 'Attack']))
        
        self.models['neural_network'] = model
        
        return {'accuracy': nn_accuracy, 'auc': nn_auc}
    
    def save_models(self, save_dir):
        """Save all models"""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save traditional models
        traditional_models = ['random_forest', 'logistic_regression', 'svm', 'isolation_forest']
        for model_name in traditional_models:
            if model_name in self.models:
                joblib.dump(self.models[model_name], f"{save_dir}/{model_name}_model.pkl")
                print(f"Saved {model_name}")
        
        # Save neural network
        if 'neural_network' in self.models:
            self.models['neural_network'].save(f"{save_dir}/neural_network_model.keras")
            print("Saved neural network")
        
        print(f"All models saved to {save_dir}")
