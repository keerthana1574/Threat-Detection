def validate_attack_categorization():
    """Test if all attacks are properly categorized"""
    from nsl_data_preprocessor import NSLKDDPreprocessor
    
    preprocessor = NSLKDDPreprocessor()
    
    # Load dataset
    df = preprocessor.load_nsl_kdd_files('datasets/network_security/NSL-KDD')
    
    # Check for unknown attacks
    unknown_attacks = []
    for attack in df['attack_type'].unique():
        attack_lower = attack.lower().strip()
        if attack_lower not in preprocessor.attack_mapping:
            category = preprocessor._map_attack_category(attack_lower)
            unknown_attacks.append((attack, category))
    
    print(f"\nFound {len(unknown_attacks)} unknown attack types:")
    for attack, category in unknown_attacks:
        category_name = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R'][category]
        print(f"  '{attack}' → {category_name}")
    
    # Check categorization accuracy
    correct = 0
    total = 0
    
    for attack in unknown_attacks:
        total += 1
        # Manual verification would be needed here
        # This is just structure
    
    print(f"\nCategorization coverage: {len(df['attack_type'].unique()) - len(unknown_attacks)}/{len(df['attack_type'].unique())}")

if __name__ == "__main__":
    validate_attack_categorization()