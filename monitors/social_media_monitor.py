import tweepy
import time
import json
import threading
from datetime import datetime
from config.x_api_config import x_api
from config.database import db_manager
from modules.cyberbullying.cyberbullying_detector import CyberbullyingDetector # pyright: ignore[reportMissingImports]
from modules.fake_news.fake_news_detector import FakeNewsDetector
from utils.alert_system import AlertSystem
import logging

class SocialMediaMonitor:
    def __init__(self):
        self.client = x_api.get_client()
        self.cyberbullying_detector = CyberbullyingDetector()
        self.fake_news_detector = FakeNewsDetector()
        self.alert_system = AlertSystem()
        self.is_monitoring = False
        self.request_count = 0
        self.max_requests = 100  # X API limit
        
    def start_monitoring(self, keywords=None, users_to_monitor=None):
        """Start real-time social media monitoring"""
        if self.is_monitoring:
            return {"error": "Monitoring already active"}
        
        self.is_monitoring = True
        
        # Default keywords for cyberbullying and fake news
        if not keywords:
            keywords = [
                'breaking news', 'urgent', 'conspiracy', 
                'hate', 'stupid', 'idiot', 'kill yourself',
                'fake', 'hoax', 'scam'
            ]
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(
            target=self._monitor_posts,
            args=(keywords, users_to_monitor)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return {"success": "Social media monitoring started"}
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        return {"success": "Social media monitoring stopped"}
    
    def _monitor_posts(self, keywords, users_to_monitor):
        """Monitor posts for threats"""
        while self.is_monitoring and self.request_count < self.max_requests:
            try:
                # Search recent tweets
                for keyword in keywords:
                    if not self.is_monitoring:
                        break
                    
                    tweets = self.client.search_recent_tweets(
                        query=f"{keyword} -is:retweet lang:en",
                        max_results=10,
                        tweet_fields=['created_at', 'author_id', 'public_metrics']
                    )
                    
                    self.request_count += 1
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            self._analyze_tweet(tweet)
                    
                    # Rate limiting
                    time.sleep(2)
                
                # Check user timelines if specified
                if users_to_monitor:
                    for user_id in users_to_monitor:
                        if not self.is_monitoring:
                            break
                        
                        tweets = self.client.get_users_tweets(
                            id=user_id,
                            max_results=5,
                            tweet_fields=['created_at', 'public_metrics']
                        )
                        
                        self.request_count += 1
                        
                        if tweets.data:
                            for tweet in tweets.data:
                                self._analyze_tweet(tweet)
                        
                        time.sleep(2)
                
                # Wait before next monitoring cycle
                time.sleep(30)
                
            except Exception as e:
                logging.error(f"Social media monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _analyze_tweet(self, tweet):
        """Analyze individual tweet for threats"""
        try:
            tweet_text = tweet.text
            tweet_id = tweet.id
            author_id = tweet.author_id
            created_at = tweet.created_at
            
            # Cyberbullying Detection
            cyberbullying_result = self.cyberbullying_detector.predict(tweet_text)
            
            if cyberbullying_result['prediction']:
                self._log_threat(
                    threat_type='cyberbullying',
                    content=tweet_text,
                    source=f'twitter_user_{author_id}',
                    confidence=cyberbullying_result['confidence'],
                    metadata={
                        'tweet_id': tweet_id,
                        'author_id': author_id,
                        'created_at': str(created_at)
                    }
                )
                
                # Send alert
                self.alert_system.send_alert(
                    alert_type='cyberbullying',
                    message=f'Cyberbullying detected in tweet: {tweet_text[:100]}...',
                    severity='high' if cyberbullying_result['confidence'] > 0.8 else 'medium'
                )
            
            # Fake News Detection
            fake_news_result = self.fake_news_detector.predict(tweet_text)
            
            if fake_news_result['prediction']:
                self._log_threat(
                    threat_type='fake_news',
                    content=tweet_text,
                    source=f'twitter_user_{author_id}',
                    confidence=fake_news_result['confidence'],
                    metadata={
                        'tweet_id': tweet_id,
                        'author_id': author_id,
                        'created_at': str(created_at)
                    }
                )
                
                # Send alert
                self.alert_system.send_alert(
                    alert_type='fake_news',
                    message=f'Fake news detected in tweet: {tweet_text[:100]}...',
                    severity='high' if fake_news_result['confidence'] > 0.8 else 'medium'
                )
            
            # Log to MongoDB
            mongo_collection = db_manager.get_mongo_collection('social_media_data')
            mongo_collection.insert_one({
                'tweet_id': tweet_id,
                'author_id': author_id,
                'text': tweet_text,
                'created_at': str(created_at),
                'cyberbullying_score': cyberbullying_result['confidence'],
                'fake_news_score': fake_news_result['confidence'],
                'processed_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            logging.error(f"Tweet analysis error: {e}")
    
    def _log_threat(self, threat_type, content, source, confidence, metadata):
        """Log threat to database"""
        try:
            cursor = db_manager.get_postgres_cursor()
            cursor.execute("""
                INSERT INTO threat_logs (threat_type, description, source_ip, severity)
                VALUES (%s, %s, %s, %s)
            """, (
                threat_type,
                f"{content[:200]}...",
                source,
                'high' if confidence > 0.8 else 'medium'
            ))
            
            # Log detection result
            cursor.execute("""
                INSERT INTO detection_results (module_name, input_data, prediction, confidence_score)
                VALUES (%s, %s, %s, %s)
            """, (threat_type, content[:500], True, confidence))
            
        except Exception as e:
            logging.error(f"Database logging error: {e}")
    
    def get_monitoring_status(self):
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'request_count': self.request_count,
            'max_requests': self.max_requests,
            'remaining_requests': self.max_requests - self.request_count
        }

# Global social media monitor instance
social_media_monitor = SocialMediaMonitor()