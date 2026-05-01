# backend/modules/network_security/simple_models.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import os

class SimpleNetworkDetector:
    def __init__(self):
        self.models = {}
    
    def train_models(self, X_train, X_test, y_train, y_test):
        """Train simplified models for network intrusion detection"""
        print("Training Network Security Models...")
        print("="*50)
        
        results = {}
        
        # 1. Random Forest (Best for network data)
        print("\n1. Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_proba = rf_model.predict_proba(X_test)[:, 1]
        
        rf_accuracy = accuracy_score(y_test, rf_pred)
        rf_auc = roc_auc_score(y_test, rf_proba)
        
        print(f"Random Forest - Accuracy: {rf_accuracy:.4f}, AUC: {rf_auc:.4f}")
        print(classification_report(y_test, rf_pred, target_names=['Normal', 'Attack']))
        
        self.models['random_forest'] = rf_model
        results['random_forest'] = {'accuracy': rf_accuracy, 'auc': rf_auc}
        
        # 2. Logistic Regression (Fast and interpretable)
        print("\n2. Training Logistic Regression...")
        lr_model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)
        lr_proba = lr_model.predict_proba(X_test)[:, 1]
        
        lr_accuracy = accuracy_score(y_test, lr_pred)
        lr_auc = roc_auc_score(y_test, lr_proba)
        
        print(f"Logistic Regression - Accuracy: {lr_accuracy:.4f}, AUC: {lr_auc:.4f}")
        print(classification_report(y_test, lr_pred, target_names=['Normal', 'Attack']))
        
        self.models['logistic_regression'] = lr_model
        results['logistic_regression'] = {'accuracy': lr_accuracy, 'auc': lr_auc}
        
        # 3. Isolation Forest (Anomaly Detection)
        print("\n3. Training Isolation Forest...")
        iso_forest = IsolationForest(
            contamination=0.2,  # Expected 20% anomalies
            random_state=42,
            n_estimators=100
        )
        
        # Train on normal traffic only
        X_normal = X_train[y_train == 0]
        iso_forest.fit(X_normal)
        
        iso_pred = iso_forest.predict(X_test)
        iso_pred_binary = (iso_pred == -1).astype(int)  # -1 = anomaly, 1 = normal
        iso_scores = iso_forest.decision_function(X_test)
        
        iso_accuracy = accuracy_score(y_test, iso_pred_binary)
        iso_auc = roc_auc_score(y_test, -iso_scores)  # Negative scores for anomalies
        
        print(f"Isolation Forest - Accuracy: {iso_accuracy:.4f}, AUC: {iso_auc:.4f}")
        print(classification_report(y_test, iso_pred_binary, target_names=['Normal', 'Anomaly']))
        
        self.models['isolation_forest'] = iso_forest
        results['isolation_forest'] = {'accuracy': iso_accuracy, 'auc': iso_auc}
        
        # 4. Simple Neural Network
        print("\n4. Training Neural Network...")
        nn_model = Sequential([
            Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        
        nn_model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Train with early stopping
        history = nn_model.fit(
            X_train, y_train,
            batch_size=128,
            epochs=20,
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        nn_pred_proba = nn_model.predict(X_test, verbose=0).flatten()
        nn_pred = (nn_pred_proba > 0.5).astype(int)
        
        nn_accuracy = accuracy_score(y_test, nn_pred)
        nn_auc = roc_auc_score(y_test, nn_pred_proba)
        
        print(f"Neural Network - Accuracy: {nn_accuracy:.4f}, AUC: {nn_auc:.4f}")
        print(classification_report(y_test, nn_pred, target_names=['Normal', 'Attack']))
        
        self.models['neural_network'] = nn_model
        results['neural_network'] = {'accuracy': nn_accuracy, 'auc': nn_auc}
        
        return results
    
    def save_models(self, save_dir):
        """Save all models"""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save traditional models
        for name, model in self.models.items():
            if name != 'neural_network':
                joblib.dump(model, f"{save_dir}/{name}_model.pkl")
        
        # Save neural network
        if 'neural_network' in self.models:
            self.models['neural_network'].save(f"{save_dir}/neural_network.keras")
        
        print(f"Models saved to {save_dir}")
