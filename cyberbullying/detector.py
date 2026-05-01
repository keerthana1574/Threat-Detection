# Fixed detector.py with improved prediction and debugging
import numpy as np
import joblib
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tweepy
import re
from datetime import datetime
import os

class CyberbullyingDetector:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.models = {}
        self.load_models()
        
    def load_models(self):
        """Load all trained models with flexible loading"""
        try:
            print(f"Loading models from {self.model_dir}...")
            
            # Load TF-IDF vectorizer (required)
            vectorizer_path = f"{self.model_dir}/tfidf_vectorizer.pkl"
            if os.path.exists(vectorizer_path):
                self.tfidf_vectorizer = joblib.load(vectorizer_path)
                print("✅ Loaded TF-IDF vectorizer")
            else:
                print(f"❌ Error: TF-IDF vectorizer not found at {vectorizer_path}")
                return
            
            # Load traditional models (with new naming convention)
            model_files = {
                'naive_bayes': 'naive_bayes_model.pkl',
                'sgd_logistic': 'sgd_logistic_model.pkl', 
                'logistic_regression': 'logistic_regression_model.pkl',
                'random_forest': 'random_forest_model.pkl',
                'svm': 'svm_model.pkl',
                # Legacy names for backward compatibility
                'rf': 'rf_model.pkl',
                'lr': 'lr_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = f"{self.model_dir}/{filename}"
                if os.path.exists(model_path):
                    try:
                        self.models[model_name] = joblib.load(model_path)
                        print(f"✅ Loaded {model_name} model")
                    except Exception as e:
                        print(f"⚠️  Error loading {model_name}: {e}")
            
            # Load LSTM model if available
            lstm_paths = [
                f"{self.model_dir}/lstm_model.keras",
                f"{self.model_dir}/lstm_model.h5"
            ]
            
            self.lstm_model = None
            for lstm_path in lstm_paths:
                if os.path.exists(lstm_path):
                    try:
                        self.lstm_model = tf.keras.models.load_model(lstm_path)
                        print("✅ Loaded LSTM model")
                        
                        # Load tokenizer
                        tokenizer_path = f"{self.model_dir}/tokenizer.pkl"
                        if os.path.exists(tokenizer_path):
                            with open(tokenizer_path, 'rb') as f:
                                self.tokenizer = pickle.load(f)
                            print("✅ Loaded tokenizer")
                        break
                    except Exception as e:
                        print(f"⚠️  Error loading LSTM model from {lstm_path}: {e}")
            
            if self.lstm_model is None:
                print("ℹ️  No LSTM model found")
            
            # Load best model info
            best_model_path = f"{self.model_dir}/best_model_info.pkl"
            if os.path.exists(best_model_path):
                with open(best_model_path, 'rb') as f:
                    self.best_model_info = pickle.load(f)
                print(f"ℹ️  Best model: {self.best_model_info.get('best_model', 'Unknown')}")
            
            print(f"\n📊 Total models loaded: {len(self.models)}")
            print(f"📋 Available models: {list(self.models.keys())}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            import traceback
            traceback.print_exc()
    
    def preprocess_text(self, text):
        """Preprocess text - MUST match training preprocessing"""
        if not text:
            return ""
        
        text = str(text).lower()
        
        # Same preprocessing as training
        text = re.sub(r'http\S+|www\S+|https\S+', ' url ', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', ' user ', text)
        text = re.sub(r'#(\w+)', r' \1 ', text)
        
        # DON'T reduce repeated characters (matching training)
        # Keep special characters (matching training)
        text = re.sub(r'[^a-zA-Z0-9\s!?.,\-_*@#$%&]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def predict_single(self, text, debug=False):
        """Predict cyberbullying for a single text"""
        if not hasattr(self, 'tfidf_vectorizer'):
            return {
                'error': 'Models not loaded properly',
                'text': text,
                'is_cyberbullying': False,
                'confidence': 0.0
            }
        
        cleaned_text = self.preprocess_text(text)
        
        if debug:
            print(f"\n{'='*60}")
            print("DEBUG MODE")
            print(f"Original text: {text}")
            print(f"Cleaned text:  {cleaned_text}")
        
        # Transform text
        text_tfidf = self.tfidf_vectorizer.transform([cleaned_text])
        
        if debug:
            print(f"TF-IDF shape: {text_tfidf.shape}")
            print(f"TF-IDF non-zero: {text_tfidf.nnz}")
            if text_tfidf.nnz > 0:
                print(f"TF-IDF features detected: {text_tfidf.nnz} features")
            else:
                print("⚠️  WARNING: No TF-IDF features detected!")
        
        predictions = {}
        probabilities = []
        
        # Traditional model predictions
        if 'naive_bayes' in self.models:
            try:
                nb_pred = self.models['naive_bayes'].predict_proba(text_tfidf)[0]
                predictions['naive_bayes'] = {
                    'probability': float(nb_pred[1]),
                    'prediction': nb_pred[1] > 0.5
                }
                probabilities.append(nb_pred[1])
                if debug:
                    print(f"Naive Bayes: {nb_pred[1]:.4f} (cyberbullying: {nb_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"Naive Bayes ERROR: {e}")
        
        if 'sgd_logistic' in self.models:
            try:
                sgd_pred = self.models['sgd_logistic'].predict_proba(text_tfidf)[0]
                predictions['sgd_logistic'] = {
                    'probability': float(sgd_pred[1]),
                    'prediction': sgd_pred[1] > 0.5
                }
                probabilities.append(sgd_pred[1])
                if debug:
                    print(f"SGD Logistic: {sgd_pred[1]:.4f} (cyberbullying: {sgd_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"SGD Logistic ERROR: {e}")
        
        if 'logistic_regression' in self.models:
            try:
                lr_pred = self.models['logistic_regression'].predict_proba(text_tfidf)[0]
                predictions['logistic_regression'] = {
                    'probability': float(lr_pred[1]),
                    'prediction': lr_pred[1] > 0.5
                }
                probabilities.append(lr_pred[1])
                if debug:
                    print(f"Logistic Regression: {lr_pred[1]:.4f} (cyberbullying: {lr_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"Logistic Regression ERROR: {e}")
        
        if 'random_forest' in self.models:
            try:
                rf_pred = self.models['random_forest'].predict_proba(text_tfidf)[0]
                predictions['random_forest'] = {
                    'probability': float(rf_pred[1]),
                    'prediction': rf_pred[1] > 0.5
                }
                probabilities.append(rf_pred[1])
                if debug:
                    print(f"Random Forest: {rf_pred[1]:.4f} (cyberbullying: {rf_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"Random Forest ERROR: {e}")
        
        # Legacy model support
        if 'rf' in self.models and 'random_forest' not in self.models:
            try:
                rf_pred = self.models['rf'].predict_proba(text_tfidf)[0]
                predictions['rf'] = {
                    'probability': float(rf_pred[1]),
                    'prediction': rf_pred[1] > 0.5
                }
                probabilities.append(rf_pred[1])
                if debug:
                    print(f"RF (legacy): {rf_pred[1]:.4f} (cyberbullying: {rf_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"RF (legacy) ERROR: {e}")
        
        if 'lr' in self.models and 'logistic_regression' not in self.models:
            try:
                lr_pred = self.models['lr'].predict_proba(text_tfidf)[0]
                predictions['lr'] = {
                    'probability': float(lr_pred[1]),
                    'prediction': lr_pred[1] > 0.5
                }
                probabilities.append(lr_pred[1])
                if debug:
                    print(f"LR (legacy): {lr_pred[1]:.4f} (cyberbullying: {lr_pred[1] > 0.5})")
            except Exception as e:
                if debug:
                    print(f"LR (legacy) ERROR: {e}")
        
        # LSTM prediction if available
        if self.lstm_model and hasattr(self, 'tokenizer'):
            try:
                text_seq = self.tokenizer.texts_to_sequences([cleaned_text])
                text_pad = pad_sequences(text_seq, maxlen=80, padding='post', truncating='post')
                lstm_pred = self.lstm_model.predict(text_pad, verbose=0)[0][0]
                predictions['lstm'] = {
                    'probability': float(lstm_pred),
                    'prediction': lstm_pred > 0.5
                }
                probabilities.append(lstm_pred)
                if debug:
                    print(f"LSTM: {lstm_pred:.4f} (cyberbullying: {lstm_pred > 0.5})")
            except Exception as e:
                if debug:
                    print(f"LSTM ERROR: {e}")
        
        # Ensemble prediction
        if probabilities:
            ensemble_prob = np.mean(probabilities)
        else:
            ensemble_prob = 0.0
            if debug:
                print("⚠️  WARNING: No model predictions available!")
        
        if debug:
            print(f"\n🎯 ENSEMBLE RESULT: {ensemble_prob:.4f}")
            print(f"🔍 FINAL PREDICTION: {'CYBERBULLYING' if ensemble_prob > 0.5 else 'NOT CYBERBULLYING'}")
            print(f"{'='*60}\n")
        
        # Final result
        result = {
            'text': text,
            'cleaned_text': cleaned_text,
            'individual_predictions': predictions,
            'ensemble_probability': float(ensemble_prob),
            'is_cyberbullying': ensemble_prob > 0.5,
            'confidence': abs(ensemble_prob - 0.5) * 2,  # Normalized confidence
            'models_used': list(predictions.keys()),
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def predict_batch(self, texts, debug=False):
        """Predict cyberbullying for multiple texts"""
        return [self.predict_single(text, debug=debug) for text in texts]
    
    def test_with_dataset_samples(self, df, n_samples=10):
        """Test detector with actual training data samples"""
        print(f"\n{'='*60}")
        print(f"TESTING WITH {n_samples} DATASET SAMPLES")
        print(f"{'='*60}\n")
        
        # Get samples from both classes
        if 'label' in df.columns:
            cyberbullying_samples = df[df['label'] == 1].sample(min(n_samples//2, len(df[df['label'] == 1])))
            normal_samples = df[df['label'] == 0].sample(min(n_samples//2, len(df[df['label'] == 0])))
            test_samples = pd.concat([cyberbullying_samples, normal_samples])
        else:
            test_samples = df.sample(min(n_samples, len(df)))
        
        correct = 0
        total = 0
        
        for idx, row in test_samples.iterrows():
            text = row['original_text'] if 'original_text' in row else row['text']
            true_label = row['label'] if 'label' in row else None
            
            result = self.predict_single(text, debug=False)
            predicted = 1 if result['is_cyberbullying'] else 0
            
            if true_label is not None:
                is_correct = (predicted == true_label)
                correct += is_correct
                total += 1
                status = "✅" if is_correct else "❌"
            else:
                status = "?"
            
            print(f"{status} Text: {text[:80]}")
            print(f"   True: {true_label}, Predicted: {predicted} (prob: {result['ensemble_probability']:.3f})")
            print()
        
        if total > 0:
            accuracy = correct / total
            print(f"{'='*60}")
            print(f"Accuracy on dataset samples: {accuracy:.2%} ({correct}/{total})")
            print(f"{'='*60}\n")

class TwitterMonitor:
    def __init__(self, api_credentials, detector):
        self.detector = detector
        self.setup_twitter_api(api_credentials)
        
    def setup_twitter_api(self, credentials):
        """Setup Twitter API connection"""
        auth = tweepy.OAuthHandler(
            credentials['api_key'], 
            credentials['api_secret']
        )
        auth.set_access_token(
            credentials['access_token'], 
            credentials['access_secret']
        )
        
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        
    def monitor_tweets(self, keywords, count=100):
        """Monitor tweets for cyberbullying"""
        results = []
        
        try:
            tweets = tweepy.Cursor(
                self.api.search_tweets,
                q=' OR '.join(keywords),
                lang='en',
                result_type='recent'
            ).items(count)
            
            for tweet in tweets:
                prediction = self.detector.predict_single(tweet.text)
                prediction['tweet_id'] = tweet.id
                prediction['user'] = tweet.user.screen_name
                prediction['created_at'] = tweet.created_at.isoformat()
                results.append(prediction)
                
        except Exception as e:
            print(f"Error monitoring tweets: {e}")
            
        return results


# Test function
def test_detector():
    """Test the detector with various inputs"""
    import pandas as pd
    
    model_dir = '../../models/cyberbullying'
    
    print("\n" + "="*60)
    print("CYBERBULLYING DETECTOR TEST")
    print("="*60)
    
    detector = CyberbullyingDetector(model_dir)
    
    if not detector.models:
        print("❌ No models loaded! Cannot test.")
        return
    
    # Test with various texts
    test_texts = [
        # Clear cyberbullying
        "You are so stupid and worthless!",
        "I hate you so much, go die",
        "Nobody likes you, loser",
        "You're ugly and fat, kill yourself",
        "Everyone thinks you're a freak",
        
        # Borderline/context-dependent
        "You suck at this game lol",
        "That was dumb",
        "ur weird",
        
        # Normal/positive
        "Have a great day everyone!",
        "Thanks for helping me with homework",
        "You did a good job!",
        "I love this!",
        "That's awesome!"
    ]
    
    print("\n" + "="*60)
    print("TESTING WITH SAMPLE TEXTS")
    print("="*60)
    
    for text in test_texts:
        print(f"\n📝 Text: {text}")
        result = detector.predict_single(text, debug=False)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            status = "🚨 CYBERBULLYING" if result['is_cyberbullying'] else "✅ SAFE"
            print(f"   {status}")
            print(f"   Probability: {result['ensemble_probability']:.3f}")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Models used: {', '.join(result['models_used'])}")
    
    # Test with debug mode
    print("\n" + "="*60)
    print("DETAILED DEBUG TEST")
    print("="*60)
    
    debug_text = "You are so stupid and nobody likes you"
    print(f"\nTesting: '{debug_text}'")
    result = detector.predict_single(debug_text, debug=True)
    
    # Try to load and test with actual dataset if available
    try:
        print("\n" + "="*60)
        print("TESTING WITH ACTUAL DATASET SAMPLES")
        print("="*60)
        
        dataset_path = '../../datasets/cyberbullying/cyberbullying_tweets.csv'
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            detector.test_with_dataset_samples(df, n_samples=10)
        else:
            print("Dataset not found, skipping dataset test")
    except Exception as e:
        print(f"Could not test with dataset: {e}")


if __name__ == "__main__":
    test_detector()