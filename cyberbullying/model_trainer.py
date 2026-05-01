# Optimized model_trainer.py - Fast Training Version
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import pickle
import joblib
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight
import time
import warnings
warnings.filterwarnings('ignore')

class FastCyberbullyingModelTrainer:
    def __init__(self, use_svm=False, max_features=10000):
        """
        Initialize trainer with option to skip SVM
        
        Args:
            use_svm (bool): Whether to include SVM (very slow, set False for speed)
            max_features (int): Maximum features for TF-IDF (reduce for speed)
        """
        self.use_svm = use_svm
        self.max_features = max_features
        
        # Reduced TF-IDF parameters for speed
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,  # Reduced from 15000
            ngram_range=(1, 2),  # Reduced from (1,3) 
            min_df=3,  # Increased from 2
            max_df=0.9,  # Reduced from 0.95
            sublinear_tf=True
        )
        self.tokenizer = Tokenizer(num_words=8000, oov_token="<OOV>")  # Reduced from 10000
        self.models = {}
        self.best_model = None
        self.best_accuracy = 0
        
    def train_traditional_models(self, X_train, X_test, y_train, y_test):
        """Train traditional ML models with optimized parameters for speed"""
        
        print(f"Training with {self.max_features} max features...")
        start_time = time.time()
        
        # Vectorize text data
        print("Vectorizing text data...")
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test)
        
        print(f"TF-IDF shape: {X_train_tfidf.shape}")
        vectorize_time = time.time() - start_time
        print(f"Vectorization completed in {vectorize_time:.2f} seconds")
        
        results = {}
        
        # Calculate class weights for imbalanced data
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        print(f"Class weights: {class_weight_dict}")
        
        # 1. Multinomial Naive Bayes (Very Fast)
        print("\n1. Training Multinomial Naive Bayes (Fast)...")
        model_start = time.time()
        nb_model = MultinomialNB(alpha=1.0)
        nb_model.fit(X_train_tfidf, y_train)
        nb_pred = nb_model.predict(X_test_tfidf)
        nb_accuracy = accuracy_score(y_test, nb_pred)
        
        print(f"Naive Bayes completed in {time.time() - model_start:.2f} seconds")
        print(f"Naive Bayes Accuracy: {nb_accuracy:.4f}")
        print(classification_report(y_test, nb_pred))
        
        self.models['naive_bayes'] = nb_model
        results['nb_accuracy'] = nb_accuracy
        
        if nb_accuracy > self.best_accuracy:
            self.best_accuracy = nb_accuracy
            self.best_model = ('naive_bayes', nb_model)
        
        # 2. Logistic Regression with SGD (Fast)
        print("\n2. Training SGD Logistic Regression (Fast)...")
        model_start = time.time()
        sgd_model = SGDClassifier(
            loss='log_loss',  # Logistic regression
            class_weight='balanced',
            random_state=42,
            max_iter=1000,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=5,
            learning_rate='adaptive',
            eta0=0.01
        )
        sgd_model.fit(X_train_tfidf, y_train)
        sgd_pred = sgd_model.predict(X_test_tfidf)
        sgd_accuracy = accuracy_score(y_test, sgd_pred)
        
        print(f"SGD Logistic Regression completed in {time.time() - model_start:.2f} seconds")
        print(f"SGD Accuracy: {sgd_accuracy:.4f}")
        print(classification_report(y_test, sgd_pred))
        
        self.models['sgd_logistic'] = sgd_model
        results['sgd_accuracy'] = sgd_accuracy
        
        if sgd_accuracy > self.best_accuracy:
            self.best_accuracy = sgd_accuracy
            self.best_model = ('sgd_logistic', sgd_model)
        
        # 3. Regular Logistic Regression (Medium Speed)
        print("\n3. Training Logistic Regression...")
        model_start = time.time()
        lr_model = LogisticRegression(
            class_weight='balanced',
            random_state=42, 
            max_iter=1000,
            C=1.0,
            solver='liblinear'  # Faster for small datasets
        )
        lr_model.fit(X_train_tfidf, y_train)
        lr_pred = lr_model.predict(X_test_tfidf)
        lr_accuracy = accuracy_score(y_test, lr_pred)
        
        print(f"Logistic Regression completed in {time.time() - model_start:.2f} seconds")
        print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
        print(classification_report(y_test, lr_pred))
        
        self.models['logistic_regression'] = lr_model
        results['lr_accuracy'] = lr_accuracy
        
        if lr_accuracy > self.best_accuracy:
            self.best_accuracy = lr_accuracy
            self.best_model = ('logistic_regression', lr_model)
        
        # 4. Random Forest (Medium Speed) - Reduced parameters
        print("\n4. Training Random Forest (Reduced Size)...")
        model_start = time.time()
        rf_model = RandomForestClassifier(
            n_estimators=50,  # Reduced from 200
            max_depth=8,      # Reduced from 10
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_tfidf, y_train)
        rf_pred = rf_model.predict(X_test_tfidf)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        print(f"Random Forest completed in {time.time() - model_start:.2f} seconds")
        print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
        print(classification_report(y_test, rf_pred))
        
        self.models['random_forest'] = rf_model
        results['rf_accuracy'] = rf_accuracy
        
        if rf_accuracy > self.best_accuracy:
            self.best_accuracy = rf_accuracy
            self.best_model = ('random_forest', rf_model)
        
        # 5. SVM (Optional - Very Slow)
        if self.use_svm:
            print("\n5. Training SVM (This will be slow!)...")
            print("Tip: Set use_svm=False to skip this step")
            model_start = time.time()
            
            from sklearn.svm import SVC
            
            # Use LinearSVC instead of RBF SVM for speed
            from sklearn.svm import LinearSVC
            svm_model = LinearSVC(
                class_weight='balanced',
                random_state=42,
                max_iter=2000,
                dual=False  # Faster for large datasets
            )
            svm_model.fit(X_train_tfidf, y_train)
            svm_pred = svm_model.predict(X_test_tfidf)
            svm_accuracy = accuracy_score(y_test, svm_pred)
            
            print(f"SVM completed in {time.time() - model_start:.2f} seconds")
            print(f"SVM Accuracy: {svm_accuracy:.4f}")
            print(classification_report(y_test, svm_pred))
            
            self.models['svm'] = svm_model
            results['svm_accuracy'] = svm_accuracy
            
            if svm_accuracy > self.best_accuracy:
                self.best_accuracy = svm_accuracy
                self.best_model = ('svm', svm_model)
        else:
            print("\n5. Skipping SVM (use_svm=False for faster training)")
        
        total_time = time.time() - start_time
        print(f"\nTotal traditional models training time: {total_time:.2f} seconds")
        
        return results
    
    def build_fast_lstm_model(self, vocab_size, embedding_dim=64, max_length=100):
        """Build a faster, smaller LSTM model"""
        model = Sequential([
            # Smaller embedding layer
            Embedding(
                input_dim=vocab_size, 
                output_dim=embedding_dim,  # Reduced from 128
                input_length=max_length,
                mask_zero=True
            ),
            
            Dropout(0.2),
            
            # Single LSTM layer instead of bidirectional
            LSTM(32, dropout=0.3, recurrent_dropout=0.3),  # Reduced from 64
            
            # Smaller dense layers
            Dense(32, activation='relu'),  # Reduced from 64
            Dropout(0.5),
            
            # Output layer
            Dense(1, activation='sigmoid')
        ])
        
        # Compile with higher learning rate for faster training
        model.compile(
            optimizer=Adam(learning_rate=0.002),  # Increased from 0.001
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_lstm_model(self, X_train, X_test, y_train, y_test, max_length=80, epochs=10):
        """Train LSTM model with faster configuration"""
        
        print("Preparing text data for LSTM...")
        start_time = time.time()
        
        # Reduced max_length and vocabulary for speed
        self.tokenizer.fit_on_texts(X_train)
        
        X_train_seq = self.tokenizer.texts_to_sequences(X_train)
        X_test_seq = self.tokenizer.texts_to_sequences(X_test)
        
        X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post', truncating='post')
        X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post', truncating='post')
        
        y_train_np = np.array(y_train, dtype=np.float32)
        y_test_np = np.array(y_test, dtype=np.float32)
        
        print(f"Sequence shapes: Train {X_train_pad.shape}, Test {X_test_pad.shape}")
        
        # Build smaller model
        vocab_size = min(len(self.tokenizer.word_index) + 1, 8000)  # Reduced
        print(f"Vocabulary size: {vocab_size}")
        
        lstm_model = self.build_fast_lstm_model(vocab_size, max_length=max_length)
        print("Model built successfully")
        
        # Calculate class weights
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        
        # Faster training callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=3,  # Reduced from 5
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,  # More aggressive reduction
                patience=2,  # Reduced from 3
                min_lr=0.0001,
                verbose=1
            )
        ]
        
        print(f"Starting LSTM training (max {epochs} epochs)...")
        
        # Train model with larger batch size for speed
        history = lstm_model.fit(
            X_train_pad, y_train_np,
            batch_size=64,  # Increased from 32
            epochs=epochs,  # Reduced default epochs
            validation_data=(X_test_pad, y_test_np),
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_accuracy = lstm_model.evaluate(X_test_pad, y_test_np, verbose=0)
        
        training_time = time.time() - start_time
        print(f"\nLSTM Training completed in {training_time:.2f} seconds")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Store model
        self.models['lstm'] = lstm_model
        
        if test_accuracy > self.best_accuracy:
            self.best_accuracy = test_accuracy
            self.best_model = ('lstm', lstm_model)
        
        return history, test_accuracy
    
    def get_training_recommendations(self, dataset_size):
        """Get recommendations based on dataset size"""
        print(f"\n🚀 TRAINING RECOMMENDATIONS FOR {dataset_size} SAMPLES:")
        print("="*50)
        
        if dataset_size < 5000:
            print("📊 Small dataset - Use fast models:")
            print("  ✅ Naive Bayes (very fast)")
            print("  ✅ SGD Logistic Regression (fast)")
            print("  ✅ Regular Logistic Regression")
            print("  ⚠️  Skip Random Forest (may overfit)")
            print("  ❌ Skip SVM (too slow)")
            print("  ❌ Skip LSTM (may overfit)")
            return {'use_svm': False, 'use_lstm': False, 'use_rf': False}
            
        elif dataset_size < 20000:
            print("📊 Medium dataset - Use balanced approach:")
            print("  ✅ All fast models")
            print("  ✅ Random Forest (reduced size)")
            print("  ⚠️  LSTM with early stopping")
            print("  ❌ Skip SVM (still too slow)")
            return {'use_svm': False, 'use_lstm': True, 'use_rf': True}
            
        else:
            print("📊 Large dataset - Can use most models:")
            print("  ✅ All models available")
            print("  ⚠️  SVM will be very slow - consider skipping")
            print("  ✅ LSTM should work well")
            return {'use_svm': False, 'use_lstm': True, 'use_rf': True}  # Still skip SVM
    
    def save_models(self, model_dir):
        """Save all trained models"""
        import os
        os.makedirs(model_dir, exist_ok=True)

        # Save vectorizer
        joblib.dump(self.tfidf_vectorizer, f"{model_dir}/tfidf_vectorizer.pkl")
        print(f"Saved TF-IDF vectorizer")
        
        # Save traditional models
        for name in ['naive_bayes', 'sgd_logistic', 'logistic_regression', 'random_forest', 'svm']:
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
        
        print(f"\n✅ All models saved to {model_dir}")
        if self.best_model:
            print(f"🏆 Best model: {self.best_model[0]} with accuracy: {self.best_accuracy:.4f}")

# Updated train.py for fast training
def main():
    print("🚀 AI-Based Cyberbullying Detection - FAST Training")
    print("=" * 60)
    
    from data_preprocessor import CyberbullyingPreprocessor
    from sklearn.model_selection import train_test_split
    import os
    import numpy as np
    
    # Dataset files
    dataset_files = [
        'datasets/cyberbullying/cyberbullying_tweets.csv',
        'datasets/cyberbullying/final_hateXplain.csv'
    ]
    
    # Check files
    existing_files = [f for f in dataset_files if os.path.exists(f)]
    if not existing_files:
        print("❌ No dataset files found!")
        return
    
    print(f"📁 Found {len(existing_files)} dataset file(s)")
    
    # Load data
    preprocessor = CyberbullyingPreprocessor()
    df = preprocessor.load_and_preprocess_data(existing_files)
    
    print(f"\n📊 Dataset size: {len(df)} samples")
    
    # Initialize fast trainer
    trainer = FastCyberbullyingModelTrainer(
        use_svm=False,  # Skip SVM for speed
        max_features=8000  # Reduced for speed
    )
    
    # Get training recommendations
    recommendations = trainer.get_training_recommendations(len(df))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'], df['label'], 
        test_size=0.2, random_state=42, stratify=df['label']
    )
    
    print(f"\n🎯 Training set: {len(X_train)} samples")
    print(f"🎯 Test set: {len(X_test)} samples")
    
    # Train traditional models
    print("\n" + "="*50)
    print("🤖 TRAINING TRADITIONAL MODELS")
    print("="*50)
    
    traditional_results = trainer.train_traditional_models(X_train, X_test, y_train, y_test)
    
    # Train LSTM if recommended
    if recommendations.get('use_lstm', True) and len(df) >= 1000:
        print("\n" + "="*50)
        print("🧠 TRAINING LSTM MODEL")
        print("="*50)
        
        lstm_history, lstm_accuracy = trainer.train_lstm_model(
            X_train, X_test, y_train, y_test,
            max_length=80,  # Reduced for speed
            epochs=8       # Reduced for speed
        )
    else:
        print("\n⏭️ Skipping LSTM (not recommended for this dataset size)")
    
    # Save models
    model_dir = 'backend/models/cyberbullying'
    os.makedirs(model_dir, exist_ok=True)
    trainer.save_models(model_dir)
    preprocessor.save_preprocessor(f"{model_dir}/preprocessor.pkl")
    
    print("\n" + "="*60)
    print("✅ FAST TRAINING COMPLETED!")
    print("="*60)
    print(f"🏆 Best model: {trainer.best_model[0] if trainer.best_model else 'None'}")
    print(f"📈 Best accuracy: {trainer.best_accuracy:.4f}")
    print(f"💾 Models saved to: {model_dir}")


if __name__ == "__main__":
    main()
    