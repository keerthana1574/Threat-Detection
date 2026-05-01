# Fixed data_preprocessor.py - Preserves cyberbullying indicators
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from collections import Counter
import pickle

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class CyberbullyingPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.label_encoder = LabelEncoder()
        
    def clean_text(self, text):
        """Improved text cleaning that preserves cyberbullying indicators"""
        if pd.isna(text) or text == "":
            return ""
        
        # Convert to string and lowercase
        text = str(text).lower()
        
        # Handle URLs and mentions but keep context
        text = re.sub(r'http\S+|www\S+|https\S+', ' url ', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', ' user ', text)
        text = re.sub(r'#(\w+)', r' \1 ', text)  # Keep hashtag content
        
        # DON'T reduce repeated characters - they're important for cyberbullying detection
        # Cyberbullies often use "sooooo", "hahahaha", etc.
        
        # Keep most special characters - they can indicate tone/aggression
        # Only remove clearly non-text characters
        text = re.sub(r'[^a-zA-Z0-9\s!?.,\-_*@#$%&]', ' ', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Minimal tokenization - keep most words
        tokens = word_tokenize(text)
        
        # Comprehensive list of cyberbullying-related terms to ALWAYS keep
        important_words = {
            # Negations
            'no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere', "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't", "shouldn't",
            
            # Aggressive/negative words
            'hate', 'hates', 'hated', 'hating', 'die', 'dies', 'died', 'dying', 'death',
            'kill', 'kills', 'killed', 'killing', 'murder',
            'ugly', 'uglier', 'ugliest', 'fat', 'fatter', 'fattest', 
            'stupid', 'dumb', 'idiot', 'idiotic', 'moron', 'moronic',
            'loser', 'losers', 'worthless', 'useless', 'pathetic',
            'disgusting', 'gross', 'nasty', 'horrible', 'terrible',
            'freak', 'freaks', 'weirdo', 'weird', 'creep', 'creepy',
            'lame', 'suck', 'sucks', 'sucked', 'sucking',
            
            # Profanity (commonly used in cyberbullying)
            'damn', 'damned', 'hell', 'shit', 'shitty', 'crap', 'crappy',
            'fuck', 'fucking', 'fucked', 'fucker',
            'bitch', 'bitches', 'bitchy', 'bastard',
            'ass', 'asshole', 'dick', 'dickhead', 'prick',
            
            # Discriminatory terms
            'gay', 'fag', 'faggot', 'retard', 'retarded', 'negro',
            
            # Threatening words
            'threat', 'threaten', 'threatened', 'threatening',
            'hurt', 'hurts', 'hurting', 'harm', 'harming',
            'attack', 'attacking', 'attacked',
            
            # Common cyberbullying phrases components
            'shut', 'nobody', 'everybody', 'everyone', 'alone', 'lonely',
            'failure', 'fail', 'fails', 'failed', 'failing',
            'joke', 'laugh', 'laughing', 'mock', 'mocking',
            'deserve', 'deserves', 'deserved',
            'wish', 'wishes', 'wished', 'hoping', 'hope'
        }
        
        # Very minimal stopwords - only the most common ones
        minimal_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 
            'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours',
            'it', 'its', 'they', 'them', 'their', 'theirs'
        }
        
        processed_tokens = []
        for token in tokens:
            # Keep almost everything - only filter very short or very common stopwords
            if len(token) > 1:
                # Always keep important cyberbullying words
                if token in important_words:
                    processed_tokens.append(token)
                # Keep words not in minimal stopwords
                elif token not in minimal_stopwords:
                    processed_tokens.append(token)
                # Even keep some stopwords if they might provide context
                elif len(processed_tokens) < 5:  # Keep context words for short texts
                    processed_tokens.append(token)
        
        result = ' '.join(processed_tokens)
        
        # Only return original if result is completely empty
        return result if len(result) > 0 else text.strip()
    
    def load_and_preprocess_data(self, file_paths):
        """Load and preprocess cyberbullying datasets"""
        dfs = []
        
        for file_path in file_paths:
            try:
                print(f"\n{'='*60}")
                print(f"Loading {file_path}...")
                df = pd.read_csv(file_path, encoding='utf-8')
                
                print(f"Original shape: {df.shape}")
                print(f"Columns: {df.columns.tolist()}")
                print("\nFirst few rows:")
                print(df.head(2))
                
                # Initialize text and label columns
                text_col = None
                label_col = None
                
                # Find text column - check multiple possible names
                text_candidates = ['text', 'tweet_text', 'tweet', 'comment', 'message', 'content', 'post']
                for col in df.columns:
                    if col.lower() in text_candidates or any(cand in col.lower() for cand in text_candidates):
                        text_col = col
                        print(f"Found text column: {text_col}")
                        break
                
                # Find label column
                label_candidates = ['label', 'class', 'type', 'cyberbullying_type', 'cyberbullying', 'category']
                for col in df.columns:
                    if col.lower() in label_candidates or any(cand in col.lower() for cand in label_candidates):
                        label_col = col
                        print(f"Found label column: {label_col}")
                        break
                
                if text_col is None or label_col is None:
                    print(f"⚠️  Could not identify text or label columns in {file_path}")
                    print("Available columns:", df.columns.tolist())
                    continue
                
                # Create clean dataframe
                df_clean = df[[text_col, label_col]].copy()
                df_clean.columns = ['text', 'label']
                
                # Remove NaN values
                print(f"Rows before removing NaN: {len(df_clean)}")
                df_clean = df_clean.dropna()
                print(f"Rows after removing NaN: {len(df_clean)}")
                
                # Show unique labels
                unique_labels = df_clean['label'].unique()
                print(f"Unique labels found: {unique_labels}")
                print(f"Label counts:\n{df_clean['label'].value_counts()}")
                
                # Convert labels to binary (0 = not cyberbullying, 1 = cyberbullying)
                if df_clean['label'].dtype == 'object':
                    # Check for "not_cyberbullying" label
                    if 'not_cyberbullying' in unique_labels:
                        df_clean['label'] = (df_clean['label'] != 'not_cyberbullying').astype(int)
                        print("Converted using 'not_cyberbullying' as negative class")
                    else:
                        # Create binary based on keywords in label
                        negative_keywords = ['not', 'normal', 'neutral', 'clean', 'safe']
                        positive_keywords = ['hate', 'offensive', 'cyberbul', 'abuse', 'toxic', 'aggress']
                        
                        def label_to_binary(label):
                            label_str = str(label).lower()
                            # Check if it's negative class
                            if any(keyword in label_str for keyword in negative_keywords):
                                return 0
                            # Check if it's positive class
                            elif any(keyword in label_str for keyword in positive_keywords):
                                return 1
                            # Default: try to convert to number
                            else:
                                try:
                                    return 1 if float(label) > 0 else 0
                                except:
                                    return 0  # Default to not cyberbullying if unclear
                        
                        df_clean['label'] = df_clean['label'].apply(label_to_binary)
                        print("Converted using keyword-based classification")
                else:
                    # Numeric labels - assume 0 is negative, anything else is positive
                    df_clean['label'] = (df_clean['label'] != 0).astype(int)
                    print("Converted numeric labels to binary")
                
                print(f"Final label distribution:\n{df_clean['label'].value_counts()}")
                
                dfs.append(df_clean)
                print(f"✅ Successfully processed {len(df_clean)} samples from {file_path}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                import traceback
                traceback.print_exc()
        
        if not dfs:
            raise ValueError("❌ No datasets could be loaded successfully!")
        
        # Combine all datasets
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"\n{'='*60}")
        print(f"Combined dataset shape: {combined_df.shape}")
        print(f"Combined label distribution:\n{combined_df['label'].value_counts()}")
        
        # Store original text for comparison
        combined_df['original_text'] = combined_df['text'].copy()
        
        # Clean text
        print("\nCleaning text data...")
        combined_df['cleaned_text'] = combined_df['text'].apply(self.clean_text)
        
        # Show examples of cleaning
        print("\n📝 Cleaning Examples:")
        print("="*60)
        for i in range(min(5, len(combined_df))):
            print(f"Original:  {combined_df.iloc[i]['original_text'][:100]}")
            print(f"Cleaned:   {combined_df.iloc[i]['cleaned_text'][:100]}")
            print(f"Label:     {combined_df.iloc[i]['label']}")
            print("-"*60)
        
        # Remove only completely empty texts
        original_size = len(combined_df)
        combined_df = combined_df[combined_df['cleaned_text'].str.len() > 0]
        removed = original_size - len(combined_df)
        print(f"\nRemoved {removed} completely empty texts")
        
        # Check class balance
        label_counts = combined_df['label'].value_counts()
        print(f"\nFinal label distribution:")
        print(label_counts)
        print(f"Class balance ratio: {label_counts.min() / label_counts.max():.2%}")
        
        # Only balance if severely imbalanced (less than 5% minority class)
        if len(label_counts) == 2:
            minority_class = label_counts.idxmin()
            majority_class = label_counts.idxmax()
            minority_count = label_counts[minority_class]
            majority_count = label_counts[majority_class]
            ratio = minority_count / majority_count
            
            if ratio < 0.05:  # Less than 5%
                print(f"\n⚠️  Dataset is severely imbalanced ({ratio:.2%})")
                print(f"Balancing to 1:5 ratio...")
                
                # Undersample majority class to 5:1 ratio
                target_majority = min(minority_count * 5, majority_count)
                majority_data = combined_df[combined_df['label'] == majority_class].sample(
                    n=target_majority, random_state=42
                )
                minority_data = combined_df[combined_df['label'] == minority_class]
                
                combined_df = pd.concat([majority_data, minority_data], ignore_index=True)
                combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
                
                print(f"Balanced dataset size: {len(combined_df)}")
                print(f"New distribution:\n{combined_df['label'].value_counts()}")
            else:
                print(f"Dataset balance is acceptable ({ratio:.2%})")
        
        print(f"\n{'='*60}")
        print(f"✅ Preprocessing complete!")
        print(f"Final dataset: {len(combined_df)} samples")
        print(f"Average text length: {combined_df['cleaned_text'].str.len().mean():.1f} characters")
        
        return combined_df
    
    def save_preprocessor(self, filepath):
        """Save the preprocessor components"""
        preprocessor_data = {
            'stop_words': self.stop_words,
            'lemmatizer': self.lemmatizer
        }
        with open(filepath, 'wb') as f:
            pickle.dump(preprocessor_data, f)
        print(f"✅ Preprocessor saved to {filepath}")


# Test the preprocessor
if __name__ == "__main__":
    preprocessor = CyberbullyingPreprocessor()
    
    # Test cleaning
    test_texts = [
        "You are so stupid and worthless!",
        "I hate you so much, go die",
        "Have a great day!",
        "Nobody likes you, loser",
        "You're soooo ugly lol"
    ]
    
    print("Testing text cleaning:")
    print("="*60)
    for text in test_texts:
        cleaned = preprocessor.clean_text(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}")
        print("-"*60)