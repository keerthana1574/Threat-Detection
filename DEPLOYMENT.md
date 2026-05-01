# AI Cybersecurity Threat Detection System - Deployment Guide

## 🚀 Complete Multi-Domain Cybersecurity Solution

This comprehensive AI-powered cybersecurity threat detection system provides real-time monitoring and detection for:

- 🛡️ **Cyberbullying Detection** (Enhanced ML models)
- 📰 **Fake News Detection** (Multi-model ensemble)
- 🔗 **Phishing URL Detection** (Advanced pattern matching)
- 💉 **SQL Injection Detection** (Rule-based + ML)
- 🔴 **XSS Detection** (Pattern recognition)
- 🌐 **DDoS & Network Anomaly Detection** (Real-time monitoring)
- 🐦 **Social Media Monitoring** (X API integration)

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **Python**: 3.8+ (recommended 3.10)
- **Memory**: 8GB RAM minimum, 16GB+ recommended
- **Storage**: 10GB free space for models and data
- **Network**: Internet connection for X API and updates

### Required API Keys
- **X (Twitter) API**: For social media monitoring
  - API Key & Secret
  - Access Token & Secret
  - Bearer Token

## 🛠️ Installation Steps

### 1. Clone and Setup Environment

```bash
# Clone the repository
cd C:\Users\yesha\Desktop\threat_det

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create/update `.env` file with your credentials:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cybersecurity_db
POSTGRES_USER=cyber_admin
POSTGRES_PASSWORD=your_secure_password

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=cybersecurity_logs

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-very-long-secure-secret-key-here

# X (Twitter) API Keys - REQUIRED for social media monitoring
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Firebase Configuration (Optional - for advanced features)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
```

### 3. Install Additional Dependencies

```bash
# For network monitoring (may require admin/sudo)
pip install scapy python-nmap

# For advanced ML features
pip install tensorflow torch transformers

# For NLP processing
python -m nltk.downloader all
python -m spacy download en_core_web_sm
```

### 4. Verify Model Files

Ensure all model directories exist with trained models:

```
backend/models/
├── cyberbullying/
│   ├── naive_bayes_model.pkl
│   ├── logistic_regression_model.pkl
│   ├── random_forest_model.pkl
│   ├── sgd_logistic_model.pkl
│   ├── lstm_model.keras
│   ├── tfidf_vectorizer.pkl
│   └── tokenizer.pkl
├── fake_news/
│   ├── random_forest_model.pkl
│   ├── logistic_regression_model.pkl
│   ├── naive_bayes_model.pkl
│   ├── gradient_boosting_model.pkl
│   ├── xgboost_model.pkl
│   ├── hybrid_lstm_model.h5
│   └── tfidf_vectorizer.pkl
├── network_security/
│   ├── ddos_model.pkl
│   └── ddos_scaler.pkl
└── web_security/
    ├── sql_injection_model.pkl
    ├── xss_random_forest_model.pkl
    └── sql_tfidf_vectorizer.pkl
```

## 🚀 Running the System

### Development Mode

```bash
# Start the main application
python app.py
```

The system will start on `http://localhost:5000`

### Production Mode

```bash
# Using Gunicorn (Linux/macOS)
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Using Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Docker Deployment (Recommended)

```bash
# Build the container
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔧 Configuration Options

### Network Monitoring
```python
# In app.py or environment
NETWORK_INTERFACE = "eth0"  # Your network interface
DDOS_THRESHOLD = 1000       # Packets per second threshold
MONITOR_DURATION = 300      # Monitoring window in seconds
```

### Social Media Monitoring
```python
# Monitoring keywords (customizable)
CYBERBULLYING_KEYWORDS = ["hate", "bully", "harassment", "threat"]
FAKE_NEWS_KEYWORDS = ["breaking", "urgent", "hoax", "conspiracy"]
```

### ML Model Thresholds
```python
# Confidence thresholds for predictions
CYBERBULLYING_THRESHOLD = 0.7
FAKE_NEWS_THRESHOLD = 0.6
PHISHING_THRESHOLD = 0.8
SQL_INJECTION_THRESHOLD = 0.7
XSS_THRESHOLD = 0.75
```

## 📊 API Endpoints

### Core Detection APIs

#### Cyberbullying Detection
```bash
POST /api/cyberbullying/predict
{
  "text": "Text to analyze for cyberbullying"
}
```

#### Fake News Detection
```bash
POST /api/fake_news/predict
{
  "text": "News article or text to analyze"
}
```

#### Phishing Detection
```bash
POST /api/phishing/predict
{
  "url": "https://suspicious-url.com"
}
```

#### Web Security
```bash
POST /api/sql_injection/predict
{
  "text": "User input to check for SQL injection"
}

POST /api/xss/predict
{
  "text": "User input to check for XSS"
}
```

### Monitoring APIs

#### Social Media Monitoring
```bash
POST /api/realtime/social-media/start
POST /api/realtime/social-media/stop
```

#### System Status
```bash
GET /health
GET /api/metrics
GET /api/alerts
GET /api/threats
```

## 🧪 Testing the System

### Comprehensive Test Suite

```bash
# Run all tests
python test_comprehensive.py

# Test specific endpoint
python test_comprehensive.py http://localhost:5000
```

### Manual Testing

#### 1. Test Cyberbullying Detection
```bash
curl -X POST http://localhost:5000/api/cyberbullying/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "You are so stupid and worthless!"}'
```

