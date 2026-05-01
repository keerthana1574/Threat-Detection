# backend/modules/network_security/model_version.py

import json
from datetime import datetime

class ModelVersion:
    def __init__(self):
        self.version = "1.0.0"
        self.trained_date = datetime.now().isoformat()
        self.model_info = {}
    
    def save_version_info(self, model_dir, model_results):
        """Save model version information"""
        version_info = {
            'version': self.version,
            'trained_date': self.trained_date,
            'model_performance': {
                name: {
                    'accuracy': results.get('accuracy', 0),
                    'auc': results.get('auc', 0)
                }
                for name, results in model_results.items()
            },
            'dataset': 'NSL-KDD',
            'features_count': 41,
            'attack_types': ['normal', 'dos', 'probe', 'r2l', 'u2r']
        }
        
        with open(f"{model_dir}/version_info.json", 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print(f"Version info saved: v{self.version}")

# In nsl_train.py, after training:
from model_version import ModelVersion

version = ModelVersion()
version.save_version_info(model_dir, all_results) # type: ignore