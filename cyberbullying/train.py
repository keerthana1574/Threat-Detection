# Fixed train.py - Complete Working Version
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

# Import the preprocessor
from data_preprocessor import CyberbullyingPreprocessor

# Import all the required classes for the trainer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import pickle
import joblib
from sklearn.utils.class_weight import compute_class_weight
import time
import warnings
warnings.filterwarnings('ignore')

class FastCyberbullyingModelTrainer:
    def __init__(self, use_svm=False, max_features=8000):
        self.use_svm = use_svm
        self.max_features = max_features
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=3,
            max_df=0.9,
            sublinear_tf=True
        )
        self.tokenizer = Tokenizer(num_words=8000, oov_token="<OOV>")
        self.models = {}
        self.best_model = None
        self.best_accuracy = 0
        
    def train_traditional_models(self, X_train, X_test, y_train, y_test):
        print(f"Training with {self.max_features} max features...")
        start_time = time.time()
        
        # Vectorize text data
        print("Vectorizing text data...")
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test)
        
        print(f"TF-IDF shape: {X_train_tfidf.shape}")
        
        results = {}
        
        # Calculate class weights
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        print(f"Class weights: {class_weight_dict}")
        
        # 1. Naive Bayes (Very Fast)
        print("\n1. Training Multinomial Naive Bayes...")
        model_start = time.time()
        nb_model = MultinomialNB(alpha=1.0)
        nb_model.fit(X_train_tfidf, y_train)
        nb_pred = nb_model.predict(X_test_tfidf)
        nb_accuracy = accuracy_score(y_test, nb_pred)
        
        print(f"Naive Bayes completed in {time.time() - model_start:.2f} seconds")
        print(f"Naive Bayes Accuracy: {nb_accuracy:.4f}")
        
        self.models['naive_bayes'] = nb_model
        results['nb_accuracy'] = nb_accuracy
        
        if nb_accuracy > self.best_accuracy:
            self.best_accuracy = nb_accuracy
            self.best_model = ('naive_bayes', nb_model)
        
        # 2. SGD Logistic Regression (Fast)
        print("\n2. Training SGD Logistic Regression...")
        model_start = time.time()
        sgd_model = SGDClassifier(
            loss='log_loss',
            class_weight='balanced',
            random_state=42,
            max_iter=1000,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=5
        )
        sgd_model.fit(X_train_tfidf, y_train)
        sgd_pred = sgd_model.predict(X_test_tfidf)
        sgd_accuracy = accuracy_score(y_test, sgd_pred)
        
        print(f"SGD completed in {time.time() - model_start:.2f} seconds")
        print(f"SGD Accuracy: {sgd_accuracy:.4f}")
        
        self.models['sgd_logistic'] = sgd_model
        results['sgd_accuracy'] = sgd_accuracy
        
        if sgd_accuracy > self.best_accuracy:
            self.best_accuracy = sgd_accuracy
            self.best_model = ('sgd_logistic', sgd_model)
        
        # 3. Logistic Regression
        print("\n3. Training Logistic Regression...")
        model_start = time.time()
        lr_model = LogisticRegression(
            class_weight='balanced',
            random_state=42,
            max_iter=1000,
            solver='liblinear'
        )
        lr_model.fit(X_train_tfidf, y_train)
        lr_pred = lr_model.predict(X_test_tfidf)
        lr_accuracy = accuracy_score(y_test, lr_pred)
        
        print(f"Logistic Regression completed in {time.time() - model_start:.2f} seconds")
        print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
        
        self.models['logistic_regression'] = lr_model
        results['lr_accuracy'] = lr_accuracy
        
        if lr_accuracy > self.best_accuracy:
            self.best_accuracy = lr_accuracy
            self.best_model = ('logistic_regression', lr_model)
        
        # 4. Random Forest (Reduced Size)
        print("\n4. Training Random Forest...")
        model_start = time.time()
        rf_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=8,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_tfidf, y_train)
        rf_pred = rf_model.predict(X_test_tfidf)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        print(f"Random Forest completed in {time.time() - model_start:.2f} seconds")
        print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
        
        self.models['random_forest'] = rf_model
        results['rf_accuracy'] = rf_accuracy
        
        if rf_accuracy > self.best_accuracy:
            self.best_accuracy = rf_accuracy
            self.best_model = ('random_forest', rf_model)
        
        total_time = time.time() - start_time
        print(f"\nTotal training time: {total_time:.2f} seconds")
        
        return results
    
    def build_fast_lstm_model(self, vocab_size, embedding_dim=64, max_length=80):
        model = Sequential([
            Embedding(vocab_size, embedding_dim, input_length=max_length, mask_zero=True),
            Dropout(0.2),
            LSTM(32, dropout=0.3, recurrent_dropout=0.3),
            Dense(32, activation='relu'),
            Dropout(0.5),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.002),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_lstm_model(self, X_train, X_test, y_train, y_test, max_length=80, epochs=8):
        print("Training LSTM model...")
        start_time = time.time()
        
        # Prepare sequences
        self.tokenizer.fit_on_texts(X_train)
        
        X_train_seq = self.tokenizer.texts_to_sequences(X_train)
        X_test_seq = self.tokenizer.texts_to_sequences(X_test)
        
        X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
        X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')
        
        y_train_np = np.array(y_train, dtype=np.float32)
        y_test_np = np.array(y_test, dtype=np.float32)
        
        # Build model
        vocab_size = min(len(self.tokenizer.word_index) + 1, 8000)
        lstm_model = self.build_fast_lstm_model(vocab_size, max_length=max_length)
        
        # Class weights
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=0.0001)
        ]
        
        # Train
        history = lstm_model.fit(
            X_train_pad, y_train_np,
            batch_size=64,
            epochs=epochs,
            validation_data=(X_test_pad, y_test_np),
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        test_loss, test_accuracy = lstm_model.evaluate(X_test_pad, y_test_np, verbose=0)
        
        print(f"LSTM completed in {time.time() - start_time:.2f} seconds")
        print(f"LSTM Accuracy: {test_accuracy:.4f}")
        
        self.models['lstm'] = lstm_model
        
        if test_accuracy > self.best_accuracy:
            self.best_accuracy = test_accuracy
            self.best_model = ('lstm', lstm_model)
        
        return history, test_accuracy
    
    def save_models(self, model_dir):
        os.makedirs(model_dir, exist_ok=True)
        
        # Save vectorizer
        joblib.dump(self.tfidf_vectorizer, f"{model_dir}/tfidf_vectorizer.pkl")
        
        # Save traditional models
        for name in ['naive_bayes', 'sgd_logistic', 'logistic_regression', 'random_forest']:
            if name in self.models:
                joblib.dump(self.models[name], f"{model_dir}/{name}_model.pkl")
                print(f"Saved {name} model")
        
        # Save LSTM model
        if 'lstm' in self.models:
            self.models['lstm'].save(f"{model_dir}/lstm_model.keras")
            print(f"Saved LSTM model")
        
        # Save tokenizer
        with open(f"{model_dir}/tokenizer.pkl", 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        # Save best model info
        with open(f"{model_dir}/best_model_info.pkl", 'wb') as f:
            pickle.dump({
                'best_model': self.best_model[0] if self.best_model else None,
                'best_accuracy': self.best_accuracy,
                'available_models': list(self.models.keys())
            }, f)
        
        print(f"All models saved to {model_dir}")
        if self.best_model:
            print(f"Best model: {self.best_model[0]} with accuracy: {self.best_accuracy:.4f}")

def create_sample_data():
    """Create sample data for testing"""
    # Cyberbullying examples
    cyberbullying_samples = [
        "you are so stupid and ugly", "nobody likes you go away", "you should disappear forever",
        "what a loser you're pathetic", "shut up you idiot", "you're the worst person ever",
        "everyone hates you", "you're a waste of space", "you don't belong here", "kill yourself"
    ] * 20  # 200 samples
    
    # Normal examples  
    normal_samples = [
        "what a beautiful day today", "I love spending time with friends", "this movie is interesting",
        "thank you for your help", "have a great weekend", "looking forward to meeting",
        "nice job on presentation", "hope you feel better", "congratulations on achievement",
        "excited about new project", "great work everyone", "thanks for sharing"
    ] * 20  # 240 samples
    
    # Create DataFrame
    data = []
    for text in cyberbullying_samples:
        data.append({'text': text, 'label': 1})
    for text in normal_samples:
        data.append({'text': text, 'label': 0})
    
    df = pd.DataFrame(data)
    
    # Clean text
    preprocessor = CyberbullyingPreprocessor()
    df['cleaned_text'] = df['text'].apply(preprocessor.clean_text)
    
    return df

def main():
    print("AI-Based Cyberbullying Detection - FAST Training")
    print("=" * 60)
    
    # Initialize
    preprocessor = CyberbullyingPreprocessor()
    trainer = FastCyberbullyingModelTrainer(use_svm=False, max_features=8000)
    
    # Dataset files
    dataset_files = [
        'datasets/cyberbullying/cyberbullying_tweets.csv',
        'datasets/cyberbullying/final_hateXplain.csv'
    ]
    
    # Check for existing files
    existing_files = [f for f in dataset_files if os.path.exists(f)]
    
    if not existing_files:
        print("No dataset files found. Creating sample data...")
        df = create_sample_data()
    else:
        print(f"Found {len(existing_files)} dataset file(s)")
        try:
            df = preprocessor.load_and_preprocess_data(existing_files)
        except Exception as e:
            print(f"Error loading datasets: {e}")
            print("Using sample data instead...")
            df = create_sample_data()
    
    print(f"Dataset size: {len(df)} samples")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'], df['label'], 
        test_size=0.2, random_state=42, stratify=df['label']
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train traditional models
    print("\n" + "="*50)
    print("TRAINING TRADITIONAL MODELS")
    print("="*50)
    
    traditional_results = trainer.train_traditional_models(X_train, X_test, y_train, y_test)
    
    # Train LSTM if we have enough data
    if len(df) >= 500:
        print("\n" + "="*50)
        print("TRAINING LSTM MODEL")
        print("="*50)
        
        try:
            lstm_history, lstm_accuracy = trainer.train_lstm_model(
                X_train, X_test, y_train, y_test, max_length=80, epochs=8
            )
        except Exception as e:
            print(f"LSTM training failed: {e}")
    else:
        print("Skipping LSTM (dataset too small)")
    
    # Save models
    model_dir = 'backend/models/cyberbullying'
    trainer.save_models(model_dir)
    preprocessor.save_preprocessor(f"{model_dir}/preprocessor.pkl")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    print(f"Best model: {trainer.best_model[0] if trainer.best_model else 'None'}")
    print(f"Best accuracy: {trainer.best_accuracy:.4f}")
    print(f"Models saved to: {model_dir}")

if __name__ == "__main__":
    main()