#### 2. Test Phishing Detection
```bash
curl -X POST http://localhost:5000/api/phishing/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://g00gle.com"}'
```

#### 3. Test SQL Injection Detection
```bash
curl -X POST http://localhost:5000/api/sql_injection/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "'\'' OR '\''1'\''='\''1"}'
```

## 📱 Dashboard Access

### Web Dashboard
- URL: `http://localhost:5000/dashboard`
- Features:
  - Real-time threat monitoring
  - Interactive testing tools
  - System status overview
  - Live detection results
  - Performance analytics

### Mobile-Responsive Interface
The dashboard is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## 🔒 Security Considerations

### Network Security
- Run network monitoring with appropriate permissions
- Configure firewall rules for DDoS protection
- Monitor system resources for anomalies

### API Security
- Use HTTPS in production
- Implement rate limiting
- Add API authentication for sensitive endpoints
- Monitor for abuse patterns

### Data Privacy
- Encrypt sensitive data at rest
- Implement data retention policies
- Comply with GDPR/CCPA requirements
- Audit access logs regularly

## 📈 Performance Optimization

### Model Optimization
- Use GPU acceleration for ML models (if available)
- Implement model caching
- Batch predictions when possible
- Monitor memory usage

### System Optimization
```bash
# Increase file descriptors (Linux)
ulimit -n 65536

# Optimize Python garbage collection
export PYTHONOPTIMIZE=1

# Use faster JSON library
pip install ujson

# Enable Redis caching
pip install redis
```

### Database Optimization
- Index frequently queried fields
- Implement connection pooling
- Use read replicas for analytics
- Regular database maintenance

## 🚨 Monitoring & Alerting

### System Monitoring
- CPU and memory usage
- Network bandwidth
- Detection accuracy rates
- Response times

### Alert Configuration
```python
# Configure alert thresholds
ALERT_THRESHOLDS = {
    'high_threat_count': 50,      # Threats per hour
    'low_accuracy': 0.85,         # Below 85% accuracy
    'high_response_time': 5.0,    # Above 5 seconds
    'system_load': 0.90           # Above 90% system load
}
```

### Notification Channels
- Email notifications
- Slack/Discord webhooks
- SMS alerts (Twilio)
- Push notifications

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks
1. **Model Updates**: Retrain models monthly with new data
2. **Security Updates**: Apply security patches promptly
3. **Performance Review**: Analyze system metrics weekly
4. **Backup Verification**: Test backup restoration quarterly

### Model Retraining
```bash
# Retrain cyberbullying model
python backend/modules/cyberbullying/train.py

# Retrain fake news model
python backend/modules/fake_news/train.py

# Update threat intelligence
python scripts/update_threat_intel.py
```

### Log Management
```bash
# Rotate logs daily
0 0 * * * /usr/sbin/logrotate /etc/logrotate.conf

# Archive old logs
find logs/ -name "*.log" -mtime +30 -delete

# Monitor log sizes
du -sh logs/
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Models Not Loading
```bash
# Check model files exist
ls -la backend/models/*/

# Verify permissions
chmod -R 755 backend/models/

# Check error logs
tail -f logs/application.log
```

#### 2. X API Connection Issues
```bash
# Verify credentials
python -c "import os; print(os.getenv('TWITTER_API_KEY'))"

# Test API connection
python backend/modules/social_media/test_api.py
```

#### 3. Network Monitoring Permissions
```bash
# Linux: Add user to required groups
sudo usermod -a -G netdev $USER

# Windows: Run as administrator
# macOS: Use sudo for network monitoring
```

#### 4. High Memory Usage
```bash
# Monitor memory usage
htop
ps aux | grep python

# Optimize model loading
# Use model quantization
# Implement lazy loading
```

### Performance Issues

#### Slow Response Times
1. Check system resources
2. Optimize database queries
3. Implement caching
4. Scale horizontally

#### Low Detection Accuracy
1. Review training data quality
2. Retrain models with more data
3. Adjust confidence thresholds
4. Implement ensemble methods

## 📚 Additional Resources

### Documentation
- API Documentation: `/api/docs`
- Model Architecture: `docs/models.md`
- Security Guidelines: `docs/security.md`

### Support
- GitHub Issues: Report bugs and feature requests
- Community Forum: Get help from other users
- Email Support: For enterprise customers

### Training Materials
- Video Tutorials: System setup and configuration
- Webinars: Advanced threat detection techniques
- Best Practices: Security implementation guides

## 🎯 Success Metrics

### Key Performance Indicators (KPIs)
- **Detection Accuracy**: >90% for all modules
- **False Positive Rate**: <5%
- **Response Time**: <2 seconds average
- **System Uptime**: >99.5%
- **Threat Coverage**: All major attack vectors

### Monitoring Dashboard Metrics
- Threats detected per day
- Detection accuracy trends
- System performance metrics
- User engagement statistics

---

## 🎉 Congratulations!

Your AI Cybersecurity Threat Detection System is now ready for deployment!

**System Features:**
✅ Multi-domain threat detection (7+ threat types)
✅ Real-time social media monitoring
✅ Advanced ML models with ensemble predictions
✅ Interactive web dashboard
✅ Comprehensive API suite
✅ Production-ready deployment
✅ Extensive testing suite
✅ Monitoring and alerting
✅ Performance optimization

For questions or support, please refer to the documentation or contact the development team.

**Stay Secure! 🛡️**