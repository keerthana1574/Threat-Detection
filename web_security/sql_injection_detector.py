import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime
from urllib.parse import unquote
import html

class SQLInjectionDetector:
    def __init__(self):
        self.models = {}
        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 3))
        
        # MUCH MORE COMPREHENSIVE SQL INJECTION PATTERNS
        self.sql_patterns = [
            # Basic OR injections (MOST COMMON)
            r"('\s*[oO][rR]\s*')",  # ' OR '
            r"('\s*[oO][rR]\s*\d+)",  # ' OR 1
            r"(\"\s*[oO][rR]\s*\")",  # " OR "
            r"(\"\s*[oO][rR]\s*\d+)",  # " OR 1
            
            # OR with equals (VERY COMMON)
            r"('\s*[oO][rR]\s*'.*?=.*?')",  # ' OR 'x'='x
            r"(\"\s*[oO][rR]\s*\".*?=.*?\")",  # " OR "x"="x
            r"('\s*[oO][rR]\s*\d+\s*=\s*\d+)",  # ' OR 1=1
            r"(\"\s*[oO][rR]\s*\d+\s*=\s*\d+)",  # " OR 1=1
            
            # AND injections
            r"('\s*[aA][nN][dD]\s*')",
            r"('\s*[aA][nN][dD]\s*\d+)",
            r"(\"\s*[aA][nN][dD]\s*\")",
            r"(\"\s*[aA][nN][dD]\s*\d+)",
            
            # UNION attacks
            r"([uU][nN][iI][oO][nN]\s+[sS][eE][lL][eE][cC][tT])",
            r"([uU][nN][iI][oO][nN]\s+[aA][lL][lL]\s+[sS][eE][lL][eE][cC][tT])",
            
            # Comment injection
            r"(--)",  # SQL comment
            r"(#)",   # MySQL comment
            r"(/\*)",  # Multi-line comment start
            r"(\*/)",  # Multi-line comment end
            
            # Admin bypass patterns
            r"(admin'\s*--)",
            r"(admin\"\s*--)",
            r"(admin'\s*#)",
            
            # Stacked queries
            r"(;\s*[dD][rR][oO][pP])",
            r"(;\s*[dD][eE][lL][eE][tT][eE])",
            r"(;\s*[uU][pP][dD][aA][tT][eE])",
            r"(;\s*[iI][nN][sS][eE][rR][tT])",
            r"(;\s*[sS][eE][lL][eE][cC][tT])",
            
            # Time-based blind
            r"([sS][lL][eE][eE][pP]\s*\()",
            r"([wW][aA][iI][tT][fF][oO][rR]\s+[dD][eE][lL][aA][yY])",
            r"([bB][eE][nN][cC][hH][mM][aA][rR][kK]\s*\()",
            
            # Information gathering
            r"([iI][nN][fF][oO][rR][mM][aA][tT][iI][oO][nN]_[sS][cC][hH][eE][mM][aA])",
            r"([sS][yY][sS][oO][bB][jJ][eE][cC][tT][sS])",
            r"([tT][aA][bB][lL][eE]_[nN][aA][mM][eE])",
            
            # Stored procedures
            r"([xX][pP]_)",
            r"([sS][pP]_)",
            r"([eE][xX][eE][cC]\s+)",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
    
    def extract_features(self, input_string):
        if not input_string:
            return np.zeros(20)
        
        text_lower = input_string.lower()
        features = [
            len(input_string),
            input_string.count("'"),
            input_string.count('"'),
            input_string.count('--'),
            input_string.count('/*'),
            input_string.count('#'),
            text_lower.count('union'),
            text_lower.count('select'),
            text_lower.count(' or '),
            text_lower.count(' and '),
            input_string.count('='),
            input_string.count(';'),
            text_lower.count('drop'),
            text_lower.count('exec'),
            input_string.count('\\'),
            text_lower.count('admin'),
            text_lower.count('sleep'),
            text_lower.count('waitfor'),
            text_lower.count('information_schema'),
            text_lower.count('sysobjects'),
        ]
        return np.array(features)
    
    def rule_based_detection(self, input_string):
        """IMPROVED rule-based detection with LOWER threshold"""
        if not input_string or len(input_string) < 2:
            return {'is_malicious': False, 'risk_score': 0, 'detections': [], 'confidence': 0.0}
        
        text_lower = input_string.lower()
        decoded = unquote(input_string)
        decoded_lower = decoded.lower()
        
        # Also check HTML decoded version
        html_decoded = html.unescape(input_string)
        html_decoded_lower = html_decoded.lower()
        
        detections = []
        risk_score = 0
        
        # Test all versions of the input
        test_strings = [text_lower, decoded_lower, html_decoded_lower]
        
        # Pattern matching
        for test_string in test_strings:
            for i, pattern in enumerate(self.compiled_patterns):
                matches = pattern.findall(test_string)
                if matches and not any(d.get('pattern_id') == i for d in detections):
                    risk_score += 12  # LOWERED from 15
                    detections.append({
                        'pattern_id': i,
                        'matches': len(matches),
                        'type': f"sql_pattern_{i}",
                        'matched_text': str(matches[0])[:50] if matches else ''
                    })
        
        # HIGH RISK PATTERNS - EXPANDED LIST
        high_risk_patterns = {
            # OR injections
            "' or '": 30,
            '" or "': 30,
            "' or 1": 35,
            '" or 1': 35,
            "' or '1'='1": 40,
            '" or "1"="1': 40,
            "' or 1=1": 40,
            '" or 1=1': 40,
            "' or true": 35,
            "' or 't'='t": 35,
            "or 1=1": 25,
            
            # Admin bypass
            "admin'--": 40,
            "admin\"--": 40,
            "admin' #": 40,
            "admin'/*": 40,
            
            # UNION attacks
            'union select': 35,
            'union all select': 35,
            
            # Dangerous commands
            'drop table': 45,
            'delete from': 35,
            'insert into': 30,
            'update set': 25,
            
            # Stored procedures
            'exec xp_': 40,
            'xp_cmdshell': 45,
            'sp_executesql': 35,
            
            # Time-based
            'waitfor delay': 35,
            'benchmark(': 35,
            'sleep(': 35,
            'pg_sleep': 35,
            
            # Information gathering
            'information_schema': 25,
            'sysobjects': 30,
            'syscolumns': 30,
            'table_name': 20,
            
            # File operations
            'load_file': 35,
            'into outfile': 35,
            'into dumpfile': 35,
        }
        
        for pattern, score in high_risk_patterns.items():
            if pattern in text_lower or pattern in decoded_lower or pattern in html_decoded_lower:
                risk_score += score
                detections.append({'type': 'high_risk', 'pattern': pattern, 'score': score})
        
        # SQL keyword combinations (LOWERED threshold)
        sql_keywords = ['select', 'union', 'insert', 'update', 'delete', 'drop', 'exec', 'create', 'alter']
        keyword_count = sum(1 for keyword in sql_keywords if keyword in text_lower)
        if keyword_count >= 1:  # LOWERED from 2
            risk_score += keyword_count * 8  # LOWERED from 10
            detections.append({'type': 'sql_keywords', 'count': keyword_count})
        
        # Comment indicators
        if any(comment in text_lower for comment in ['--', '/*', '#']):
            risk_score += 12  # LOWERED from 15
            detections.append({'type': 'sql_comments'})
        
        # Quotes (LOWERED threshold)
        quote_count = text_lower.count("'") + text_lower.count('"')
        if quote_count >= 2:  # LOWERED from 3
            risk_score += min(quote_count * 4, 20)  # LOWERED from 5, 25
            detections.append({'type': 'excessive_quotes', 'count': quote_count})
        
        # Semicolon (command separator)
        if ';' in input_string:
            risk_score += 10
            detections.append({'type': 'semicolon_separator'})
        
        # Equals signs (LOWERED threshold)
        equals_count = input_string.count('=')
        if equals_count >= 1:  # LOWERED from 2
            risk_score += equals_count * 3
            detections.append({'type': 'equals_signs', 'count': equals_count})
        
        # LOWERED THRESHOLD FOR DETECTION
        is_malicious = risk_score >= 25 or len([d for d in detections if d.get('type') == 'high_risk']) >= 1  # LOWERED from 35
        
        return {
            'is_malicious': is_malicious,
            'risk_score': risk_score,
            'detections': detections,
            'confidence': min(risk_score / 80.0, 0.98)  # LOWERED denominator from 100
        }
    
    def predict(self, input_string):
        rule_result = self.rule_based_detection(input_string)
        
        result = {
            'input': input_string,
            'timestamp': datetime.now().isoformat(),
            'rule_based': rule_result,
            'ml_predictions': {},
            'final_prediction': rule_result['is_malicious'],
            'confidence': rule_result['confidence']
        }
        
        # Try ML models if available
        if self.models and self.vectorizer:
            try:
                manual_features = self.extract_features(input_string)
                tfidf_features = self.vectorizer.transform([input_string])
                
                from scipy.sparse import hstack
                combined = hstack([tfidf_features, manual_features.reshape(1, -1)])
                
                ml_predictions = {}
                ml_scores = []
                
                for name, model in self.models.items():
                    pred_proba = model.predict_proba(combined)[0]
                    ml_predictions[name] = {
                        'prediction': bool(pred_proba[1] > 0.5),
                        'probability': float(pred_proba[1])
                    }
                    ml_scores.append(pred_proba[1])
                
                result['ml_predictions'] = ml_predictions
                avg_ml_score = np.mean(ml_scores) if ml_scores else 0
                
                # LOWERED threshold
                if rule_result['is_malicious'] or avg_ml_score > 0.5:  # LOWERED from 0.6
                    result['final_prediction'] = True
                    result['confidence'] = max(rule_result['confidence'], avg_ml_score)
                    
            except Exception as e:
                pass
        
        return result
    
    def save_models(self, model_dir):
        os.makedirs(model_dir, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{model_dir}/sqli_{name}_model.pkl")
        joblib.dump(self.vectorizer, f"{model_dir}/sqli_vectorizer.pkl")
    
    def load_models(self, model_dir):
        try:
            for model_name in ['random_forest', 'logistic_regression']:
                model_path = f"{model_dir}/sqli_{model_name}_model.pkl"
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
            
            vec_path = f"{model_dir}/sqli_vectorizer.pkl"
            if os.path.exists(vec_path):
                self.vectorizer = joblib.load(vec_path)
            
            return len(self.models) > 0
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


class XSSDetector:
    def __init__(self):
        self.models = {}
        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 3))
        
        # MUCH MORE COMPREHENSIVE XSS PATTERNS
        self.xss_patterns = [
            # Script tags (MOST COMMON)
            r"<\s*script",
            r"</\s*script\s*>",
            
            # Event handlers (VERY COMMON)
            r"on\w+\s*=",  # Any event handler
            r"onerror\s*=",
            r"onload\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"onfocus\s*=",
            r"onmouseout\s*=",
            r"onkeypress\s*=",
            r"onchange\s*=",
            r"onsubmit\s*=",
            
            # JavaScript protocols
            r"javascript\s*:",
            r"vbscript\s*:",
            r"data\s*:\s*text/html",
            
            # Dangerous tags
            r"<\s*iframe",
            r"<\s*embed",
            r"<\s*object",
            r"<\s*img",
            r"<\s*svg",
            r"<\s*body",
            r"<\s*link",
            r"<\s*meta",
            r"<\s*style",
            r"<\s*frame",
            r"<\s*frameset",
            
            # Dangerous functions
            r"alert\s*\(",
            r"confirm\s*\(",
            r"prompt\s*\(",
            r"eval\s*\(",
            r"document\.write",
            r"document\.writeln",
            r"innerHTML",
            r"outerHTML",
            
            # Expression (IE)
            r"expression\s*\(",
            
            # Data URIs
            r"data:text/html",
            r"data:application/",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
    
    def extract_features(self, input_string):
        if not input_string:
            return np.zeros(20)
        
        text_lower = input_string.lower()
        features = [
            len(input_string),
            input_string.count('<'),
            input_string.count('>'),
            text_lower.count('script'),
            text_lower.count('javascript'),
            text_lower.count('onerror'),
            text_lower.count('onload'),
            text_lower.count('alert'),
            text_lower.count('eval'),
            text_lower.count('iframe'),
            input_string.count('='),
            text_lower.count('src'),
            text_lower.count('href'),
            input_string.count('"'),
            input_string.count("'"),
            text_lower.count('onclick'),
            text_lower.count('onmouseover'),
            text_lower.count('svg'),
            text_lower.count('img'),
            text_lower.count('document'),
        ]
        return np.array(features)
    
    def rule_based_detection(self, input_string):
        """IMPROVED rule-based detection with LOWER threshold"""
        if not input_string or len(input_string) < 2:
            return {'is_malicious': False, 'risk_score': 0, 'detections': [], 'confidence': 0.0}
        
        text_lower = input_string.lower()
        decoded = unquote(input_string)
        decoded_lower = decoded.lower()
        html_decoded = html.unescape(input_string)
        html_decoded_lower = html_decoded.lower()
        
        detections = []
        risk_score = 0
        
        # Test all versions
        test_strings = [text_lower, decoded_lower, html_decoded_lower]
        
        # Pattern matching
        for test_string in test_strings:
            for i, pattern in enumerate(self.compiled_patterns):
                if pattern.search(test_string) and not any(d.get('pattern_id') == i for d in detections):
                    risk_score += 10  # LOWERED from 12
                    detections.append({'pattern_id': i, 'type': f'xss_pattern_{i}'})
        
        # HIGH RISK PATTERNS - EXPANDED
        high_risk_patterns = {
            # Script injections
            '<script': 40,
            '</script>': 40,
            '<script>': 40,
            
            # JavaScript protocols
            'javascript:alert': 45,
            'javascript:prompt': 45,
            'javascript:confirm': 45,
            'javascript:': 30,
            
            # Event handler injections
            '<img src=x onerror=': 40,
            'onerror=alert': 40,
            'onload=alert': 40,
            'onclick=alert': 35,
            'onmouseover=alert': 35,
            'onfocus=alert': 35,
            
            # SVG attacks
            '<svg onload=': 40,
            '<svg/onload=': 40,
            
            # Iframe attacks
            '<iframe src=javascript:': 45,
            '<iframe src=': 30,
            
            # Dangerous functions
            'eval(': 30,
            'document.write': 30,
            'document.writeln': 30,
            'innerhtml': 25,
            'outerhtml': 25,
            
            # Object/embed
            '<object data=javascript:': 40,
            '<embed src=javascript:': 40,
            
            # Data URIs
            'data:text/html': 35,
            'data:application/': 30,
            
            # Expression
            'expression(': 30,
        }
        
        for pattern, score in high_risk_patterns.items():
            if pattern in text_lower or pattern in decoded_lower or pattern in html_decoded_lower:
                risk_score += score
                detections.append({'type': 'high_risk_xss', 'pattern': pattern, 'score': score})
        
        # Event handlers count
        event_handlers = ['onerror=', 'onload=', 'onclick=', 'onmouseover=', 'onfocus=', 'onmouseout=']
        handler_count = sum(1 for handler in event_handlers if handler in text_lower)
        if handler_count >= 1:  # LOWERED from 1 (but more sensitive detection)
            risk_score += handler_count * 12
            detections.append({'type': 'event_handlers', 'count': handler_count})
        
        # Tag detection
        if '<' in input_string and '>' in input_string:
            dangerous_tags = ['script', 'iframe', 'object', 'embed', 'svg', 'img', 'body', 'link', 'meta']
            tag_count = sum(1 for tag in dangerous_tags if f'<{tag}' in text_lower or f'</{tag}' in text_lower)
            if tag_count >= 1:
                risk_score += tag_count * 15
                detections.append({'type': 'dangerous_tags', 'count': tag_count})
        
        # Angle brackets (potential tag injection)
        angle_bracket_count = input_string.count('<') + input_string.count('>')
        if angle_bracket_count >= 2:  # At least one complete tag
            risk_score += 8
            detections.append({'type': 'angle_brackets', 'count': angle_bracket_count})
        
        # LOWERED THRESHOLD
        is_malicious = risk_score >= 25 or len([d for d in detections if d.get('type') == 'high_risk_xss']) >= 1  # LOWERED from 35
        
        return {
            'is_malicious': is_malicious,
            'risk_score': risk_score,
            'detections': detections,
            'confidence': min(risk_score / 80.0, 0.98)  # LOWERED from 100
        }
    
    def predict(self, input_string):
        rule_result = self.rule_based_detection(input_string)
        
        result = {
            'input': input_string,
            'timestamp': datetime.now().isoformat(),
            'rule_based': rule_result,
            'ml_predictions': {},
            'final_prediction': rule_result['is_malicious'],
            'confidence': rule_result['confidence']
        }
        
        # Try ML models if available
        if self.models and self.vectorizer:
            try:
                manual_features = self.extract_features(input_string)
                tfidf_features = self.vectorizer.transform([input_string])
                
                from scipy.sparse import hstack
                combined = hstack([tfidf_features, manual_features.reshape(1, -1)])
                
                ml_predictions = {}
                ml_scores = []
                
                for name, model in self.models.items():
                    pred_proba = model.predict_proba(combined)[0]
                    ml_predictions[name] = {
                        'prediction': bool(pred_proba[1] > 0.5),
                        'probability': float(pred_proba[1])
                    }
                    ml_scores.append(pred_proba[1])
                
                result['ml_predictions'] = ml_predictions
                avg_ml_score = np.mean(ml_scores) if ml_scores else 0
                
                # LOWERED threshold
                if rule_result['is_malicious'] or avg_ml_score > 0.5:  # LOWERED from 0.6
                    result['final_prediction'] = True
                    result['confidence'] = max(rule_result['confidence'], avg_ml_score)
                    
            except Exception as e:
                pass
        
        return result
    
    def save_models(self, model_dir):
        os.makedirs(model_dir, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{model_dir}/xss_{name}_model.pkl")
        joblib.dump(self.vectorizer, f"{model_dir}/xss_vectorizer.pkl")
    
    def load_models(self, model_dir):
        try:
            for model_name in ['random_forest', 'logistic_regression']:
                model_path = f"{model_dir}/xss_{model_name}_model.pkl"
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
            
            vec_path = f"{model_dir}/xss_vectorizer.pkl"
            if os.path.exists(vec_path):
                self.vectorizer = joblib.load(vec_path)
            
            return len(self.models) > 0
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


# COMPREHENSIVE TEST SUITE
if __name__ == "__main__":
    print("="*80)
    print("COMPREHENSIVE SQL & XSS DETECTION TEST")
    print("="*80)
    
    sql_detector = SQLInjectionDetector()
    xss_detector = XSSDetector()
    
    # EXPANDED SQL INJECTION TEST CASES
    sql_test_cases = [
        # Basic OR injections
        ("' OR '1'='1", True),
        ("' OR 1=1--", True),
        ("admin' OR '1'='1'--", True),
        ('" OR "1"="1', True),
        ("' OR 'x'='x", True),
        ("1' OR '1'='1", True),
        
        # Simple OR
        ("' OR '", True),
        ('" OR "', True),
        ("' OR 1", True),
        
        # Admin bypass
        ("admin'--", True),
        ("admin' #", True),
        ("admin' /*", True),
        
        # UNION
        ("' UNION SELECT NULL--", True),
        ("1' UNION SELECT password FROM users--", True),
        
        # Stacked queries
        ("'; DROP TABLE users--", True),
        ("1'; DELETE FROM users--", True),
        
        # Time-based
        ("'; SLEEP(5)--", True),
        ("'; WAITFOR DELAY '00:00:05'--", True),
        
        # Various encodings
        ("%27%20OR%20%271%27%3D%271", True),
        
        # Safe inputs
        ("john.doe@example.com", False),
        ("user123", False),
        ("password123!", False),
        ("SELECT * FROM products WHERE id=5", False),  # Might be flagged
    ]
    
    # EXPANDED XSS TEST CASES
    xss_test_cases = [
        # Script tags
        ("<script>alert('XSS')</script>", True),
        ("<script>alert(1)</script>", True),
        ("<SCRIPT>alert('XSS')</SCRIPT>", True),
        
        # Event handlers
        ("<img src=x onerror=alert('XSS')>", True),
        ("<img src=x onerror=alert(1)>", True),
        ("<body onload=alert('XSS')>", True),
        ("<svg onload=alert(1)>", True),
        ("<input onfocus=alert(1) autofocus>", True),
        
        # JavaScript protocol
        ("javascript:alert('XSS')", True),
        ("<a href=javascript:alert(1)>Click</a>", True),
        
        # Iframe
        ("<iframe src=javascript:alert('XSS')>", True),
        
        # Various encodings
        ("<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>", True),
        
        # Object/embed
        ("<object data=javascript:alert(1)>", True),
        ("<embed src=javascript:alert(1)>", True),
        
        # Safe inputs
        ("Hello world", False),
        ("user@example.com", False),
        ("Click <here> for more info", False),
        ("<p>Normal HTML paragraph</p>", False),
    ]
    
    print("\nSQL INJECTION DETECTION:")
    print("-"*80)
    sql_correct = 0
    for payload, expected in sql_test_cases:
        result = sql_detector.predict(payload)
        detected = result['final_prediction']
        status = "✓" if detected == expected else "✗"
        
        if detected == expected:
            sql_correct += 1
        
        label = "DETECTED" if detected else "SAFE"
        expected_label = "EXPECTED DETECTED" if expected else "EXPECTED SAFE"
        
        print(f"[{status}] [{label}] {payload[:50]}")
        if detected != expected:
            print(f"    ^ MISMATCH! {expected_label}")
            print(f"    Risk Score: {result['rule_based']['risk_score']}")
            print(f"    Detections: {len(result['rule_based']['detections'])}")
    
    print(f"\nSQL Accuracy: {sql_correct}/{len(sql_test_cases)} ({sql_correct/len(sql_test_cases)*100:.1f}%)")
    
    print("\n" + "="*80)
    print("XSS DETECTION:")
    print("-"*80)
    xss_correct = 0
    for payload, expected in xss_test_cases:
        result = xss_detector.predict(payload)
        detected = result['final_prediction']
        status = "✓" if detected == expected else "✗"
        
        if detected == expected:
            xss_correct += 1
        
        label = "DETECTED" if detected else "SAFE"
        expected_label = "EXPECTED DETECTED" if expected else "EXPECTED SAFE"
        
        print(f"[{status}] [{label}] {payload[:50]}")
        if detected != expected:
            print(f"    ^ MISMATCH! {expected_label}")
            print(f"    Risk Score: {result['rule_based']['risk_score']}")
            print(f"    Detections: {len(result['rule_based']['detections'])}")
    
    print(f"\nXSS Accuracy: {xss_correct}/{len(xss_test_cases)} ({xss_correct/len(xss_test_cases)*100:.1f}%)")
    print("="*80)