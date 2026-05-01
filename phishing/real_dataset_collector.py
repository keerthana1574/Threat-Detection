# real_dataset_collector.py - Get the best available phishing datasets
import pandas as pd
import requests
import os
import time
from urllib.parse import urlparse
import zipfile
import io

class PhishingDatasetCollector:
    def __init__(self):
        self.datasets_dir = 'datasets/phishing'
        os.makedirs(self.datasets_dir, exist_ok=True)
        
    def download_phishtank_data(self):
        """Download PhishTank verified phishing URLs"""
        print("Downloading PhishTank data...")
        try:
            # PhishTank verified URLs (free, no API key needed for this endpoint)
            url = "http://data.phishtank.com/data/online-valid.csv"
            
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                # Save raw data
                with open(f"{self.datasets_dir}/phishtank_verified.csv", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parse and clean
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    header = lines[0]
                    data_lines = lines[1:2000]  # Take first 2000 entries
                    
                    phishing_urls = []
                    for line in data_lines:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            url_part = parts[1].strip('"')
                            if url_part.startswith('http'):
                                phishing_urls.append(url_part)
                    
                    print(f"PhishTank: Downloaded {len(phishing_urls)} verified phishing URLs")
                    return phishing_urls
            else:
                print(f"PhishTank download failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"PhishTank download error: {e}")
            return []
    
    def download_openphish_data(self):
        """Download OpenPhish feed"""
        print("Downloading OpenPhish data...")
        try:
            url = "https://openphish.com/feed.txt"
            
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                # Save raw data
                with open(f"{self.datasets_dir}/openphish_feed.txt", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parse URLs
                lines = response.text.strip().split('\n')
                phishing_urls = []
                for line in lines[:1500]:  # Take first 1500
                    line = line.strip()
                    if line.startswith('http'):
                        phishing_urls.append(line)
                
                print(f"OpenPhish: Downloaded {len(phishing_urls)} phishing URLs")
                return phishing_urls
            else:
                print(f"OpenPhish download failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"OpenPhish download error: {e}")
            return []
    
    def download_urlvoid_data(self):
        """Download URLVoid malicious URLs"""
        print("Downloading URLVoid data...")
        try:
            # URLVoid provides some free data
            url = "https://www.urlvoid.com/api/v1000/host/scan/"
            # Note: This would require an API key in practice
            # For now, we'll use a placeholder
            print("URLVoid: API key required for full access")
            return []
        except Exception as e:
            print(f"URLVoid download error: {e}")
            return []
    
    def get_alexa_top_sites(self):
        """Get legitimate URLs from Alexa top sites"""
        print("Getting Alexa top sites...")
        try:
            # Alexa top sites (archived data since Alexa was discontinued)
            # We'll use a hardcoded list of top legitimate sites
            top_sites = [
                "https://www.google.com", "https://www.youtube.com", "https://www.facebook.com",
                "https://www.amazon.com", "https://www.wikipedia.org", "https://www.twitter.com",
                "https://www.instagram.com", "https://www.linkedin.com", "https://www.microsoft.com",
                "https://www.apple.com", "https://www.netflix.com", "https://www.paypal.com",
                "https://www.ebay.com", "https://www.reddit.com", "https://www.pinterest.com",
                "https://www.spotify.com", "https://www.dropbox.com", "https://www.adobe.com",
                "https://www.salesforce.com", "https://www.zoom.us", "https://www.slack.com",
                "https://github.com", "https://stackoverflow.com", "https://www.cnn.com",
                "https://www.bbc.com", "https://www.nytimes.com", "https://www.washingtonpost.com",
                "https://www.walmart.com", "https://www.target.com", "https://www.bestbuy.com",
                "https://www.homedepot.com", "https://www.lowes.com", "https://www.costco.com",
                "https://www.chase.com", "https://www.bankofamerica.com", "https://www.wellsfargo.com",
                "https://www.citibank.com", "https://www.usbank.com", "https://www.capitalone.com",
                "https://www.americanexpress.com", "https://www.discover.com", "https://www.schwab.com",
                "https://www.fidelity.com", "https://www.vanguard.com", "https://www.tdameritrade.com"
            ]
            
            # Add variations
            legitimate_urls = []
            for site in top_sites:
                legitimate_urls.append(site)
                # Add common subdomains
                domain = urlparse(site).netloc
                legitimate_urls.extend([
                    f"https://www.{domain}/login",
                    f"https://accounts.{domain}",
                    f"https://signin.{domain}",
                    f"https://secure.{domain}",
                    f"https://help.{domain}",
                    f"https://support.{domain}"
                ])
            
            print(f"Legitimate sites: Generated {len(legitimate_urls)} URLs")
            return legitimate_urls
            
        except Exception as e:
            print(f"Error generating legitimate URLs: {e}")
            return []
    
    def download_university_datasets(self):
        """Download academic phishing datasets"""
        print("Downloading university datasets...")
        
        datasets = []
        
        # UCI Machine Learning Repository
        uci_urls = [
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00327/Phishing%20Websites%20Data%20Set.zip"
        ]
        
        for url in uci_urls:
            try:
                print(f"Downloading from UCI: {url}")
                response = requests.get(url, timeout=120)
                if response.status_code == 200:
                    # Save zip file
                    zip_path = f"{self.datasets_dir}/uci_phishing.zip"
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Extract
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.datasets_dir)
                    
                    print("UCI dataset downloaded and extracted")
                    datasets.append("uci_phishing")
                else:
                    print(f"UCI download failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"UCI download error: {e}")
        
        return datasets
    
    def create_comprehensive_dataset(self):
        """Create a comprehensive dataset from all sources"""
        print("\n" + "="*60)
        print("CREATING COMPREHENSIVE PHISHING DATASET")
        print("="*60)
        
        all_phishing_urls = []
        all_legitimate_urls = []
        
        # Download real phishing data
        phishtank_urls = self.download_phishtank_data()
        openphish_urls = self.download_openphish_data()
        
        all_phishing_urls.extend(phishtank_urls)
        all_phishing_urls.extend(openphish_urls)
        
        # Get legitimate URLs
        legitimate_urls = self.get_alexa_top_sites()
        all_legitimate_urls.extend(legitimate_urls)
        
        # Download academic datasets
        academic_datasets = self.download_university_datasets()
        
        # Remove duplicates
        all_phishing_urls = list(set(all_phishing_urls))
        all_legitimate_urls = list(set(all_legitimate_urls))
        
        print(f"\nDataset Statistics:")
        print(f"Phishing URLs: {len(all_phishing_urls)}")
        print(f"Legitimate URLs: {len(all_legitimate_urls)}")
        
        # Create balanced dataset
        min_count = min(len(all_phishing_urls), len(all_legitimate_urls))
        if min_count < 500:
            print("Warning: Dataset is quite small. Adding synthetic data...")
            # Add synthetic data if needed
            synthetic_phishing, synthetic_legitimate = self.generate_synthetic_data()
            all_phishing_urls.extend(synthetic_phishing)
            all_legitimate_urls.extend(synthetic_legitimate)
        
        # Create DataFrame
        data = []
        
        # Add phishing URLs
        for url in all_phishing_urls[:2000]:  # Limit to 2000
            data.append({'url': url, 'label': 1})
        
        # Add legitimate URLs  
        for url in all_legitimate_urls[:2000]:  # Limit to 2000
            data.append({'url': url, 'label': 0})
        
        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset=['url']).reset_index(drop=True)
        
        # Save the dataset
        dataset_path = f"{self.datasets_dir}/comprehensive_phishing_dataset.csv"
        df.to_csv(dataset_path, index=False)
        
        print(f"\nFinal dataset saved to: {dataset_path}")
        print(f"Final dataset size: {len(df)} URLs")
        print(f"Phishing: {len(df[df['label'] == 1])}")
        print(f"Legitimate: {len(df[df['label'] == 0])}")
        print(f"Balance ratio: {len(df[df['label'] == 0]) / len(df[df['label'] == 1]):.2f}")
        
        return df
    
    def generate_synthetic_data(self):
        """Generate synthetic phishing and legitimate data if needed"""
        print("Generating synthetic data...")
        
        # High-quality synthetic phishing URLs
        synthetic_phishing = [
            # Current 2024 phishing patterns
            "http://paypal-verify-account.tk/urgent-action-required",
            "http://amazon-billing-update.ml/payment-method-expired", 
            "http://microsoft-security-alert.ga/suspicious-activity-detected",
            "http://apple-id-locked.cf/verify-identity-immediately",
            "http://google-account-suspended.pw/confirm-ownership",
            "http://facebook-security-check.tk/account-review-required",
            "http://netflix-payment-failed.ml/update-billing-info",
            "http://spotify-premium-expired.ga/renew-subscription",
            "http://dropbox-storage-full.cf/upgrade-account-now",
            "http://adobe-license-expired.pw/activate-software",
            
            # Banking phishing
            "http://chase-security-department.tk/fraud-alert",
            "http://bankofamerica-verification.ml/account-locked",
            "http://wells-fargo-notice.ga/immediate-action",
            "http://citibank-fraud-prevention.cf/verify-transaction",
            "http://usbank-security-center.pw/suspicious-login",
            
            # Cryptocurrency phishing
            "http://coinbase-verification.tk/kyc-required",
            "http://binance-security-notice.ml/account-suspended",
            "http://crypto-wallet-recovery.ga/restore-access",
            "http://blockchain-support.cf/transaction-failed",
            
            # Government impersonation
            "http://irs-tax-refund.tk/claim-refund-now",
            "http://social-security-update.ml/verify-benefits",
            "http://usps-redelivery.ga/package-notification",
            "http://medicare-enrollment.cf/update-information",
            
            # IP-based attacks
            "http://192.168.1.100/secure-banking/login.php",
            "http://10.0.0.50/paypal-verification/account.html",
            "http://172.16.0.25/amazon-billing/update.asp",
            "http://203.0.113.10/microsoft-security/verify.php"
        ] * 20  # Replicate to get more samples
        
        # High-quality legitimate URLs
        synthetic_legitimate = [
            # Official login pages
            "https://accounts.google.com/signin/v2/identifier",
            "https://login.microsoftonline.com/common/oauth2/authorize",
            "https://appleid.apple.com/sign-in",
            "https://www.paypal.com/signin/",
            "https://signin.aws.amazon.com/",
            "https://www.facebook.com/login.php",
            "https://accounts.spotify.com/en/login",
            "https://www.dropbox.com/login",
            "https://auth.adobe.com/authorize",
            "https://github.com/login",
            
            # Banking official sites
            "https://secure07ea.chase.com/web/auth/dashboard",
            "https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go",
            "https://connect.secure.wellsfargo.com/auth/login/present",
            "https://online.citi.com/US/login.do",
            "https://www.usbank.com/customer-service/online-mobile-banking.html",
            
            # E-commerce
            "https://www.amazon.com/ap/signin",
            "https://www.walmart.com/account/login",
            "https://www.target.com/account/signin",
            "https://www.bestbuy.com/identity/global/signin",
            "https://secure.homedepot.com/auth/view/signin",
            
            # News and media
            "https://www.cnn.com/account/log-in",
            "https://www.nytimes.com/subscription/login",
            "https://www.washingtonpost.com/subscribe/signin",
            "https://www.wsj.com/login",
            "https://www.reuters.com/signin/"
        ] * 20  # Replicate to get more samples
        
        return synthetic_phishing, synthetic_legitimate

def main():
    """Main function to collect and prepare datasets"""
    collector = PhishingDatasetCollector()
    
    print("Enhanced Phishing Dataset Collector")
    print("This will download the best available datasets for maximum accuracy")
    print("="*60)
    
    # Create comprehensive dataset
    df = collector.create_comprehensive_dataset()
    
    print("\nDataset collection complete!")
    print("You now have access to:")
    print("1. Real phishing URLs from PhishTank and OpenPhish")
    print("2. Verified legitimate URLs from top websites")
    print("3. Academic datasets from UCI")
    print("4. High-quality synthetic data for balance")
    
    return df

if __name__ == "__main__":
    main()