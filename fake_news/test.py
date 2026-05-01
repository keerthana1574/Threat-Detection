from detector import FakeNewsDetector, NewsArticleAnalyzer
import json

def test_fake_news_detector():
    """Test the fake news detector with sample texts"""
    
    # Initialize detector
    model_dir = 'backend/models/fake_news'
    detector = FakeNewsDetector(model_dir)
    
    # Sample texts for testing
    test_texts = [
        # Likely fake news
        "BREAKING: Scientists discover that drinking water actually makes you MORE dehydrated! Doctors don't want you to know this shocking truth!",
        
        # Likely real news
        "The Federal Reserve announced today that it will maintain current interest rates while monitoring economic indicators for signs of inflation.",
        
        # Ambiguous/clickbait
        "You won't believe what this celebrity said about climate change! The response is incredible!",
        
        # Real-sounding fake
        "Recent studies from Harvard Medical School show that eating chocolate for breakfast increases productivity by 300% according to leading researchers."
    ]
    
    print("Testing Fake News Detection System")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Text: {text[:100]}...")
        
        result = detector.predict_single(text)
        
        print(f"Prediction: {'FAKE' if result['is_fake'] else 'REAL'}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Ensemble Probability: {result['ensemble_probability']:.3f}")
        
        # Show individual model predictions
        print("Individual Model Predictions:")
        for model, prob in result['individual_predictions'].items():
            print(f"  {model}: {prob:.3f}")
    
    # Test article analysis
    print("\n" + "=" * 50)
    print("Testing Article Analysis")
    print("=" * 50)
    
    analyzer = NewsArticleAnalyzer(detector)
    
    # Test with a sample news URL (replace with actual URL)
    test_url = "https://www.reuters.com/world/"  # Example URL
    
    try:
        article_result = analyzer.analyze_article(test_url)
        print(f"Article Analysis Result:")
        print(json.dumps(article_result, indent=2))
    except Exception as e:
        print(f"Error analyzing article: {e}")

def run_performance_test():
    """Test performance with multiple predictions"""
    import time
    
    detector = FakeNewsDetector('backend/models/fake_news')
    
    test_texts = [
        "This is a sample news text for performance testing." * 10
    ] * 100  # 100 test texts
    
    print(f"\nPerformance Test: Analyzing {len(test_texts)} texts...")
    
    start_time = time.time()
    results = detector.predict_batch(test_texts)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / len(test_texts)
    
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per prediction: {avg_time:.4f} seconds")
    print(f"Predictions per second: {1/avg_time:.2f}")

if __name__ == "__main__":
    test_fake_news_detector()
    run_performance_test()