"""
Complete Fast Cyberbullying Detection Module with Twitter Monitor
Includes TwitterMonitor class for social media monitoring
"""

import pandas as pd
import numpy as np
import pickle
import re
import nltk
import os
import logging
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix, accuracy_score, 
                           precision_score, recall_score, f1_score, precision_recall_curve, 
                           roc_auc_score, make_scorer)
from sklearn.pipeline import Pipeline
import joblib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import threading
import time

# Twitter monitoring imports
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    logging.warning("Tweepy not installed. Twitter monitoring will not be available.")

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
    except:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('enhanced_cyberbullying_training.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCyberbullyingDetector:
    """Enhanced Fast Cyberbullying Detector"""
    
    def __init__(self, model_path: str = "backend/models/cyberbullying/"):
        self.model_path = model_path
        self.vectorizer = None
        self.model = None
        self.pipeline = None
        self.transformer_model = None
        self.optimal_threshold = 0.65
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
        
        # Skip transformer model for faster initialization
        logger.info("Fast detector initialized (no transformer for speed)")
        self.transformer_model = None
    
    def enhanced_preprocess_text(self, text: str) -> str:
        """Enhanced preprocessing that preserves cyberbullying indicators"""
        if not isinstance(text, str):
            return ""
        
        # Store original for pattern analysis
        original = text.lower()
        
        # Handle contractions (reduced list for speed)
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "shouldn't": "should not", "wouldn't": "would not", "couldn't": "could not",
            "you're": "you are", "i'm": "i am", "he's": "he is", "she's": "she is",
            "it's": "it is", "we're": "we are", "they're": "they are"
        }
        
        text = text.lower()
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Preserve important patterns before cleaning
        threat_markers = []
        hate_markers = []
        
        # Extract threat patterns
        threat_patterns = [r'kill\s+you', r'die\s+\w+', r'hurt\s+you', r'beat\s+you']
        for pattern in threat_patterns:
            if re.search(pattern, text):
                threat_markers.append('[THREAT]')
        
        # Extract hate patterns  
        hate_patterns = [r'hate\s+you', r'can\'t\s+stand\s+you', r'despise\s+you']
        for pattern in hate_patterns:
            if re.search(pattern, text):
                hate_markers.append('[HATE]')
        
        # Handle URLs and mentions (preserve context)
        text = re.sub(r'http\S+|www\S+|https\S+', '[URL]', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', '[USER]', text)
        text = re.sub(r'#(\w+)', r'hashtag_\1', text)  # Preserve hashtag content
        
        # Handle repeated characters more carefully
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)  # sooooo -> soo
        
        # Handle ALL CAPS (preserve intensity indication)
        caps_count = sum(1 for c in original if c.isupper())
        if caps_count > len(original) * 0.5:  # More than 50% caps
            text = text + ' [SHOUTING]'
        
        # Preserve punctuation patterns that indicate intensity
        exclamation_count = original.count('!')
        question_count = original.count('?')
        if exclamation_count > 2:
            text = text + ' [EXCITED]'
        if question_count > 1 and exclamation_count > 0:
            text = text + ' [AGGRESSIVE_QUESTION]'
        
        # Remove some special characters but keep sentence structure
        text = re.sub(r'[^\w\s!?.,\-\[\]]', ' ', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Add preserved markers back
        if threat_markers:
            text = text + ' ' + ' '.join(threat_markers)
        if hate_markers:
            text = text + ' ' + ' '.join(hate_markers)
        
        # Don't over-filter - preserve context
        return text if len(text) > 2 else original

    def create_enhanced_vectorizer(self) -> TfidfVectorizer:
        """Create FAST TF-IDF vectorizer with optimized parameters"""
        return TfidfVectorizer(
            max_features=8000,      # Reduced from 15000 for speed
            ngram_range=(1, 2),     # Only bigrams, no trigrams for speed
            stop_words='english',
            lowercase=True,
            min_df=5,              # Increased to filter noise
            max_df=0.8,            # Adjusted for better discrimination
            sublinear_tf=True,
            analyzer='word',
            token_pattern=r'(?u)\b\w\w+\b|\[[\w_]+\]',  # Include our special tokens
        )

    def load_and_preprocess_data(self, dataset_paths: List[str]) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """Load and preprocess multiple cyberbullying datasets with enhanced balancing"""
        all_dataframes = []
        
        for dataset_path in dataset_paths:
            try:
                logger.info(f"Loading dataset: {dataset_path}")
                df = pd.read_csv(dataset_path, encoding='utf-8', on_bad_lines='skip')
                
                # Handle different dataset formats
                processed_df = self._standardize_dataset_format(df, dataset_path)
                if processed_df is not None and len(processed_df) > 0:
                    all_dataframes.append(processed_df)
                    logger.info(f"Loaded {len(processed_df)} samples from {dataset_path}")
                
            except Exception as e:
                logger.error(f"Error loading {dataset_path}: {e}")
                continue
        
        if not all_dataframes:
            raise ValueError("No datasets could be loaded successfully!")
        
        # Combine all datasets
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Enhanced preprocessing
        combined_df['cleaned_text'] = combined_df['text'].apply(self.enhanced_preprocess_text)
        
        # Remove empty texts
        combined_df = combined_df[combined_df['cleaned_text'].str.len() > 0]
        
        # FAST balancing with smaller dataset
        combined_df = self._fast_balance_dataset(combined_df)
        
        X = combined_df['cleaned_text'].values
        y = combined_df['label'].values
        
        logger.info(f"Final dataset size: {len(combined_df)}")
        logger.info(f"Label distribution: {np.bincount(y)}")
        
        return combined_df, X, y

    def _standardize_dataset_format(self, df: pd.DataFrame, dataset_path: str) -> Optional[pd.DataFrame]:
        """Enhanced dataset format standardization"""
        standardized_df = pd.DataFrame()
        filename = os.path.basename(dataset_path).lower()
        
        try:
            logger.info(f"Dataset {filename} columns: {list(df.columns)}")
            logger.info(f"Dataset shape: {df.shape}")
            
            # Handle cyberbullying_tweets.csv
            if 'cyberbullying_tweets' in filename:
                if 'tweet_text' in df.columns and 'cyberbullying_type' in df.columns:
                    standardized_df['text'] = df['tweet_text']
                    standardized_df['label'] = (df['cyberbullying_type'] != 'not_cyberbullying').astype(int)
            
            # Handle hatexplain dataset
            elif 'hatexplain' in filename or 'hate' in filename:
                if 'text' in df.columns:
                    standardized_df['text'] = df['text']
                    if 'label' in df.columns:
                        unique_labels = df['label'].unique()
                        logger.info(f"Unique labels in {filename}: {unique_labels}")
                        hate_keywords = ['hate', 'offensive', 'hatespeech']
                        standardized_df['label'] = df['label'].apply(
                            lambda x: 1 if any(keyword in str(x).lower() for keyword in hate_keywords) else 0
                        )
                elif 'comment' in df.columns:
                    standardized_df['text'] = df['comment']
                    if 'label' in df.columns:
                        unique_labels = df['label'].unique()
                        logger.info(f"Generic fallback - unique labels: {unique_labels}")
                        negative_keywords = ['normal']
                        standardized_df['label'] = df['label'].apply(
                            lambda x: 0 if any(keyword in str(x).lower() for keyword in negative_keywords) else 1
                        )
            
            # Handle parsed datasets (aggression, attack, toxicity)
            elif any(keyword in filename for keyword in ['aggression', 'attack', 'toxicity']):
                text_candidates = [col for col in df.columns if any(keyword in col.lower() 
                                 for keyword in ['text', 'comment', 'tweet', 'message', 'content'])]
                label_candidates = [col for col in df.columns if any(keyword in col.lower() 
                                  for keyword in ['label', 'class', 'toxic', 'aggression', 'target', 'attack', 'oh_label'])]
                
                if text_candidates and label_candidates:
                    standardized_df['text'] = df[text_candidates[0]]
                    label_col = label_candidates[0]
                    
                    if df[label_col].dtype == 'object':
                        standardized_df['label'] = df[label_col].apply(
                            lambda x: 1 if str(x).lower() in ['yes', 'true', '1', 'toxic', 'aggressive', 'hate', 'offensive'] else 0
                        )
                    else:
                        standardized_df['label'] = (df[label_col] > 0).astype(int)
            
            # Handle Twitter datasets
            elif 'twitter' in filename:
                possible_text_cols = []
                possible_label_cols = []
                
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['text', 'tweet', 'comment', 'content']):
                        possible_text_cols.append(col)
                    elif any(keyword in col_lower for keyword in ['label', 'class', 'category', 'racist', 'sexist', 'target', 'annotation', 'oh_label']):
                        possible_label_cols.append(col)
                
                if possible_text_cols:
                    standardized_df['text'] = df[possible_text_cols[0]]
                    
                    if possible_label_cols:
                        label_col = possible_label_cols[0]
                        if df[label_col].dtype == 'object':
                            unique_vals = df[label_col].unique()
                            logger.info(f"Unique values in {label_col}: {unique_vals}")
                            
                            if 'neither' in str(unique_vals).lower():
                                standardized_df['label'] = (df[label_col] != 'neither').astype(int)
                            else:
                                negative_keywords = ['not', 'normal', 'neutral', 'none', '0', 'neither', 'okay', 'no']
                                standardized_df['label'] = df[label_col].apply(
                                    lambda x: 0 if any(keyword in str(x).lower() for keyword in negative_keywords) else 1
                                )
                        else:
                            standardized_df['label'] = (df[label_col] > 0).astype(int)
            
            # Generic fallback
            if standardized_df.empty:
                all_cols = df.columns.tolist()
                text_col = None
                label_col = None
                
                for col in all_cols:
                    if any(keyword in col.lower() for keyword in ['text', 'comment', 'tweet', 'message', 'content']):
                        text_col = col
                        break
                
                for col in all_cols:
                    if any(keyword in col.lower() for keyword in ['label', 'class', 'target', 'category', 'oh_label']):
                        label_col = col
                        break
                
                if text_col and label_col:
                    standardized_df['text'] = df[text_col]
                    
                    if df[label_col].dtype == 'object':
                        unique_labels = df[label_col].unique()
                        logger.info(f"Generic fallback - unique labels: {unique_labels}")
                        
                        if len(unique_labels) == 2:
                            standardized_df['label'] = (df[label_col] == unique_labels[1]).astype(int)
                        else:
                            negative_keywords = ['not', 'normal', 'neutral', 'none', '0', 'neither']
                            standardized_df['label'] = df[label_col].apply(
                                lambda x: 0 if any(keyword in str(x).lower() for keyword in negative_keywords) else 1
                            )
                    else:
                        standardized_df['label'] = (df[label_col] > 0).astype(int)
            
            # Final validation and cleaning
            if not standardized_df.empty:
                standardized_df = standardized_df.dropna()
                standardized_df = standardized_df[standardized_df['text'].str.len() > 0]
                standardized_df['label'] = standardized_df['label'].astype(int)
                standardized_df = standardized_df[standardized_df['label'].isin([0, 1])]
                
                logger.info(f"Processed {filename}: {len(standardized_df)} samples, "
                           f"labels: {standardized_df['label'].value_counts().to_dict()}")
                
                return standardized_df
            
        except Exception as e:
            logger.error(f"Error standardizing dataset {filename}: {e}")
        
        logger.warning(f"Could not process dataset: {filename}")
        return None

    def _fast_balance_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """FAST dataset balancing with smaller target size"""
        label_counts = df['label'].value_counts()
        logger.info(f"Original distribution: {label_counts.to_dict()}")
        
        if len(label_counts) == 2:
            minority_count = label_counts.min()
            majority_count = label_counts.max()
            minority_label = label_counts.idxmin()
            majority_label = label_counts.idxmax()
            
            # MUCH smaller target size for FAST training
            target_size = min(minority_count * 2, 25000)  # Reduced from 75000 to 25000
            
            minority_data = df[df['label'] == minority_label]
            majority_data = df[df['label'] == majority_label]
            
            # Sample with stratification if possible
            if len(minority_data) >= target_size:
                minority_sample = minority_data.sample(n=target_size, random_state=42)
            else:
                # Oversample minority class if needed
                minority_sample = minority_data.sample(n=target_size, replace=True, random_state=42)
            
            if len(majority_data) >= target_size:
                majority_sample = majority_data.sample(n=target_size, random_state=42)
            else:
                majority_sample = majority_data
            
            balanced_df = pd.concat([minority_sample, majority_sample], ignore_index=True)
            
            logger.info(f"FAST balanced dataset from {len(df)} to {len(balanced_df)} samples")
            logger.info(f"New distribution: {balanced_df['label'].value_counts().to_dict()}")
            
            return balanced_df
        
        return df

    def enhanced_train_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """FIXED training with Gradient Boosting instead of SVM"""
        
        # Split the data with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create enhanced vectorizer
        vectorizer = self.create_enhanced_vectorizer()
        
        # Fit vectorizer and transform data
        logger.info("Vectorizing text data with optimized features...")
        start_time = time.time()
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        vectorize_time = time.time() - start_time
        logger.info(f"Vectorization completed in {vectorize_time:.2f} seconds")
        
        # Store vectorizer
        self.vectorizer = vectorizer
        
        # Define FAST models - NO SVM, using Gradient Boosting instead
        models = {
            'logistic': LogisticRegression(
                class_weight='balanced',
                random_state=42,
                max_iter=1000
            ),
            'random_forest': RandomForestClassifier(
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                random_state=42,
                n_estimators=100,  # Start with reasonable size
                learning_rate=0.1,
                max_depth=5
            )
        }
        
        # FAST hyperparameter tuning with smaller search spaces
        best_models = {}
        
        # Logistic Regression - minimal tuning
        logger.info("Quick tuning Logistic Regression...")
        lr_params = {
            'C': [0.5, 1.0, 2.0],  # Reduced search space
            'solver': ['lbfgs']     # Use fastest solver only
        }
        
        start_time = time.time()
        lr_grid = GridSearchCV(
            models['logistic'], lr_params, cv=3, 
            scoring='f1', n_jobs=-1, verbose=0
        )
        lr_grid.fit(X_train_vec, y_train)
        best_models['logistic'] = lr_grid.best_estimator_
        lr_time = time.time() - start_time
        logger.info(f"Best LR params: {lr_grid.best_params_} (trained in {lr_time:.2f}s)")
        
        # Random Forest - minimal tuning
        logger.info("Quick tuning Random Forest...")
        rf_params = {
            'n_estimators': [100, 150],   # Reduced options
            'max_depth': [10, 15],        # Reduced options
            'min_samples_split': [5]      # Fixed value
        }
        
        start_time = time.time()
        rf_grid = GridSearchCV(
            models['random_forest'], rf_params, cv=3,
            scoring='f1', n_jobs=-1, verbose=0
        )
        rf_grid.fit(X_train_vec, y_train)
        best_models['random_forest'] = rf_grid.best_estimator_
        rf_time = time.time() - start_time
        logger.info(f"Best RF params: {rf_grid.best_params_} (trained in {rf_time:.2f}s)")
        
        # Gradient Boosting - FAST alternative to SVM
        logger.info("Quick tuning Gradient Boosting...")
        gb_params = {
            'n_estimators': [50, 100],    # Smaller than RF for speed
            'learning_rate': [0.1, 0.2], # Higher learning rates for speed
            'max_depth': [3, 5]           # Shallow trees for speed
        }
        
        start_time = time.time()
        gb_grid = GridSearchCV(
            models['gradient_boosting'], gb_params, cv=3,
            scoring='f1', n_jobs=-1, verbose=0
        )
        gb_grid.fit(X_train_vec, y_train)
        best_models['gradient_boosting'] = gb_grid.best_estimator_
        gb_time = time.time() - start_time
        logger.info(f"Best GB params: {gb_grid.best_params_} (trained in {gb_time:.2f}s)")
        
        # Create FIXED voting ensemble - USE SOFT VOTING for predict_proba
        logger.info("Training FIXED ensemble model...")
        ensemble = VotingClassifier(
            estimators=[
                ('lr', best_models['logistic']),
                ('rf', best_models['random_forest']),
                ('gb', best_models['gradient_boosting'])  # GB instead of SVM
            ],
            voting='soft',  # FIXED: Use soft voting to get predict_proba
            weights=[1.2, 1.0, 0.9]  # Slightly favor LR, then RF, then GB
        )
        
        start_time = time.time()
        ensemble.fit(X_train_vec, y_train)
        ensemble_time = time.time() - start_time
        logger.info(f"Ensemble training completed in {ensemble_time:.2f} seconds")
        
        # FAST cross-validation evaluation
        logger.info("Quick cross-validation...")
        cv_scores = cross_val_score(ensemble, X_train_vec, y_train, 
                                   cv=3,  # Reduced from 5 folds
                                   scoring='f1')
        logger.info(f"CV F1 scores: {cv_scores}")
        logger.info(f"Mean CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Evaluate on test set
        y_pred = ensemble.predict(X_test_vec)
        y_pred_proba = ensemble.predict_proba(X_test_vec)  # This now works with soft voting
        
        # Calculate comprehensive metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        logger.info("FIXED Model Results:")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1 Score: {f1:.4f}")
        
        # Create enhanced pipeline
        self.pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('ensemble', ensemble)
        ])
        
        # Calculate optimal threshold
        optimal_threshold = self._optimize_threshold(y_test, y_pred_proba[:, 1])
        self.optimal_threshold = optimal_threshold
        logger.info(f"Optimal threshold: {optimal_threshold:.4f}")
        
        # Save models
        model_file = os.path.join(self.model_path, 'fast_cyberbullying_model.pkl')
        joblib.dump(self.pipeline, model_file)
        
        # Save optimal threshold
        threshold_file = os.path.join(self.model_path, 'optimal_threshold.pkl')
        joblib.dump(optimal_threshold, threshold_file)
        
        # Feature importance analysis
        feature_importance = self._analyze_feature_importance(best_models, vectorizer)
        
        logger.info(f"FIXED model saved to {model_file}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cv_f1_mean': cv_scores.mean(),
            'cv_f1_std': cv_scores.std(),
            'optimal_threshold': optimal_threshold,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': feature_importance,
            'model_info': {
                'best_lr_params': lr_grid.best_params_,
                'best_rf_params': rf_grid.best_params_,
                'best_gb_params': gb_grid.best_params_  # GB instead of SVM
            },
            'training_times': {
                'vectorization': vectorize_time,
                'logistic_regression': lr_time,
                'random_forest': rf_time,
                'gradient_boosting': gb_time,
                'ensemble': ensemble_time
            }
        }

    def _optimize_threshold(self, y_true, y_proba):
        """Find optimal threshold balancing precision and recall"""
        thresholds = np.arange(0.3, 0.8, 0.05)  # Smaller range for speed
        best_threshold = 0.5
        best_score = 0
        
        for threshold in thresholds:
            y_pred_thresh = (y_proba >= threshold).astype(int)
            try:
                f1 = f1_score(y_true, y_pred_thresh)
                precision = precision_score(y_true, y_pred_thresh)
                
                # Weighted score favoring F1 but requiring minimum precision
                if precision > 0.6:  # Minimum precision requirement
                    weighted_score = f1 * 0.7 + precision * 0.3
                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_threshold = threshold
            except:
                continue
        
        return best_threshold

    def _analyze_feature_importance(self, models, vectorizer):
        """Analyze feature importance across models"""
        feature_names = vectorizer.get_feature_names_out()
        
        # Get importance from Random Forest
        rf_importance = models['random_forest'].feature_importances_
        
        # Get coefficients from Logistic Regression
        lr_coefs = np.abs(models['logistic'].coef_[0])
        
        # Get importance from Gradient Boosting
        gb_importance = models['gradient_boosting'].feature_importances_
        
        # Combine importances (normalize first)
        rf_norm = rf_importance / np.max(rf_importance)
        lr_norm = lr_coefs / np.max(lr_coefs)
        gb_norm = gb_importance / np.max(gb_importance)
        
        # Average the three importance scores
        combined_importance = (rf_norm + lr_norm + gb_norm) / 3
        
        # Get top features
        top_indices = np.argsort(combined_importance)[-50:][::-1]
        
        return [
            (feature_names[idx], combined_importance[idx]) 
            for idx in top_indices
        ]

    def load_model(self) -> bool:
        """Load pre-trained fast model"""
        try:
            model_file = os.path.join(self.model_path, 'fast_cyberbullying_model.pkl')
            threshold_file = os.path.join(self.model_path, 'optimal_threshold.pkl')
            
            if os.path.exists(model_file):
                self.pipeline = joblib.load(model_file)
                logger.info("Fast cyberbullying model loaded successfully")
                
                # Load optimal threshold if available
                if os.path.exists(threshold_file):
                    self.optimal_threshold = joblib.load(threshold_file)
                    logger.info(f"Optimal threshold loaded: {self.optimal_threshold:.4f}")
                
                return True
            else:
                # Fallback to enhanced model
                enhanced_model_file = os.path.join(self.model_path, 'enhanced_cyberbullying_model.pkl')
                if os.path.exists(enhanced_model_file):
                    self.pipeline = joblib.load(enhanced_model_file)
                    logger.info("Enhanced cyberbullying model loaded as fallback")
                    return True
                else:
                    logger.warning("No pre-trained model found")
                    return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def _analyze_severity_features(self, text: str) -> Dict:
        """Fast severity feature analysis"""
        text_lower = text.lower()
        
        # Simplified patterns for speed
        threat_patterns = ['kill', 'die', 'hurt', 'harm', 'destroy', 'beat', 'punch', 'attack']
        attack_patterns = ['ugly', 'stupid', 'fat', 'worthless', 'pathetic', 'loser', 'idiot', 'moron']
        hate_patterns = ['hate', 'despise', 'can\'t stand']
        intensity_words = ['so', 'really', 'very', 'extremely', 'totally']
        
        return {
            'has_threats': any(pattern in text_lower for pattern in threat_patterns),
            'has_personal_attacks': any(pattern in text_lower for pattern in attack_patterns),
            'has_hate_speech': any(pattern in text_lower for pattern in hate_patterns),
            'intensity_count': sum(1 for word in intensity_words if word in text_lower),
            'threat_count': sum(1 for pattern in threat_patterns if pattern in text_lower),
            'attack_count': sum(1 for pattern in attack_patterns if pattern in text_lower),
            'caps_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'exclamation_count': text.count('!')
        }

    def predict_with_dynamic_threshold(self, text: str) -> Dict:
        """FIXED prediction with context-aware thresholds"""
        if not self.pipeline and not self.load_model():
            return {"error": "No model available for prediction"}
        
        try:
            cleaned_text = self.enhanced_preprocess_text(text)
            if not cleaned_text:
                return {"is_cyberbullying": False, "confidence": 0.0, "severity": "none"}
            
            # Get traditional model prediction
            prediction_proba = self.pipeline.predict_proba([cleaned_text])[0]
            traditional_score = prediction_proba[1] if len(prediction_proba) > 1 else 0
            
            # No transformer for speed
            transformer_score = 0.0
            
            # Fast feature analysis
            severity_indicators = self._analyze_severity_features(text)
            
            # Dynamic threshold based on content analysis
            base_threshold = self.optimal_threshold
            
            # Adjust threshold based on content
            if severity_indicators['has_threats']:
                threshold = 0.35  # Very sensitive for threats
            elif severity_indicators['has_personal_attacks']:
                threshold = 0.45  # Sensitive for personal attacks
            elif severity_indicators['has_hate_speech']:
                threshold = 0.5   # Moderately sensitive
            else:
                threshold = base_threshold
            
            # Simple scoring (no transformer ensemble)
            confidence = traditional_score
            
            # Apply slight boost for severe content
            if severity_indicators['has_threats']:
                confidence = min(0.95, confidence + 0.2)
            elif severity_indicators['has_personal_attacks']:
                confidence = min(0.95, confidence + 0.1)
            
            prediction = confidence > threshold
            
            # Calculate severity
            if severity_indicators['has_threats']:
                severity = "critical"
            elif severity_indicators['has_personal_attacks'] and confidence > 0.7:
                severity = "high"
            elif confidence > 0.6:
                severity = "medium"
            elif confidence > 0.4:
                severity = "low"
            else:
                severity = "none"
            
            return {
                "is_cyberbullying": bool(prediction),
                "confidence": float(confidence),
                "severity": severity,
                "traditional_score": float(traditional_score),
                "threshold_used": threshold,
                "severity_indicators": severity_indicators,
                "analysis": self._analyze_content(text)
            }
            
        except Exception as e:
            logger.error(f"Fast prediction error: {e}")
            return {"error": str(e)}

    def predict(self, text: str) -> Dict:
        """Main prediction method - uses fast prediction"""
        return self.predict_with_dynamic_threshold(text)

    def _analyze_content(self, text: str) -> Dict:
        """Fast content analysis"""
        text_lower = text.lower()
        
        analysis = {
            "threats": False,
            "personal_attacks": False,
            "discriminatory_language": False,
            "encouraging_harm": False,
            "profanity": False
        }
        
        # Simplified pattern matching for speed
        threat_patterns = ['kill', 'die', 'hurt', 'harm', 'destroy', 'murder']
        analysis["threats"] = any(pattern in text_lower for pattern in threat_patterns)
        
        attack_patterns = ['ugly', 'stupid', 'fat', 'worthless', 'pathetic', 'loser']
        analysis["personal_attacks"] = any(pattern in text_lower for pattern in attack_patterns)
        
        discriminatory_patterns = ['racist', 'sexist', 'homophobic', 'transphobic']
        analysis["discriminatory_language"] = any(pattern in text_lower for pattern in discriminatory_patterns)
        
        harm_patterns = ['suicide', 'cut yourself', 'end it all', 'jump off']
        analysis["encouraging_harm"] = any(pattern in text_lower for pattern in harm_patterns)
        
        profanity_patterns = ['fuck', 'shit', 'bitch', 'asshole']
        analysis["profanity"] = any(pattern in text_lower for pattern in profanity_patterns)
        
        return analysis


