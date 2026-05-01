import re
import requests
from urllib.parse import urlparse, parse_qs
import tldextract
import whois
from datetime import datetime
import socket
import ssl
import pandas as pd
import numpy as np
from textstat import flesch_reading_ease
import dns.resolver
from bs4 import BeautifulSoup

class URLAnalyzer:
    def __init__(self):
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.pw', '.top', '.click', '.download',
            '.bid', '.win', '.party', '.review', '.trade', '.date', '.racing'
        ]
        
        self.legitimate_domains = [
            'google.com', 'facebook.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'paypal.com', 'ebay.com', 'twitter.com',
            'instagram.com', 'linkedin.com', 'github.com', 'stackoverflow.com'
        ]
        
    def extract_url_features(self, url):
        """Extract comprehensive features from URL"""
        features = {}
        
        try:
            parsed_url = urlparse(url)
            domain_info = tldextract.extract(url)
            
            # Basic URL features
            features['url_length'] = len(url)
            features['domain_length'] = len(parsed_url.netloc)
            features['path_length'] = len(parsed_url.path)
            features['query_length'] = len(parsed_url.query) if parsed_url.query else 0
            
            # Character analysis
            features['num_dots'] = url.count('.')
            features['num_hyphens'] = url.count('-')
            features['num_underscores'] = url.count('_')
            features['num_slashes'] = url.count('/')
            features['num_questionmarks'] = url.count('?')
            features['num_equals'] = url.count('=')
            features['num_ats'] = url.count('@')
            features['num_ampersands'] = url.count('&')
            
            # Protocol analysis
            features['is_https'] = 1 if parsed_url.scheme == 'https' else 0
            features['has_port'] = 1 if parsed_url.port else 0
            features['suspicious_port'] = 1 if parsed_url.port and parsed_url.port not in [80, 443, 8080] else 0
            
            # Domain analysis
            features['has_subdomain'] = 1 if domain_info.subdomain else 0
            features['subdomain_count'] = len(domain_info.subdomain.split('.')) if domain_info.subdomain else 0
            features['suspicious_tld'] = 1 if any(tld in url.lower() for tld in self.suspicious_tlds) else 0
            
            # Suspicious patterns
            features['has_ip_address'] = self.has_ip_address(parsed_url.netloc)
            features['url_shortener'] = self.is_url_shortener(domain_info.domain)
            features['suspicious_keywords'] = self.count_suspicious_keywords(url)
            features['homograph_attack'] = self.detect_homograph_attack(parsed_url.netloc)
            
            # Encoding and obfuscation
            features['has_hex_chars'] = 1 if re.search(r'%[0-9a-fA-F]{2}', url) else 0
            features['has_unicode'] = 1 if any(ord(char) > 127 for char in url) else 0
            
            # Length-based suspicious indicators
            features['extremely_long_url'] = 1 if len(url) > 200 else 0
            features['extremely_long_domain'] = 1 if len(parsed_url.netloc) > 50 else 0
            
            # Query parameter analysis
            if parsed_url.query:
                query_params = parse_qs(parsed_url.query)
                features['num_query_params'] = len(query_params)
                features['has_suspicious_params'] = self.has_suspicious_query_params(query_params)
            else:
                features['num_query_params'] = 0
                features['has_suspicious_params'] = 0
            
        except Exception as e:
            # Fill with default values if URL parsing fails
            for key in ['url_length', 'domain_length', 'path_length', 'query_length',
                       'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes',
                       'num_questionmarks', 'num_equals', 'num_ats', 'num_ampersands',
                       'is_https', 'has_port', 'suspicious_port', 'has_subdomain',
                       'subdomain_count', 'suspicious_tld', 'has_ip_address',
                       'url_shortener', 'suspicious_keywords', 'homograph_attack',
                       'has_hex_chars', 'has_unicode', 'extremely_long_url',
                       'extremely_long_domain', 'num_query_params', 'has_suspicious_params']:
                features[key] = 0
            
            features['url_length'] = len(url) if url else 0
        
        return features
    
    def has_ip_address(self, netloc):
        """Check if URL uses IP address instead of domain"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return 1 if re.search(ip_pattern, netloc) else 0
    
    def is_url_shortener(self, domain):
        """Check if domain is a known URL shortener"""
        shorteners = [
            'bit.ly', 'tinyurl.com', 'short.link', 'ow.ly', 't.co',
            'goo.gl', 'buff.ly', 'adf.ly', 'tr.im', 'is.gd'
        ]
        return 1 if domain.lower() in shorteners else 0
    
    def count_suspicious_keywords(self, url):
        """Count suspicious keywords in URL"""
        suspicious_words = [
            'login', 'signin', 'account', 'update', 'verify', 'secure',
            'bank', 'paypal', 'amazon', 'microsoft', 'apple', 'google',
            'facebook', 'security', 'suspended', 'limited', 'confirm'
        ]
        
        url_lower = url.lower()
        count = sum(1 for word in suspicious_words if word in url_lower)
        return min(count, 5)  # Cap at 5
    
    def detect_homograph_attack(self, domain):
        """Detect potential homograph attacks"""
        # Check for mixed scripts or suspicious unicode characters
        suspicious_chars = ['а', 'е', 'о', 'р', 'с', 'у', 'х']  # Cyrillic chars that look like Latin
        return 1 if any(char in domain.lower() for char in suspicious_chars) else 0
    
    def has_suspicious_query_params(self, query_params):
        """Check for suspicious query parameters"""
        suspicious_params = ['redirect', 'url', 'link', 'goto', 'next', 'return']
        return 1 if any(param.lower() in suspicious_params for param in query_params.keys()) else 0

class WebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def analyze_website(self, url, timeout=10):
        """Analyze website content and structure"""
        features = {}
        
        try:
            response = self.session.get(url, timeout=timeout, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Content analysis
            features['page_size'] = len(response.content)
            features['status_code'] = response.status_code
            features['num_redirects'] = len(response.history)
            
            # HTML structure analysis
            features['num_forms'] = len(soup.find_all('form'))
            features['num_input_fields'] = len(soup.find_all('input'))
            features['num_password_fields'] = len(soup.find_all('input', {'type': 'password'}))
            features['num_hidden_fields'] = len(soup.find_all('input', {'type': 'hidden'}))
            
            # Link analysis
            all_links = soup.find_all('a', href=True)
            features['num_links'] = len(all_links)
            features['external_links'] = self.count_external_links(all_links, url)
            
            # Image analysis
            images = soup.find_all('img')
            features['num_images'] = len(images)
            features['external_images'] = self.count_external_images(images, url)
            
            # JavaScript analysis
            scripts = soup.find_all('script')
            features['num_scripts'] = len(scripts)
            features['has_obfuscated_js'] = self.has_obfuscated_javascript(scripts)
            
            # Content quality analysis
            text_content = soup.get_text()
            features['text_length'] = len(text_content)
            features['readability_score'] = flesch_reading_ease(text_content) if text_content else 0
            
            # Security features
            features['has_ssl'] = 1 if url.startswith('https') else 0
            features['mixed_content'] = self.has_mixed_content(soup, url)
            
            # Suspicious indicators
            features['suspicious_title'] = self.has_suspicious_title(soup)
            features['copyright_year'] = self.get_copyright_year(soup)
            features['favicon_external'] = self.has_external_favicon(soup, url)
            
        except Exception as e:
            # Default values for failed analysis
            default_features = {
                'page_size': 0, 'status_code': 0, 'num_redirects': 0,
                'num_forms': 0, 'num_input_fields': 0, 'num_password_fields': 0,
                'num_hidden_fields': 0, 'num_links': 0, 'external_links': 0,
                'num_images': 0, 'external_images': 0, 'num_scripts': 0,
                'has_obfuscated_js': 0, 'text_length': 0, 'readability_score': 0,
                'has_ssl': 0, 'mixed_content': 0, 'suspicious_title': 0,
                'copyright_year': 0, 'favicon_external': 0
            }
            features.update(default_features)
        
        return features
    
    def count_external_links(self, links, base_url):
        """Count links pointing to external domains"""
        base_domain = tldextract.extract(base_url).registered_domain
        external_count = 0
        
        for link in links:
            href = link.get('href', '')
            if href.startswith('http'):
                link_domain = tldextract.extract(href).registered_domain
                if link_domain != base_domain:
                    external_count += 1
        
        return external_count
    
    def count_external_images(self, images, base_url):
        """Count images from external domains"""
        base_domain = tldextract.extract(base_url).registered_domain
        external_count = 0
        
        for img in images:
            src = img.get('src', '')
            if src.startswith('http'):
                img_domain = tldextract.extract(src).registered_domain
                if img_domain != base_domain:
                    external_count += 1
        
        return external_count
    
    def has_obfuscated_javascript(self, scripts):
        """Detect obfuscated JavaScript"""
        for script in scripts:
            script_text = script.get_text()
            if script_text:
                # Look for obfuscation patterns
                if (len(script_text) > 1000 and 
                    (script_text.count('eval') > 2 or 
                     script_text.count('unescape') > 1 or
                     len(re.findall(r'\\x[0-9a-fA-F]{2}', script_text)) > 10)):
                    return 1
        return 0
    
    def has_mixed_content(self, soup, url):
        """Check for mixed HTTP/HTTPS content"""
        if not url.startswith('https'):
            return 0
        
        # Check for HTTP resources in HTTPS page
        for tag in soup.find_all(['img', 'script', 'link', 'iframe']):
            src = tag.get('src') or tag.get('href')
            if src and src.startswith('http://'):
                return 1
        return 0
    
    def has_suspicious_title(self, soup):
        """Check for suspicious page titles"""
        title_tag = soup.find('title')
        if not title_tag:
            return 1  # No title is suspicious
        
        title = title_tag.get_text().lower()
        suspicious_words = [
            'login', 'signin', 'verify', 'update', 'suspended', 'limited',
            'security', 'alert', 'warning', 'urgent', 'immediate'
        ]
        
        return 1 if any(word in title for word in suspicious_words) else 0
    
    def get_copyright_year(self, soup):
        """Extract copyright year to check if site is up to date"""
        copyright_text = soup.get_text().lower()
        current_year = datetime.now().year
        
        # Look for copyright years
        years = re.findall(r'copyright.*?(\d{4})', copyright_text)
        if years:
            latest_year = max(int(year) for year in years)
            return current_year - latest_year  # Return age
        
        return 10  # Default to old if no copyright found
    
    def has_external_favicon(self, soup, base_url):
        """Check if favicon is hosted externally"""
        favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        if favicon:
            href = favicon.get('href', '')
            if href.startswith('http'):
                base_domain = tldextract.extract(base_url).registered_domain
                favicon_domain = tldextract.extract(href).registered_domain
                return 1 if favicon_domain != base_domain else 0
        return 0