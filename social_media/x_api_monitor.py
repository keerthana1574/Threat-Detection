import tweepy
import time
import threading
from datetime import datetime, timedelta
import os
import sys
import json
import requests
from collections import defaultdict, deque
import logging

# Add backend modules to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.append(backend_path)

class XAPIMonitor:
    def __init__(self, api_credentials, cyberbullying_detector=None, fake_news_detector=None):
        """
        Initialize X API Monitor with threat detectors

        Args:
            api_credentials: Dict with X API keys
            cyberbullying_detector: CyberbullyingDetector instance
            fake_news_detector: FakeNewsDetector instance
        """
        self.api_credentials = api_credentials
        self.cyberbullying_detector = cyberbullying_detector
        self.fake_news_detector = fake_news_detector

        # API clients
        self.api_v1 = None
        self.client_v2 = None

        # Monitoring state
        self.is_monitoring = False
        self.monitor_threads = {}

        # Detection results storage
        self.recent_detections = {
            'cyberbullying': deque(maxlen=100),
            'fake_news': deque(maxlen=100),
            'combined': deque(maxlen=200)
        }

        # Rate limiting
        self.rate_limits = {
            'search_tweets': {'remaining': 100, 'reset_time': None},
            'tweet_lookup': {'remaining': 900, 'reset_time': None}
        }

        # Monitoring configuration
        self.config = {
            'cyberbullying_keywords': [
                'hate', 'bully', 'harassment', 'threat', 'abuse',
                'suicide', 'kys', 'loser', 'stupid', 'worthless',
                'ugly', 'fat', 'disgusting', 'pathetic'
            ],
            'fake_news_keywords': [
                'breaking', 'urgent', 'exclusive', 'shocking',
                'hoax', 'conspiracy', 'fake news', 'misinformation',
                'covid', 'vaccine', 'election', 'conspiracy theory'
            ],
            'search_limit': 100,
            'monitoring_interval': 60  # seconds
        }

        # Setup API clients
        self.setup_api_clients()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_api_clients(self):
        """Setup Twitter API v1.1 and v2 clients"""
        try:
            # API v1.1 for advanced search and user context
            auth = tweepy.OAuthHandler(
                self.api_credentials.get('api_key', ''),
                self.api_credentials.get('api_secret', '')
            )
            auth.set_access_token(
                self.api_credentials.get('access_token', ''),
                self.api_credentials.get('access_secret', '')
            )

            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

            # API v2 for better tweet features
            bearer_token = self.api_credentials.get('bearer_token', '')
            if bearer_token:
                self.client_v2 = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True
                )

            # Test the connection
            try:
                if self.api_v1:
                    self.api_v1.verify_credentials()
                    self.logger.info("✅ X API v1.1 connected successfully")

                if self.client_v2:
                    me = self.client_v2.get_me()
                    self.logger.info("✅ X API v2 connected successfully")

            except Exception as e:
                self.logger.warning(f"⚠️ API connection test failed: {e}")

        except Exception as e:
            self.logger.error(f"❌ Failed to setup X API clients: {e}")

    def check_rate_limits(self):
        """Check current rate limit status"""
        try:
            if self.api_v1:
                rate_limit_status = self.api_v1.get_rate_limit_status()

                # Update search rate limits
                search_limits = rate_limit_status['resources']['search']['/search/tweets']
                self.rate_limits['search_tweets'] = {
                    'remaining': search_limits['remaining'],
                    'reset_time': datetime.fromtimestamp(search_limits['reset'])
                }

                # Update lookup rate limits
                lookup_limits = rate_limit_status['resources']['statuses']['/statuses/lookup']
                self.rate_limits['tweet_lookup'] = {
                    'remaining': lookup_limits['remaining'],
                    'reset_time': datetime.fromtimestamp(lookup_limits['reset'])
                }

                return self.rate_limits

        except Exception as e:
            self.logger.error(f"Error checking rate limits: {e}")
            return None

    def search_tweets(self, keywords, count=100, result_type='recent'):
        """Search for tweets containing specified keywords"""
        try:
            if not self.api_v1:
                return []

            # Build search query
            query = ' OR '.join(f'"{keyword}"' for keyword in keywords)
            query += ' -filter:retweets lang:en'  # Exclude retweets, English only

            tweets = []

            # Use Cursor for pagination
            for tweet in tweepy.Cursor(
                self.api_v1.search_tweets,
                q=query,
                result_type=result_type,
                lang='en',
                include_entities=True,
                tweet_mode='extended'
            ).items(count):

                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.full_text,
                    'user': {
                        'id': tweet.user.id,
                        'screen_name': tweet.user.screen_name,
                        'name': tweet.user.name,
                        'followers_count': tweet.user.followers_count,
                        'verified': tweet.user.verified,
                        'created_at': tweet.user.created_at.isoformat()
                    },
                    'created_at': tweet.created_at.isoformat(),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'reply_count': getattr(tweet, 'reply_count', 0),
                    'lang': tweet.lang,
                    'source': tweet.source,
                    'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                    'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                    'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])]
                }

                tweets.append(tweet_data)

            return tweets

        except Exception as e:
            self.logger.error(f"Error searching tweets: {e}")
            return []

    def analyze_tweet_for_cyberbullying(self, tweet_data):
        """Analyze a tweet for cyberbullying content"""
        try:
            if not self.cyberbullying_detector:
                return None

            text = tweet_data['text']
            result = self.cyberbullying_detector.predict_single(text)

            # Add tweet metadata to result
            analysis = {
                'tweet_id': tweet_data['id'],
                'tweet_text': text,
                'user_info': tweet_data['user'],
                'tweet_metrics': {
                    'retweet_count': tweet_data['retweet_count'],
                    'favorite_count': tweet_data['favorite_count'],
                    'reply_count': tweet_data['reply_count']
                },
                'detection_result': result,
                'timestamp': datetime.now().isoformat(),
                'threat_type': 'cyberbullying'
            }

            # Calculate risk level
            confidence = result.get('confidence', 0)
            if confidence > 0.8:
                analysis['risk_level'] = 'high'
            elif confidence > 0.6:
                analysis['risk_level'] = 'medium'
            else:
                analysis['risk_level'] = 'low'

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing tweet for cyberbullying: {e}")
            return None

    def analyze_tweet_for_fake_news(self, tweet_data):
        """Analyze a tweet for fake news content"""
        try:
            if not self.fake_news_detector:
                return None

            text = tweet_data['text']

            # Include URLs in analysis if present
            full_text = text
            if tweet_data['urls']:
                full_text += ' ' + ' '.join(tweet_data['urls'])

            result = self.fake_news_detector.predict_single(full_text)

            analysis = {
                'tweet_id': tweet_data['id'],
                'tweet_text': text,
                'user_info': tweet_data['user'],
                'tweet_metrics': {
                    'retweet_count': tweet_data['retweet_count'],
                    'favorite_count': tweet_data['favorite_count'],
                    'reply_count': tweet_data['reply_count']
                },
                'urls': tweet_data['urls'],
                'hashtags': tweet_data['hashtags'],
                'detection_result': result,
                'timestamp': datetime.now().isoformat(),
                'threat_type': 'fake_news'
            }

            # Calculate risk level
            confidence = result.get('confidence', 0)
            if confidence > 0.8:
                analysis['risk_level'] = 'high'
            elif confidence > 0.6:
                analysis['risk_level'] = 'medium'
            else:
                analysis['risk_level'] = 'low'

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing tweet for fake news: {e}")
            return None

    def start_cyberbullying_monitoring(self, keywords=None, interval=300):
        """Start monitoring for cyberbullying content"""
        if 'cyberbullying' in self.monitor_threads and self.monitor_threads['cyberbullying'].is_alive():
            return {'error': 'Cyberbullying monitoring already active'}

        keywords = keywords or self.config['cyberbullying_keywords']

        def monitor_loop():
            self.logger.info("🔍 Starting cyberbullying monitoring...")

            while self.is_monitoring:
                try:
                    # Search for tweets
                    tweets = self.search_tweets(
                        keywords,
                        count=self.config['search_limit']
                    )

                    self.logger.info(f"Found {len(tweets)} tweets to analyze for cyberbullying")

                    # Analyze each tweet
                    for tweet in tweets:
                        if not self.is_monitoring:
                            break

                        analysis = self.analyze_tweet_for_cyberbullying(tweet)

                        if analysis and analysis['detection_result'].get('is_cyberbullying', False):
                            # Store detection
                            self.recent_detections['cyberbullying'].append(analysis)
                            self.recent_detections['combined'].append(analysis)

                            self.logger.warning(
                                f"🚨 Cyberbullying detected: {tweet['id']} "
                                f"(confidence: {analysis['detection_result']['confidence']:.3f})"
                            )

                    # Wait before next check
                    if self.is_monitoring:
                        time.sleep(interval)

                except Exception as e:
                    self.logger.error(f"Error in cyberbullying monitoring: {e}")
                    time.sleep(60)  # Wait a minute on error

            self.logger.info("🔍 Cyberbullying monitoring stopped")

        # Start monitoring thread
        self.monitor_threads['cyberbullying'] = threading.Thread(target=monitor_loop)
        self.monitor_threads['cyberbullying'].daemon = True
        self.monitor_threads['cyberbullying'].start()

        return {
            'status': 'started',
            'type': 'cyberbullying',
            'keywords': keywords,
            'interval': interval
        }

    def start_fake_news_monitoring(self, keywords=None, interval=300):
        """Start monitoring for fake news content"""
        if 'fake_news' in self.monitor_threads and self.monitor_threads['fake_news'].is_alive():
            return {'error': 'Fake news monitoring already active'}

        keywords = keywords or self.config['fake_news_keywords']

        def monitor_loop():
            self.logger.info("🔍 Starting fake news monitoring...")

            while self.is_monitoring:
                try:
                    # Search for tweets
                    tweets = self.search_tweets(
                        keywords,
                        count=self.config['search_limit']
                    )

                    self.logger.info(f"Found {len(tweets)} tweets to analyze for fake news")

                    # Analyze each tweet
                    for tweet in tweets:
                        if not self.is_monitoring:
                            break

                        analysis = self.analyze_tweet_for_fake_news(tweet)

                        if analysis and analysis['detection_result'].get('is_fake', False):
                            # Store detection
                            self.recent_detections['fake_news'].append(analysis)
                            self.recent_detections['combined'].append(analysis)

                            self.logger.warning(
                                f"🚨 Fake news detected: {tweet['id']} "
                                f"(confidence: {analysis['detection_result']['confidence']:.3f})"
                            )

                    # Wait before next check
                    if self.is_monitoring:
                        time.sleep(interval)

                except Exception as e:
                    self.logger.error(f"Error in fake news monitoring: {e}")
                    time.sleep(60)

            self.logger.info("🔍 Fake news monitoring stopped")

        # Start monitoring thread
        self.monitor_threads['fake_news'] = threading.Thread(target=monitor_loop)
        self.monitor_threads['fake_news'].daemon = True
        self.monitor_threads['fake_news'].start()

        return {
            'status': 'started',
            'type': 'fake_news',
            'keywords': keywords,
            'interval': interval
        }

    def start_comprehensive_monitoring(self, interval=300):
        """Start monitoring for both cyberbullying and fake news"""
        self.is_monitoring = True

        results = {}

        # Start cyberbullying monitoring
        if self.cyberbullying_detector:
            results['cyberbullying'] = self.start_cyberbullying_monitoring(interval=interval)
        else:
            results['cyberbullying'] = {'error': 'Cyberbullying detector not available'}

        # Start fake news monitoring
        if self.fake_news_detector:
            results['fake_news'] = self.start_fake_news_monitoring(interval=interval)
        else:
            results['fake_news'] = {'error': 'Fake news detector not available'}

        return {
            'comprehensive_monitoring': True,
            'results': results,
            'rate_limits': self.check_rate_limits()
        }

    def stop_monitoring(self):
        """Stop all monitoring activities"""
        self.is_monitoring = False

        stopped_threads = []
        for name, thread in self.monitor_threads.items():
            if thread.is_alive():
                thread.join(timeout=5)  # Wait up to 5 seconds
                stopped_threads.append(name)

        self.monitor_threads.clear()

        return {
            'status': 'stopped',
            'stopped_threads': stopped_threads
        }

    def get_monitoring_status(self):
        """Get current monitoring status"""
        active_monitors = {}
        for name, thread in self.monitor_threads.items():
            active_monitors[name] = thread.is_alive()

        return {
            'is_monitoring': self.is_monitoring,
            'active_monitors': active_monitors,
            'recent_detections_count': {
                'cyberbullying': len(self.recent_detections['cyberbullying']),
                'fake_news': len(self.recent_detections['fake_news']),
                'total': len(self.recent_detections['combined'])
            },
            'rate_limits': self.check_rate_limits(),
            'configuration': self.config
        }

    def get_recent_detections(self, threat_type='all', limit=20):
        """Get recent threat detections"""
        if threat_type == 'all':
            detections = list(self.recent_detections['combined'])
        elif threat_type in self.recent_detections:
            detections = list(self.recent_detections[threat_type])
        else:
            return []

        # Sort by timestamp (most recent first)
        detections.sort(key=lambda x: x['timestamp'], reverse=True)

        return detections[:limit]

    def analyze_specific_tweet(self, tweet_id):
        """Analyze a specific tweet by ID"""
        try:
            if not self.api_v1:
                return {'error': 'API not available'}

            # Get tweet details
            tweet = self.api_v1.get_status(tweet_id, tweet_mode='extended')

            tweet_data = {
                'id': tweet.id,
                'text': tweet.full_text,
                'user': {
                    'id': tweet.user.id,
                    'screen_name': tweet.user.screen_name,
                    'name': tweet.user.name,
                    'followers_count': tweet.user.followers_count,
                    'verified': tweet.user.verified
                },
                'created_at': tweet.created_at.isoformat(),
                'retweet_count': tweet.retweet_count,
                'favorite_count': tweet.favorite_count,
                'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])]
            }

            # Analyze for both threats
            results = {
                'tweet_data': tweet_data,
                'analyses': {}
            }

            if self.cyberbullying_detector:
                cyberbullying_analysis = self.analyze_tweet_for_cyberbullying(tweet_data)
                if cyberbullying_analysis:
                    results['analyses']['cyberbullying'] = cyberbullying_analysis

            if self.fake_news_detector:
                fake_news_analysis = self.analyze_tweet_for_fake_news(tweet_data)
                if fake_news_analysis:
                    results['analyses']['fake_news'] = fake_news_analysis

            return results

        except Exception as e:
            return {'error': f'Failed to analyze tweet: {e}'}

    def export_detections(self, threat_type='all', format='json'):
        """Export recent detections to file"""
        detections = self.get_recent_detections(threat_type, limit=1000)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"threat_detections_{threat_type}_{timestamp}.{format}"

        try:
            if format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(detections, f, indent=2, ensure_ascii=False)
            elif format == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    if detections:
                        fieldnames = ['tweet_id', 'tweet_text', 'user_screen_name',
                                    'threat_type', 'risk_level', 'confidence', 'timestamp']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()

                        for detection in detections:
                            writer.writerow({
                                'tweet_id': detection['tweet_id'],
                                'tweet_text': detection['tweet_text'][:200],  # Truncate
                                'user_screen_name': detection['user_info']['screen_name'],
                                'threat_type': detection['threat_type'],
                                'risk_level': detection['risk_level'],
                                'confidence': detection['detection_result'].get('confidence', 0),
                                'timestamp': detection['timestamp']
                            })

            return {
                'success': True,
                'filename': filename,
                'count': len(detections)
            }

        except Exception as e:
            return {'error': f'Export failed: {e}'}

# Test function
def test_x_api_monitor():
    """Test the X API monitor"""
    print("Testing X API Monitor...")

    # Mock credentials (replace with real ones)
    credentials = {
        'api_key': 'your_api_key',
        'api_secret': 'your_api_secret',
        'access_token': 'your_access_token',
        'access_secret': 'your_access_secret',
        'bearer_token': 'your_bearer_token'
    }

    monitor = XAPIMonitor(credentials)

    # Test connection
    status = monitor.get_monitoring_status()
    print(f"Monitor status: {status}")

    return monitor

if __name__ == "__main__":
    test_x_api_monitor()