class TwitterMonitor:
    """
    Twitter/X monitoring class for real-time cyberbullying detection
    Integrates with the cyberbullying detector to analyze tweets
    """
    
    def __init__(self, api_credentials: Dict, cyberbullying_detector=None):
        """
        Initialize Twitter monitor with API credentials
        
        Args:
            api_credentials: Dict with Twitter API v2 credentials
            cyberbullying_detector: Instance of cyberbullying detector
        """
        if not TWITTER_AVAILABLE:
            raise ImportError("Tweepy not installed. Install with: pip install tweepy")
            
        self.api_credentials = api_credentials
        self.detector = cyberbullying_detector
        self.client = None
        self.api = None
        
        # Initialize Twitter API clients
        self._initialize_twitter_api()
    
    def _initialize_twitter_api(self):
        """Initialize Twitter API v2 client"""
        try:
            # Twitter API v2 client (recommended)
            self.client = tweepy.Client(
                bearer_token=self.api_credentials.get('bearer_token'),
                consumer_key=self.api_credentials.get('api_key'),
                consumer_secret=self.api_credentials.get('api_secret'),
                access_token=self.api_credentials.get('access_token'),
                access_token_secret=self.api_credentials.get('access_secret'),
                wait_on_rate_limit=True
            )
            
            # Test authentication
            try:
                me = self.client.get_me()
                logger.info(f"Twitter API initialized successfully for user: {me.data.username if me.data else 'Unknown'}")
            except Exception as e:
                logger.warning(f"Twitter API authentication test failed: {e}")
                # Continue anyway, might work for public endpoints
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def search_tweets(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """
        Search for tweets containing specific keywords and analyze them
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of tweets to retrieve (10-100)
            
        Returns:
            List of analyzed tweets with cyberbullying detection results
        """
        if not self.client:
            raise Exception("Twitter API not initialized")
        
        if not keywords:
            raise ValueError("Keywords list cannot be empty")
        
        # Limit max_results to API limits
        max_results = min(max(max_results, 10), 100)
        
        try:
            # Build search query
            query = ' OR '.join(keywords)
            
            # Add filters to get diverse content
            query += ' -is:retweet lang:en'  # Exclude retweets, English only
            
            logger.info(f"Searching Twitter for: {query} (max {max_results} results)")
            
            # Search tweets using Twitter API v2
            tweets_response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang', 'context_annotations'],
                user_fields=['username', 'name', 'verified'],
                expansions=['author_id']
            )
            
            if not tweets_response.data:
                logger.info("No tweets found for the given keywords")
                return []
            
            # Process tweets
            results = []
            users_dict = {}
            
            # Create users lookup dictionary
            if tweets_response.includes and 'users' in tweets_response.includes:
                users_dict = {user.id: user for user in tweets_response.includes['users']}
            
            for tweet in tweets_response.data:
                try:
                    # Get user info
                    user = users_dict.get(tweet.author_id, None)
                    username = user.username if user else 'unknown'
                    display_name = user.name if user else 'Unknown User'
                    
                    # Analyze tweet for cyberbullying
                    analysis_result = self._analyze_tweet(tweet.text, tweet, user)
                    
                    # Compile result
                    result = {
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'author': {
                            'username': username,
                            'display_name': display_name,
                            'verified': user.verified if user else False,
                            'user_id': tweet.author_id
                        },
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'metrics': {
                            'retweet_count': tweet.public_metrics['retweet_count'],
                            'like_count': tweet.public_metrics['like_count'],
                            'reply_count': tweet.public_metrics['reply_count'],
                            'quote_count': tweet.public_metrics['quote_count']
                        } if tweet.public_metrics else {},
                        'cyberbullying_analysis': analysis_result,
                        'matched_keywords': [kw for kw in keywords if kw.lower() in tweet.text.lower()],
                        'url': f"https://twitter.com/{username}/status/{tweet.id}"
                    }
                    
                    # Add top-level fields for compatibility
                    result.update({
                        'is_cyberbullying': analysis_result.get('is_cyberbullying', False),
                        'confidence': analysis_result.get('confidence', 0.0),
                        'severity': analysis_result.get('severity', 'none')
                    })
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing tweet {tweet.id}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(results)} tweets")
            return results
            
        except Exception as e:
            logger.error(f"Twitter search failed: {e}")
            if "rate limit" in str(e).lower():
                raise Exception(f"Twitter API rate limit exceeded. Try again later.")
            else:
                raise Exception(f"Twitter search failed: {str(e)}")
    
    def _analyze_tweet(self, text: str, tweet_data=None, user_data=None) -> Dict:
        """
        Analyze a tweet for cyberbullying using the detector
        
        Args:
            text: Tweet text to analyze
            tweet_data: Twitter API tweet object
            user_data: Twitter API user object
            
        Returns:
            Cyberbullying analysis result
        """
        if not self.detector:
            # Fallback analysis without detector
            return self._fallback_analysis(text)
        
        try:
            # Use the cyberbullying detector
            result = self.detector.predict(text)
            
            # Add Twitter-specific context
            result['platform'] = 'twitter'
            result['analyzed_at'] = datetime.now().isoformat()
            
            # Add engagement-based risk factors
            if tweet_data and hasattr(tweet_data, 'public_metrics'):
                metrics = tweet_data.public_metrics
                engagement_score = (
                    metrics.get('like_count', 0) + 
                    metrics.get('retweet_count', 0) * 2 +  # Retweets have more impact
                    metrics.get('reply_count', 0)
                )
                
                # High engagement + cyberbullying = higher severity
                if result.get('is_cyberbullying', False) and engagement_score > 50:
                    current_severity = result.get('severity', 'low')
                    if current_severity == 'low':
                        result['severity'] = 'medium'
                    elif current_severity == 'medium':
                        result['severity'] = 'high'
                    
                    result['engagement_amplification'] = True
                    result['engagement_score'] = engagement_score
            
            return result
            
        except Exception as e:
            logger.error(f"Cyberbullying analysis failed: {e}")
            # Return fallback analysis
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict:
        """
        Fallback analysis when detector is not available
        Uses simple keyword-based detection
        """
        cyberbullying_keywords = [
            'hate', 'stupid', 'idiot', 'kill', 'die', 'ugly', 'loser', 'pathetic',
            'worthless', 'trash', 'garbage', 'disgusting', 'kill yourself'
        ]
        
        text_lower = text.lower()
        matches = [word for word in cyberbullying_keywords if word in text_lower]
        
        is_cyberbullying = len(matches) > 0
        confidence = min(0.9, 0.3 + len(matches) * 0.2)
        
        severity = 'none'
        if len(matches) >= 3:
            severity = 'high'
        elif len(matches) >= 2:
            severity = 'medium'
        elif len(matches) >= 1:
            severity = 'low'
        
        return {
            'is_cyberbullying': is_cyberbullying,
            'confidence': confidence,
            'severity': severity,
            'method': 'fallback_keywords',
            'matched_keywords': matches,
            'platform': 'twitter',
            'analyzed_at': datetime.now().isoformat()
        }
    
    def monitor_hashtags(self, hashtags: List[str], duration_minutes: int = 60) -> List[Dict]:
        """
        Monitor specific hashtags for cyberbullying content
        
        Args:
            hashtags: List of hashtags to monitor (without #)
            duration_minutes: How long to monitor (max 60 minutes)
            
        Returns:
            List of flagged tweets
        """
        # Format hashtags properly
        formatted_hashtags = [f"#{tag.lstrip('#')}" for tag in hashtags]
        
        # Use search_tweets with hashtag query
        return self.search_tweets(formatted_hashtags, max_results=100)
    
    def validate_credentials(self) -> Dict:
        """
        Validate Twitter API credentials and return status
        
        Returns:
            Dictionary with validation results
        """
        try:
            if not self.client:
                return {
                    'valid': False,
                    'error': 'Client not initialized',
                    'details': 'Twitter API client could not be created'
                }
            
            # Test API access
            me = self.client.get_me()
            
            if me.data:
                return {
                    'valid': True,
                    'user': {
                        'username': me.data.username,
                        'name': me.data.name,
                        'id': me.data.id
                    },
                    'rate_limits': 'Available'  # Could check specific limits
                }
            else:
                return {
                    'valid': False,
                    'error': 'Authentication failed',
                    'details': 'Could not retrieve user information'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'details': 'API credentials validation failed'
            }


