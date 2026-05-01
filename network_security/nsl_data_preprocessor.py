# backend/modules/network_security/nsl_data_preprocessor.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
import os
import logging

logger = logging.getLogger(__name__)

class NSLKDDPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
        # NSL-KDD column names (41 features + 1 target + 1 difficulty)
        self.columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
            'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
            'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
            'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
            'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
            'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
        ]
        
        # Categorical columns to encode
        self.categorical_columns = ['protocol_type', 'service', 'flag']
        
        # Attack category mapping
        # NEW attack_mapping (COMPLETE)
        self.attack_mapping = {
            # Normal traffic
            'normal': 0,
            
            # DoS/DDoS attacks
            'dos': 1, 'ddos': 1, 'back': 1, 'land': 1, 'neptune': 1, 'pod': 1, 
            'smurf': 1, 'teardrop': 1, 'apache2': 1, 'processtable': 1, 
            'mailbomb': 1, 'udpstorm': 1,
            
            # Probe attacks (scanning/reconnaissance)
            'probe': 2, 'ipsweep': 2, 'nmap': 2, 'portsweep': 2, 'satan': 2,
            'saint': 2, 'mscan': 2, 'snmpgetattack': 2,
            
            # R2L attacks (remote to local)
            'r2l': 3, 'ftp_write': 3, 'guess_passwd': 3, 'imap': 3, 'multihop': 3, 
            'phf': 3, 'spy': 3, 'warezclient': 3, 'warezmaster': 3, 'httptunnel': 3,
            'snmpguess': 3,
            
            # U2R attacks (user to root)
            'u2r': 4, 'buffer_overflow': 4, 'loadmodule': 4, 'perl': 4, 'rootkit': 4,
            'sqlattack': 4, 'xterm': 4, 'ps': 4, 'named': 4, 'sendmail': 4,
            'xlock': 4, 'xsnoop': 4, 'worm': 4
        }
    
    def load_nsl_kdd_files(self, dataset_dir='datasets/network_security/NSL-KDD'):
        """Load NSL-KDD dataset files"""
        print(f"Loading NSL-KDD dataset from {dataset_dir}")
        
        # Common NSL-KDD file names
        possible_files = [
            'KDDTrain+.txt', 'KDDTest+.txt',
            'KDDTrain+.csv', 'KDDTest+.csv',
            'NSL_KDDTrain+.txt', 'NSL_KDDTest+.txt',
            'NSL_KDDTrain+.csv', 'NSL_KDDTest+.csv'
        ]
        
        train_file = None
        test_file = None
        
        # Find available files
        for file in os.listdir(dataset_dir):
            if 'train' in file.lower() and file in possible_files:
                train_file = os.path.join(dataset_dir, file)
            elif 'test' in file.lower() and file in possible_files:
                test_file = os.path.join(dataset_dir, file)
        
        if not train_file or not test_file:
            print("Available files in directory:")
            for f in os.listdir(dataset_dir):
                print(f"  {f}")
            raise FileNotFoundError("Could not find NSL-KDD train/test files. Expected files like KDDTrain+.txt, KDDTest+.txt")
        
        print(f"Found train file: {train_file}")
        print(f"Found test file: {test_file}")
        
        # Load datasets
        try:
            # Try loading with comma separator first
            train_df = pd.read_csv(train_file, names=self.columns, header=None)
            test_df = pd.read_csv(test_file, names=self.columns, header=None)
            
            print(f"Train dataset shape: {train_df.shape}")
            print(f"Test dataset shape: {test_df.shape}")
            
        except Exception as e:
            print(f"Error with comma separator, trying with different separators: {e}")
            # Try with different separators
            for sep in [',', '\t', ' ', ';']:
                try:
                    train_df = pd.read_csv(train_file, names=self.columns, header=None, sep=sep)
                    test_df = pd.read_csv(test_file, names=self.columns, header=None, sep=sep)
                    print(f"Successfully loaded with separator: '{sep}'")
                    break
                except:
                    continue
            else:
                raise ValueError("Could not load dataset with any common separator")
        
        # Combine datasets
        combined_df = pd.concat([train_df, test_df], ignore_index=True)
        
        print(f"Combined dataset shape: {combined_df.shape}")
        print(f"Attack types found: {combined_df['attack_type'].unique()}")
        
        return combined_df
    
    def preprocess_data(self, df):
        """Preprocess NSL-KDD data"""
        print("Starting data preprocessing...")
        
        # Remove last column if it exists (difficulty level)
        if 'difficulty' in df.columns:
            df = df.drop('difficulty', axis=1)
        
        # Clean attack type column (remove trailing dots, spaces)
        df['attack_type'] = df['attack_type'].astype(str).str.strip().str.rstrip('.')
        
        print(f"Cleaned attack types: {df['attack_type'].value_counts()}")
        
        # Create binary labels (0=normal, 1=attack)
        df['is_attack'] = (df['attack_type'] != 'normal').astype(int)
        
        # Create multi-class labels
        df['attack_category'] = df['attack_type'].map(
            lambda x: self._map_attack_category(x.lower())
        )
        
        print(f"Binary distribution: {df['is_attack'].value_counts()}")
        print(f"Attack category distribution: {df['attack_category'].value_counts()}")
        
        # Separate features from targets
        feature_columns = [col for col in df.columns if col not in ['attack_type', 'is_attack', 'attack_category']]
        X = df[feature_columns].copy()
        y_binary = df['is_attack']
        y_multi = df['attack_category']
        
        # Handle categorical columns
        print("Encoding categorical features...")
        for col in self.categorical_columns:
            if col in X.columns:
                print(f"Encoding {col}: {X[col].nunique()} unique values")
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le
        
        # Handle missing and infinite values
        print("Handling missing and infinite values...")
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)
        
        # Get numerical columns for scaling
        numerical_columns = [col for col in X.columns if col not in self.categorical_columns]
        
        print(f"Scaling {len(numerical_columns)} numerical features...")
        
        # Scale only numerical columns
        X_scaled = X.copy()
        X_scaled[numerical_columns] = self.scaler.fit_transform(X[numerical_columns])
        
        print(f"Final preprocessed data shape: {X_scaled.shape}")
        print("Preprocessing completed successfully!")
        
        return X_scaled, y_binary, y_multi
    
    def _map_attack_category(self, attack_type):
        """Enhanced attack mapping with better categorization"""
        attack_type = attack_type.lower().strip()
        
        # Direct mapping first
        if attack_type in self.attack_mapping:
            return self.attack_mapping[attack_type]
        
        # DoS patterns (overwhelm resources)
        dos_keywords = ['dos', 'ddos', 'back', 'land', 'neptune', 'pod', 'smurf', 
                        'teardrop', 'apache', 'processtable', 'mailbomb', 'udpstorm']
        if any(keyword in attack_type for keyword in dos_keywords):
            return 1
        
        # Probe patterns (scanning/reconnaissance)
        probe_keywords = ['probe', 'scan', 'sweep', 'portsweep', 'ipsweep', 
                        'nmap', 'satan', 'saint', 'mscan', 'snmp']
        if any(keyword in attack_type for keyword in probe_keywords):
            return 2
        
        # R2L patterns (remote access attempts)
        r2l_keywords = ['r2l', 'remote', 'ftp', 'guess', 'imap', 'phf', 'spy', 
                        'warezclient', 'warezmaster', 'httptunnel', 'http']
        if any(keyword in attack_type for keyword in r2l_keywords):
            return 3
        
        # U2R patterns (privilege escalation)
        u2r_keywords = ['u2r', 'buffer', 'overflow', 'rootkit', 'loadmodule', 
                        'perl', 'xterm', 'ps', 'named', 'sendmail', 'xlock', 
                        'xsnoop', 'worm', 'sql']
        if any(keyword in attack_type for keyword in u2r_keywords):
            return 4
        
        # Log unknown attacks but still classify them
        print(f"Warning: Unrecognized attack '{attack_type}', analyzing pattern...")
        
        # Default: if completely unknown, classify as DoS (most common attack)
        return 1
    
    def save_preprocessor(self, save_dir):
        """Save preprocessing components"""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save label encoders
        with open(f"{save_dir}/label_encoders.pkl", 'wb') as f:
            pickle.dump(self.label_encoders, f)
        
        # Save scaler
        with open(f"{save_dir}/scaler.pkl", 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save column information
        with open(f"{save_dir}/columns_info.pkl", 'wb') as f:
            pickle.dump({
                'columns': self.columns,
                'categorical_columns': self.categorical_columns,
                'attack_mapping': self.attack_mapping
            }, f)
        
        print(f"Preprocessor saved to {save_dir}")
