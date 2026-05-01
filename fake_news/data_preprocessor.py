import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
from textstat import flesch_reading_ease, flesch_kincaid_grade
from collections import Counter
import string

class FakeNewsPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.label_encoder = LabelEncoder()
        
    def extract_features(self, text):
        """Extract linguistic and stylistic features from text"""
        if pd.isna(text) or text == "":
            return {}
            
        features = {}
        
        # Basic text statistics
        features['char_count'] = len(text)
        features['word_count'] = len(word_tokenize(text))
        features['sentence_count'] = len(sent_tokenize(text))
        features['avg_word_length'] = np.mean([len(word) for word in word_tokenize(text)])
        
        # Readability scores
        try:
            features['flesch_reading_ease'] = flesch_reading_ease(text)
            features['flesch_kincaid_grade'] = flesch_kincaid_grade(text)
        except:
            features['flesch_reading_ease'] = 0
            features['flesch_kincaid_grade'] = 0
        
        # Punctuation and capitalization features
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['capital_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        features['punctuation_ratio'] = sum(1 for c in text if c in string.punctuation) / len(text) if text else 0
        
        # Emotional indicators
        positive_words = ['amazing', 'great', 'excellent', 'wonderful', 'fantastic', 'incredible']
        negative_words = ['terrible', 'awful', 'horrible', 'disgusting', 'shocking', 'outrageous']
        
        text_lower = text.lower()
        features['positive_words'] = sum(1 for word in positive_words if word in text_lower)
        features['negative_words'] = sum(1 for word in negative_words if word in text_lower)
        
        # Clickbait indicators
        clickbait_phrases = ['you won\'t believe', 'shocking', 'amazing', 'incredible', 'unbelievable']
        features['clickbait_score'] = sum(1 for phrase in clickbait_phrases if phrase in text_lower)
        
        return features
    
    def clean_text(self, text):
        """Clean and preprocess text data"""
        if pd.isna(text):
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?\,\;\:\-\'\"]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def load_liar_dataset(self, file_path):
        """Load and preprocess LIAR dataset"""
        columns = ['id', 'label', 'statement', 'subject', 'speaker', 'job_title', 
                  'state_info', 'party_affiliation', 'barely_true_counts', 
                  'false_counts', 'half_true_counts', 'mostly_true_counts', 
                  'pants_on_fire_counts', 'context']
        
        df = pd.read_csv(file_path, sep='\t', header=None, names=columns)
        
        # Convert labels to binary (fake vs real)
        fake_labels = ['false', 'barely-true', 'pants-fire']
        df['binary_label'] = df['label'].apply(lambda x: 1 if x in fake_labels else 0)
        
        # Combine statement and context
        df['full_text'] = df['statement'].fillna('') + ' ' + df['context'].fillna('')
        
        return df[['full_text', 'binary_label', 'subject', 'speaker']]
    
    def load_fake_real_dataset(self, fake_file, real_file):
        """Load fake and real news dataset"""
        fake_df = pd.read_csv(fake_file)
        real_df = pd.read_csv(real_file)
        
        fake_df['label'] = 1  # Fake news
        real_df['label'] = 0  # Real news
        
        # Standardize columns
        if 'text' not in fake_df.columns and 'title' in fake_df.columns:
            fake_df['text'] = fake_df['title'] + ' ' + fake_df.get('text', '')
        if 'text' not in real_df.columns and 'title' in real_df.columns:
            real_df['text'] = real_df['title'] + ' ' + real_df.get('text', '')
        
        combined_df = pd.concat([fake_df, real_df], ignore_index=True)
        return combined_df[['text', 'label']]
    
    def preprocess_dataset(self, df, text_column='text', label_column='label'):
        """Complete preprocessing pipeline"""
        # Clean text
        df['cleaned_text'] = df[text_column].apply(self.clean_text)
        
        # Extract features
        feature_dicts = df[text_column].apply(self.extract_features)
        feature_df = pd.DataFrame(feature_dicts.tolist())
        
        # Combine with original data
        result_df = pd.concat([df, feature_df], axis=1)
        
        # Remove empty texts
        result_df = result_df[result_df['cleaned_text'].str.len() > 0]
        
        return result_df
    
    def save_preprocessor(self, filepath):
        """Save the label encoder and other preprocessing components"""
        preprocessing_components = {
            'label_encoder': self.label_encoder,
            'stop_words': self.stop_words
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(preprocessing_components, f)