class EnhancedModelTester:
    """Fast testing framework for cyberbullying detection"""
    
    def __init__(self, detector):
        self.detector = detector
        self.test_cases = self._create_test_suite()
    
    def _create_test_suite(self) -> List[Dict]:
        """Create test suite with diverse examples"""
        return [
            # Obvious cyberbullying (should detect)
            {"text": "You're so ugly and stupid, nobody likes you", "expected": True, "category": "personal_attack"},
            {"text": "Kill yourself, you worthless piece of trash", "expected": True, "category": "threat"},
            {"text": "I hate you so much, go die!", "expected": True, "category": "hate_speech"},
            {"text": "You fat loser, you should just disappear", "expected": True, "category": "harassment"},
            {"text": "Nobody wants you here, just leave and never come back", "expected": True, "category": "exclusion"},
            
            # Subtle cases
            {"text": "Wow, you really thought that was a good idea? That's... interesting.", "expected": True, "category": "subtle_mockery"},
            {"text": "I'm sure someone, somewhere might find you attractive", "expected": True, "category": "backhanded_insult"},
            
            # Safe content
            {"text": "You're such an amazing person! Keep being awesome!", "expected": False, "category": "positive"},
            {"text": "Just had a great day at the park with friends", "expected": False, "category": "neutral"},
            {"text": "Hey, how are you doing today? Hope you're well!", "expected": False, "category": "friendly"},
            {"text": "Looking forward to the weekend", "expected": False, "category": "casual"},
            
            # Edge cases
            {"text": "That movie was fucking amazing!", "expected": False, "category": "casual_profanity"},
            {"text": "You're killing it in this game!", "expected": False, "category": "positive_slang"},
            {"text": "This assignment is killing me", "expected": False, "category": "metaphorical"},
            
            # Enthusiasm
            {"text": "I LOVE THIS SONG SO MUCH!!!", "expected": False, "category": "enthusiasm"},
        ]
    
    def run_quick_test(self) -> Dict:
        """Run quick test suite and analyze results"""
        results = []
        
        logger.info("Running FAST test suite...")
        logger.info("=" * 50)
        
        for i, test_case in enumerate(self.test_cases, 1):
            text = test_case['text']
            expected = test_case['expected']
            category = test_case['category']
            
            # Get prediction
            result = self.detector.predict(text)
            predicted = result.get('is_cyberbullying', False)
            confidence = result.get('confidence', 0)
            threshold_used = result.get('threshold_used', 0.5)
            
            is_correct = predicted == expected
            
            # Store result
            test_result = {
                'test_id': i,
                'text': text,
                'expected': expected,
                'predicted': predicted,
                'correct': is_correct,
                'confidence': confidence,
                'threshold_used': threshold_used,
                'category': category
            }
            results.append(test_result)
            
            # Display result
            status = "✓ PASS" if is_correct else "✗ FAIL"
            logger.info(f"Test {i:2d}: {status} - {category}")
            logger.info(f"  Text: {text}")
            logger.info(f"  Expected: {expected}, Predicted: {predicted}")
            logger.info(f"  Confidence: {confidence:.3f}, Threshold: {threshold_used:.3f}")
            
            if not is_correct:
                if expected and not predicted:
                    logger.info("  → FALSE NEGATIVE: Missed actual cyberbullying")
                elif not expected and predicted:
                    logger.info("  → FALSE POSITIVE: Incorrectly flagged safe content")
            logger.info("")
        
        # Calculate overall metrics
        correct_predictions = sum(1 for r in results if r['correct'])
        total_tests = len(results)
        overall_accuracy = correct_predictions / total_tests
        
        logger.info("=" * 50)
        logger.info("FAST TEST RESULTS:")
        logger.info("=" * 50)
        logger.info(f"Overall Accuracy: {overall_accuracy:.1%} ({correct_predictions}/{total_tests})")
        
        return {
            'overall_accuracy': overall_accuracy,
            'detailed_results': results,
            'test_passed': overall_accuracy >= 0.75  # 75% threshold for fast model
        }


