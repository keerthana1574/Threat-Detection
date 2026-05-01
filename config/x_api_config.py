import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

class XAPIConfig:
    def __init__(self):
        self.api_key = os.getenv('eVdTmPJpLe2trEcBWnjzMbZBR')
        self.api_secret = os.getenv('zrUSGC5nDIHPIMqwk5zbyao1Ta9iJqaXNQPYgom95jCotlCcDo')
        self.access_token = os.getenv('1759606899732025344-eN5igcpmBCrcBUtjqHi5ZXf73sFSp6')
        self.access_token_secret = os.getenv('K6C0dPe87V3ivYS12FXxaRSCJRot1gh0QAijK8qIt5TVc')
        self.bearer_token = os.getenv('AAAAAAAAAAAAAAAAAAAAAL%2BN3gEAAAAAsZFH09MvFghorHlnRBImW2p68mQ%3DAFHw0R1I9qwcq5nzaHLqH8wZfVN7M8kyR8zxkMYMpePEoDBsGD')
        
        # Initialize API v2 client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
    
    def get_client(self):
        return self.client

# Global X API instance
x_api = XAPIConfig()