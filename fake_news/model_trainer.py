import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.model_selection import cross_val_score, GridSearchCV
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Input, Concatenate
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import pickle
import joblib
import torch
from torch.utils.data import Dataset

class FakeNewsDataset(Dataset):
    """PyTorch dataset for transformer models"""
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

class FakeNewsModelTrainer:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
        self.tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
        self.models = {}
        self.feature_columns = []
        
    def train_traditional_models(self, X_train, X_test, y_train, y_test, feature_cols):
        """Train traditional ML models with text and engineered features"""
        
        # Separate text and features
        X_train_text = X_train['cleaned_text']
        X_test_text = X_test['cleaned_text']
        X_train_features = X_train[feature_cols]
        X_test_features = X_test[feature_cols]
        
        # Vectorize text
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train_text)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test_text)
        
        # Combine text features with engineered features
        from scipy.sparse import hstack
        X_train_combined = hstack([X_train_tfidf, X_train_features.values])
        X_test_combined = hstack([X_test_tfidf, X_test_features.values])
        
        models_to_train = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'naive_bayes': MultinomialNB(),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42)
        }
        
        results = {}
        
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...")
            
            if name == 'naive_bayes':
                # Naive Bayes works better with just TF-IDF features
                model.fit(X_train_tfidf, y_train)
                pred = model.predict(X_test_tfidf)
                pred_proba = model.predict_proba(X_test_tfidf)[:, 1]
            else:
                model.fit(X_train_combined, y_train)
                pred = model.predict(X_test_combined)
                pred_proba = model.predict_proba(X_test_combined)[:, 1]
            
            accuracy = accuracy_score(y_test, pred)
            auc_score = roc_auc_score(y_test, pred_proba)
            
            print(f"{name} - Accuracy: {accuracy:.4f}, AUC: {auc_score:.4f}")
            print(classification_report(y_test, pred))
            
            results[name] = {
                'accuracy': accuracy,
                'auc': auc_score,
                'predictions': pred,
                'probabilities': pred_proba
            }
            
            self.models[name] = model
        
        return results
    
    def build_hybrid_model(self, vocab_size, feature_dim, max_length=100):
        """Build hybrid model combining LSTM and engineered features"""
        
        # Text input branch
        text_input = Input(shape=(max_length,), name='text_input')
        embedding = Embedding(vocab_size, 128, input_length=max_length)(text_input)
        lstm1 = LSTM(64, dropout=0.2, recurrent_dropout=0.2, return_sequences=True)(embedding)
        lstm2 = LSTM(32, dropout=0.2, recurrent_dropout=0.2)(lstm1)
        
        # Feature input branch
        feature_input = Input(shape=(feature_dim,), name='feature_input')
        feature_dense = Dense(16, activation='relu')(feature_input)
        feature_dropout = Dropout(0.3)(feature_dense)
        
        # Combine branches
        combined = Concatenate()([lstm2, feature_dropout])
        dense1 = Dense(32, activation='relu')(combined)
        dropout = Dropout(0.3)(dense1)
        output = Dense(1, activation='sigmoid')(dropout)
        
        model = Model(inputs=[text_input, feature_input], outputs=output)
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_hybrid_model(self, X_train, X_test, y_train, y_test, feature_cols, max_length=100, epochs=10):
        """Train hybrid LSTM + features model"""
        
        # Prepare text data
        self.tokenizer.fit_on_texts(X_train['cleaned_text'])
        
        X_train_seq = self.tokenizer.texts_to_sequences(X_train['cleaned_text'])
        X_test_seq = self.tokenizer.texts_to_sequences(X_test['cleaned_text'])
        
        X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
        X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')
        
        # Prepare feature data
        X_train_features = X_train[feature_cols].values
        X_test_features = X_test[feature_cols].values
        
        # Build model
        vocab_size = len(self.tokenizer.word_index) + 1
        feature_dim = len(feature_cols)
        
        hybrid_model = self.build_hybrid_model(vocab_size, feature_dim, max_length)
        
        # Train model
        history = hybrid_model.fit(
            [X_train_pad, X_train_features], y_train,
            batch_size=32,
            epochs=epochs,
            validation_data=([X_test_pad, X_test_features], y_test),
            verbose=1
        )
        
        # Evaluate
        loss, accuracy = hybrid_model.evaluate([X_test_pad, X_test_features], y_test, verbose=0)
        print(f"\nHybrid Model Results:")
        print(f"Test Accuracy: {accuracy:.4f}")
        
        self.models['hybrid_lstm'] = hybrid_model
        self.feature_columns = feature_cols
        
        return history, accuracy
    
    def train_transformer_model(self, train_texts, train_labels, val_texts, val_labels, model_name='distilbert-base-uncased'):
        """Train transformer model using Hugging Face"""
        
        # Initialize tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
        
        # Create datasets
        train_dataset = FakeNewsDataset(train_texts, train_labels, tokenizer)
        val_dataset = FakeNewsDataset(val_texts, val_labels, tokenizer)
        
        # Fixed Training arguments
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            eval_strategy="epoch",  # Changed from 'evaluation_strategy'
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        # Train model
        trainer.train()
        
        # Save model
        self.models['transformer'] = (model, tokenizer)
        
        return trainer
    
    def save_models(self, model_dir):
        """Save all trained models"""
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        # Save traditional models
        for name, model in self.models.items():
            if name in ['random_forest', 'logistic_regression', 'naive_bayes', 'gradient_boosting', 'xgboost']:
                joblib.dump(model, f"{model_dir}/{name}_model.pkl")
        
        # Save vectorizer
        joblib.dump(self.tfidf_vectorizer, f"{model_dir}/tfidf_vectorizer.pkl")
        
        # Save hybrid LSTM model
        if 'hybrid_lstm' in self.models:
            self.models['hybrid_lstm'].save(f"{model_dir}/hybrid_lstm_model.h5")
            
            # Save tokenizer
            with open(f"{model_dir}/keras_tokenizer.pkl", 'wb') as f:
                pickle.dump(self.tokenizer, f)
            
            # Save feature columns
            with open(f"{model_dir}/feature_columns.pkl", 'wb') as f:
                pickle.dump(self.feature_columns, f)
        
        # Save transformer model
        if 'transformer' in self.models:
            model, tokenizer = self.models['transformer']
            model.save_pretrained(f"{model_dir}/transformer_model")
            tokenizer.save_pretrained(f"{model_dir}/transformer_tokenizer")