# Backwards compatibility
class CyberbullyingDetector(EnhancedCyberbullyingDetector):
    """Backwards compatibility wrapper"""
    def __init__(self, model_path: str = "backend/models/cyberbullying/"):
        super().__init__(model_path)


# Training functions
def fast_train_with_all_datasets():
    """Train FAST model with available datasets - for API compatibility"""
    detector = EnhancedCyberbullyingDetector()
    
    # List all available datasets
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
    
    # Filter existing files
    existing_datasets = [path for path in dataset_paths if os.path.exists(path)]
    
    if not existing_datasets:
        logger.error("No datasets found! Please ensure datasets are in the correct location.")
        return None
    
    logger.info(f"Found {len(existing_datasets)} datasets")
    
    # Load and preprocess data
    df, X, y = detector.load_and_preprocess_data(existing_datasets)
    
    # Train model
    results = detector.enhanced_train_model(X, y)
    
    logger.info("Fast training completed!")
    logger.info(f"Final accuracy: {results['accuracy']:.4f}")
    
    return results

# Alias for compatibility
train_with_all_datasets = fast_train_with_all_datasets


def run_fast_testing():
    """Run the FAST testing framework"""
    detector = EnhancedCyberbullyingDetector()
    
    # Load model
    if not detector.load_model():
        logger.error("No model found. Please train the model first.")
        return None
    
    # Create and run tester
    tester = EnhancedModelTester(detector)
    results = tester.run_quick_test()
    
    return results


if __name__ == "__main__":
    # Train FAST model with all datasets
    fast_train_with_all_datasets()
    
    # Run FAST testing
    logger.info("\n" + "=" * 50)
    logger.info("RUNNING FAST TESTING")
    logger.info("=" * 50)
    run_fast_testing()