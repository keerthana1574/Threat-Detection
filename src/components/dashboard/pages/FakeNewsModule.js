import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Icon Components
const NewspaperIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
  </svg>
);

const PlayIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const RssIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z" />
  </svg>
);

const MagnifyingGlassIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const ExclamationTriangleIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

function FakeNewsModule() {
  const [inputText, setInputText] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newsHeadlines, setNewsHeadlines] = useState([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('analyze');
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    fake: 0,
    verified: 0,
    percentage: 0
  });

  const handleTextAnalysis = async () => {
    if (!inputText.trim()) {
      alert('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setPrediction(null);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/fake_news/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      console.log('API Response:', data);
      setPrediction(data);
      
    } catch (error) {
      console.error('Error analyzing text:', error);
      setError(error.message || 'Failed to analyze text');
      alert('Error analyzing text: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestNews = async () => {
    setLoadingNews(true);
    setError(null);
    
    try {
      const response = await fetch(
        'http://localhost:5000/api/fake_news/news/headlines?country=us&page_size=10',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch headlines');
      }

      if (data.success && data.articles) {
        setNewsHeadlines(data.articles);
        setStats({
          total: data.total_articles,
          fake: data.fake_news_detected,
          verified: data.verified_articles,
          percentage: data.fake_news_percentage
        });
      }
      
    } catch (error) {
      console.error('Error fetching news:', error);
      setError(error.message || 'Failed to load headlines');
      alert('Error fetching news: ' + error.message);
    } finally {
      setLoadingNews(false);
    }
  };

  const searchNews = async () => {
    if (!searchQuery.trim()) {
      alert('Please enter a search query');
      return;
    }

    setLoadingNews(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:5000/api/fake_news/news/search?query=${encodeURIComponent(searchQuery)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Search failed');
      }

      if (data.success && data.articles) {
        setNewsHeadlines(data.articles);
        setStats({
          total: data.total_articles,
          fake: data.fake_news_detected,
          verified: data.verified_articles,
          percentage: data.fake_news_percentage
        });
      } else {
        setNewsHeadlines([]);
        setError(data.message || 'No results found');
      }
      
    } catch (error) {
      console.error('Error searching news:', error);
      setError(error.message || 'Failed to search news');
      setNewsHeadlines([]);
      alert('Error searching news: ' + error.message);
    } finally {
      setLoadingNews(false);
    }
  };

  const handleArticleClick = (article) => {
    if (article.url && article.url !== '#') {
      window.open(article.url, '_blank', 'noopener,noreferrer');
    } else {
      console.error('No URL available for this article');
    }
  };

  useEffect(() => {
    if (activeTab === 'monitor') {
      fetchLatestNews();
    }
  }, [activeTab]);

  const getVerdictStyle = (verdict) => {
    switch (verdict) {
      case 'verified':
      case 'likely_true':
        return {
          bg: 'bg-green-500/10',
          border: 'border-green-500/50',
          text: 'text-green-400',
          label: 'Found in News'
        };
      case 'false':
      case 'likely_false':
        return {
          bg: 'bg-red-500/10',
          border: 'border-red-500/50',
          text: 'text-red-400',
          label: 'Suspicious'
        };
      case 'opinion':
        return {
          bg: 'bg-blue-500/10',
          border: 'border-blue-500/50',
          text: 'text-blue-400',
          label: 'Opinion'
        };
      default:
        return {
          bg: 'bg-yellow-500/10',
          border: 'border-yellow-500/50',
          text: 'text-yellow-400',
          label: 'Unverified'
        };
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6"
    >
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-orange-500/20 rounded-lg">
            <NewspaperIcon className="h-8 w-8 text-orange-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Fake News Detection</h1>
            <p className="text-gray-400">Analyze news articles and monitor latest headlines</p>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
          <div className="flex bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all flex items-center justify-center ${
                activeTab === 'analyze'
                  ? 'bg-orange-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
              Text Analysis
            </button>
            <button
              onClick={() => setActiveTab('monitor')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all flex items-center justify-center ${
                activeTab === 'monitor'
                  ? 'bg-orange-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <RssIcon className="h-4 w-4 mr-2" />
              News Monitor
            </button>
          </div>
        </div>

        {/* Content Area */}
        {activeTab === 'analyze' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Section */}
            <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Text Analysis</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Enter news content to analyze:
                  </label>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Paste the news article or content you want to analyze..."
                    className="w-full h-40 p-4 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 resize-none"
                  />
                </div>
                
                <button
                  onClick={handleTextAnalysis}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white py-3 px-4 rounded-lg font-medium hover:from-orange-600 hover:to-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Analyzing with AI...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Analyze Text
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results Section - NO STATUS BANNER */}
            <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Analysis Results</h3>
              
              {prediction ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-4"
                >
                  {/* Claim Analysis */}
                  {prediction.claim_analysis && (
                    <div className="bg-gray-700/50 rounded-lg p-4">
                      <h5 className="font-medium text-white mb-3 flex items-center">
                        <span className="mr-2">🔍</span> Claim Analysis
                      </h5>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {prediction.claim_analysis.type && (
                          <div>
                            <span className="text-gray-400">Type:</span>
                            <span className="ml-2 text-white capitalize">
                              {prediction.claim_analysis.type}
                            </span>
                          </div>
                        )}
                        {prediction.claim_analysis.entities && prediction.claim_analysis.entities.length > 0 && (
                          <div>
                            <span className="text-gray-400">Entities:</span>
                            <span className="ml-2 text-white">
                              {prediction.claim_analysis.entities.join(', ')}
                            </span>
                          </div>
                        )}
                        {prediction.claim_analysis.has_negation !== undefined && (
                          <div>
                            <span className="text-gray-400">Negation:</span>
                            <span className={`ml-2 ${prediction.claim_analysis.has_negation ? 'text-yellow-400' : 'text-green-400'}`}>
                              {prediction.claim_analysis.has_negation ? 'Yes' : 'No'}
                            </span>
                          </div>
                        )}
                        {prediction.claim_analysis.sentiment && (
                          <div>
                            <span className="text-gray-400">Sentiment:</span>
                            <span className="ml-2 text-white capitalize">
                              {prediction.claim_analysis.sentiment}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Related News Articles */}
                  {prediction.fact_check && prediction.fact_check.sources && prediction.fact_check.sources.length > 0 && (
                    <div className="bg-gray-700/50 rounded-lg p-4">
                      <h5 className="font-medium text-white mb-3 flex items-center">
                        <span className="mr-2">📰</span> Related News Articles ({prediction.fact_check.sources.length})
                      </h5>
                      <p className="text-xs text-gray-400 mb-3">
                        Articles with similar content found in news sources
                      </p>
                      <div className="space-y-2 max-h-80 overflow-y-auto">
                        {prediction.fact_check.sources.slice(0, 7).map((source, idx) => (
                          <div key={idx} className="bg-gray-800 rounded p-3 hover:bg-gray-750 transition-colors">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1">
                                <p className="text-sm text-white font-medium mb-1 line-clamp-2">
                                  {source.title}
                                </p>
                                <div className="flex items-center gap-2 text-xs">
                                  <span className="text-blue-400">{source.source}</span>
                                  <span className="text-gray-500">•</span>
                                  <span className="text-gray-500">
                                    Similarity: {(source.relevance * 100).toFixed(0)}%
                                  </span>
                                </div>
                              </div>
                              {source.url && (
                                <button
                                  onClick={() => window.open(source.url, '_blank')}
                                  className="text-orange-400 hover:text-orange-300 text-xs whitespace-nowrap"
                                >
                                  View →
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Content Match Score */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Content Match Score</span>
                      <span className={`font-medium ${
                        prediction.confidence > 0.7 ? 'text-green-400' :
                        prediction.confidence > 0.4 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-3 relative overflow-hidden">
                      <div
                        className="h-3 rounded-full transition-all duration-1000"
                        style={{ 
                          width: `${prediction.confidence * 100}%`,
                          background: prediction.confidence > 0.7
                            ? 'linear-gradient(90deg, #10b981, #34d399)'
                            : prediction.confidence > 0.4
                            ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
                            : 'linear-gradient(90deg, #dc2626, #ef4444)'
                        }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Based on similarity to {prediction.fact_check?.sources?.length || 0} news articles
                    </p>
                  </div>

                  {/* Analysis Method Badge */}
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex gap-2">
                      {prediction.enhanced && (
                        <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded">
                          ✓ AI Analysis v2.0
                        </span>
                      )}
                      {prediction.claim_analysis && (
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                          ✓ NLP Analysis
                        </span>
                      )}
                      {prediction.fact_check && prediction.fact_check.sources && prediction.fact_check.sources.length > 0 && (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded">
                          ✓ {prediction.fact_check.sources.length} Sources
                        </span>
                      )}
                    </div>
                    <span className="text-gray-500">
                      {new Date(prediction.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  {/* Disclaimer */}
                  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                    <p className="text-xs text-blue-300">
                      <strong>Note:</strong> This tool compares your text against news sources using AI similarity matching. 
                      It does not independently verify facts. Always verify important information through multiple credible sources.
                    </p>
                  </div>
                </motion.div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <NewspaperIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Enter content and click "Analyze" to see results</p>
                    <p className="text-sm mt-2">Enhanced v2.0 with AI-powered analysis</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* News Monitor Tab */
          <div className="space-y-6">
            {/* Search Bar */}
            <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchNews()}
                  placeholder="Search news topics (e.g., 'climate change', 'technology', 'health')"
                  className="flex-1 p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <button
                  onClick={searchNews}
                  disabled={loadingNews}
                  className="bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 transition-all disabled:opacity-50 flex items-center"
                >
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                  Search
                </button>
                <button
                  onClick={fetchLatestNews}
                  disabled={loadingNews}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center"
                >
                  <RssIcon className="h-5 w-5 mr-2" />
                  Latest
                </button>
              </div>
            </div>

            {/* Statistics */}
            {stats.total > 0 && (
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-lg p-4 text-center">
                  <h4 className="text-2xl font-bold text-white">{stats.total}</h4>
                  <p className="text-gray-400 text-sm">Total Articles</p>
                </div>
                <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 text-center">
                  <h4 className="text-2xl font-bold text-green-400">{stats.verified}</h4>
                  <p className="text-gray-400 text-sm">Found in News</p>
                </div>
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-center">
                  <h4 className="text-2xl font-bold text-red-400">{stats.fake}</h4>
                  <p className="text-gray-400 text-sm">Suspicious</p>
                </div>
                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 text-center">
                  <h4 className="text-2xl font-bold text-blue-400">{stats.percentage.toFixed(1)}%</h4>
                  <p className="text-gray-400 text-sm">Flagged Rate</p>
                </div>
              </div>
            )}

            {/* News Headlines */}
            <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                {loadingNews ? 'Analyzing News...' : `News Headlines (${newsHeadlines.length})`}
              </h3>
              
              {loadingNews ? (
                <div className="flex flex-col items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mb-4"></div>
                  <p className="text-gray-400">Fetching and analyzing articles...</p>
                </div>
              ) : error ? (
                <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
                  <p className="text-red-400">{error}</p>
                  <button
                    onClick={fetchLatestNews}
                    className="mt-4 text-orange-400 hover:text-orange-300 text-sm"
                  >
                    Try again →
                  </button>
                </div>
              ) : newsHeadlines.length > 0 ? (
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                  {newsHeadlines.map((article, index) => {
                    const verdictStyle = getVerdictStyle(article.verdict);
                    
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`p-4 rounded-lg border-2 ${verdictStyle.bg} ${verdictStyle.border}`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${verdictStyle.text}`}>
                                {verdictStyle.label}
                              </span>
                              <span className="text-xs text-gray-400">{article.source}</span>
                            </div>
                            
                            <h4 className="text-white font-semibold mb-2 line-clamp-2">
                              {article.title}
                            </h4>
                            
                            <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                              {article.description}
                            </p>
                            
                            <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                              <span>Match: {(article.confidence * 100).toFixed(0)}%</span>
                              <span>•</span>
                              <span>
                                {new Date(article.published_at).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric'
                                })}
                              </span>
                              {article.author && article.author !== 'Unknown' && (
                                <>
                                  <span>•</span>
                                  <span>{article.author}</span>
                                </>
                              )}
                            </div>

                            <button
                              onClick={() => handleArticleClick(article)}
                              className="text-orange-400 hover:text-orange-300 text-sm font-medium flex items-center gap-1 transition-colors"
                            >
                              Read full article →
                            </button>
                          </div>
                          
                          {article.image_url && (
                            <img
                              src={article.image_url}
                              alt={article.title}
                              className="w-24 h-24 object-cover rounded-lg flex-shrink-0"
                              onError={(e) => e.target.style.display = 'none'}
                            />
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <RssIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Click "Latest" to load news headlines</p>
                    <p className="text-sm mt-2">or search for specific topics</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6 text-center">
            <h4 className="text-2xl font-bold text-orange-400">
              {stats.total || newsHeadlines.length || 0}
            </h4>
            <p className="text-gray-400">Articles Analyzed</p>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6 text-center">
            <h4 className="text-2xl font-bold text-red-400">
              {stats.fake || newsHeadlines.filter(a => a.prediction === true).length || 0}
            </h4>
            <p className="text-gray-400">Suspicious Articles</p>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6 text-center">
            <h4 className="text-2xl font-bold text-green-400">
              {stats.verified || newsHeadlines.filter(a => a.prediction === false).length || 0}
            </h4>
            <p className="text-gray-400">Found in News</p>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6 text-center">
            <h4 className="text-2xl font-bold text-blue-400">
              {stats.percentage 
                ? `${stats.percentage.toFixed(1)}%` 
                : newsHeadlines.length > 0 
                ? `${((newsHeadlines.filter(a => a.prediction === true).length / newsHeadlines.length) * 100).toFixed(1)}%`
                : '0%'}
            </h4>
            <p className="text-gray-400">Flagged Rate</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default FakeNewsModule;