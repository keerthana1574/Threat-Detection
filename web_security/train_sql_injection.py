import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import joblib
import pickle
from urllib.parse import unquote
import base64
from datetime import datetime
import logging

class SQLInjectionDetector:
    def __init__(self):
        self.models = {}
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
        self.feature_names = None  # Store feature names for consistency
        
        self.sql_keywords = [
            'select', 'union', 'insert', 'update', 'delete', 'drop', 'create',
            'alter', 'exec', 'execute', 'sp_', 'xp_', 'cmdshell', 'waitfor',
            'cast', 'char', 'ascii', 'substring', 'len', 'user', 'database',
            'table_name', 'column_name', 'information_schema', 'sysobjects',
            'syscolumns', 'pg_', 'mysql', 'oracle', 'mssql', 'sqlite'
        ]
        
        self.sql_patterns = [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # SQL meta-characters
            r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",  # Typical SQL injection
            r"w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",  # 'or' variations
            r"((\%27)|(\'))union",  # Union-based injection
            r"((\%27)|(\'))select",  # Select-based injection
            r"exec(\s|\+)+(s|x)p\w+",  # Stored procedure execution
            r"UNION(.|\s)*SELECT",  # Union select (case insensitive)
            r"((\%27)|(\'))\s*(and|or)\s*((\%27)|(\'))",  # Boolean-based injection
            r"(sleep|benchmark|waitfor)\s*\(",  # Time-based injection
            r"(load_file|into\s+outfile)",  # File operations
            r"(concat|group_concat|string_agg)\s*\(",  # String functions
            r"(ascii|char|hex|unhex|substring)\s*\(",  # Character functions
            r"information_schema\.(tables|columns)",  # Schema enumeration
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
        
    def extract_simple_features(self, input_string):
        """Extract simplified features that match training"""
        if not input_string:
            input_string = ""
        
        text_lower = input_string.lower()
        
        # These must match exactly what was used in training
        features = {
            'length': len(input_string),
            'quotes': input_string.count("'") + input_string.count('"'),
            'hyphens': input_string.count('--'),
            'union': text_lower.count('union'),
            'select': text_lower.count('select'),
            'or_count': text_lower.count(' or '),
            'and_count': text_lower.count(' and '),
            'equals': input_string.count('='),
            'semicolon': input_string.count(';')
        }
        
        return list(features.values())
    
    def preprocess_input(self, input_string):
        """Preprocess input string for analysis"""
        if not input_string:
            return ""
        
        # URL decode
        decoded = unquote(input_string)
        
        # Handle multiple encoding layers
        try:
            # Try base64 decode if it looks like base64
            if re.match(r'^[A-Za-z0-9+/]*={0,2}$', decoded) and len(decoded) % 4 == 0:
                try:
                    decoded = base64.b64decode(decoded).decode('utf-8', errors='ignore')
                except:
                    pass
        except:
            pass
        
        # Convert to lowercase for analysis
        return decoded.lower()
    
    def rule_based_detection(self, input_string):
        """Rule-based SQL injection detection"""
        preprocessed = self.preprocess_input(input_string)
        detections = []
        
        # Check for common SQL injection patterns
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(preprocessed)
            if matches:
                detections.append({
                    'pattern_id': i,
                    'pattern': self.sql_patterns[i],
                    'matches': matches,
                    'match_count': len(matches)
                })
        
        # Heuristic checks
        risk_score = 0
        
        # High-risk keywords
        high_risk_keywords = ['union select', 'drop table', 'exec xp_', 'sp_password', 'information_schema']
        for keyword in high_risk_keywords:
            if keyword in preprocessed:
                risk_score += 10
                detections.append({
                    'type': 'high_risk_keyword',
                    'keyword': keyword
                })
        
        # Suspicious character combinations
        if "'or'" in preprocessed or '"or"' in preprocessed:
            risk_score += 8
            detections.append({'type': 'or_injection_pattern'})
        
        if "' and '" in preprocessed or '" and "' in preprocessed:
            risk_score += 8
            detections.append({'type': 'and_injection_pattern'})
        
        # Comment-based evasion
        if '--' in preprocessed or '/*' in preprocessed:
            risk_score += 5
            detections.append({'type': 'comment_evasion'})
        
        # Multiple quotes (often used in injection)
        quote_count = preprocessed.count("'") + preprocessed.count('"')
        if quote_count > 2:
            risk_score += min(quote_count - 2, 10)
            detections.append({'type': 'excessive_quotes', 'count': quote_count})
        
        is_malicious = risk_score > 15 or len(detections) >= 3
        
        return {
            'is_malicious': is_malicious,
            'risk_score': risk_score,
            'detections': detections,
            'confidence': min(risk_score / 50.0, 1.0)
        }
    
    def predict(self, input_string):
        """Predict SQL injection for a single input"""
        # Rule-based detection
        rule_result = self.rule_based_detection(input_string)
        
        result = {
            'input': input_string,
            'timestamp': datetime.now().isoformat(),
            'rule_based': rule_result,
            'ml_predictions': {},
            'final_prediction': rule_result['is_malicious'],
            'confidence': rule_result['confidence']
        }
        
        # ML-based detection if models are available
        if self.models:
            try:
                # Use the same simple features as training
                simple_features = self.extract_simple_features(input_string)
                
                # TF-IDF
                tfidf_features = self.vectorizer.transform([input_string])
                
                # Combine features
                from scipy.sparse import hstack
                combined_features = hstack([tfidf_features, np.array(simple_features).reshape(1, -1)])
                
                ml_predictions = {}
                for name, model in self.models.items():
                    pred = model.predict(combined_features)[0]
                    pred_proba = model.predict_proba(combined_features)[0]
                    
                    ml_predictions[name] = {
                        'prediction': bool(pred),
                        'probability': float(pred_proba[1])
                    }
                
                result['ml_predictions'] = ml_predictions
                
                # Ensemble decision
                ml_votes = sum(1 for pred in ml_predictions.values() if pred['prediction'])
                ml_confidence = np.mean([pred['probability'] for pred in ml_predictions.values()])
                
                # Combine rule-based and ML results
                if ml_votes >= 1:  # If any ML model detects threat
                    result['final_prediction'] = True
                    result['confidence'] = max(rule_result['confidence'], ml_confidence)
                elif rule_result['is_malicious'] and ml_confidence > 0.3:
                    result['final_prediction'] = True
                    result['confidence'] = (rule_result['confidence'] + ml_confidence) / 2
                else:
                    result['confidence'] = max(rule_result['confidence'], ml_confidence * 0.5)
                
            except Exception as e:
                print(f"Error in ML prediction: {e}")
        
        return result
    
    def save_models(self, model_dir):
        """Save trained models"""
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        # Save ML models
        for name, model in self.models.items():
            joblib.dump(model, f"{model_dir}/sqli_{name}_model.pkl")
        
        # Save vectorizer
        joblib.dump(self.vectorizer, f"{model_dir}/sqli_vectorizer.pkl")
        
        # Save feature names for consistency
        if self.feature_names:
            with open(f"{model_dir}/feature_names.pkl", 'wb') as f:
                pickle.dump(self.feature_names, f)
    
    def load_models(self, model_dir):
        """Load trained models"""
        import os
        try:
            model_files = ['sqli_random_forest_model.pkl', 'sqli_logistic_regression_model.pkl']
            for model_file in model_files:
                if os.path.exists(f"{model_dir}/{model_file}"):
                    model_name = model_file.replace('sqli_', '').replace('_model.pkl', '')
                    self.models[model_name] = joblib.load(f"{model_dir}/{model_file}")
            
            # Load vectorizer
            if os.path.exists(f"{model_dir}/sqli_vectorizer.pkl"):
                self.vectorizer = joblib.load(f"{model_dir}/sqli_vectorizer.pkl")
            
            # Load feature names
            if os.path.exists(f"{model_dir}/feature_names.pkl"):
                with open(f"{model_dir}/feature_names.pkl", 'rb') as f:
                    self.feature_names = pickle.load(f)
                
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


# Test the fixed detector
if __name__ == "__main__":
    detector = SQLInjectionDetector()
    
    # Load models if they exist
    detector.load_models('backend/models/web_security')
    
    test_samples = [
        "normal user input",
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin'--"
    ]
    
    print("Testing Fixed SQL Injection Detector:")
    print("-" * 40)
    
    for sample in test_samples:
        result = detector.predict(sample)
        status = "MALICIOUS" if result['final_prediction'] else "SAFE"
        print(f"'{sample}' -> {status} (confidence: {result['confidence']:.2f})")
        
        if result['ml_predictions']:
            print(f"  ML predictions: {result['ml_predictions']}")
        
        print("-" * 40)