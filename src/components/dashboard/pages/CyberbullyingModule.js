import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ExclamationTriangleIcon,
  PlayIcon,
  StopIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { toast } from 'react-toastify';

function CyberbullyingModule() {
  const [inputText, setInputText] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recentDetections, setRecentDetections] = useState([
    {
      id: 1,
      text: "You're so stupid, nobody likes you!",
      prediction: true,
      confidence: 0.95,
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      text: "Great job on your presentation today!",
      prediction: false,
      confidence: 0.12,
      timestamp: new Date().toISOString()
    }
  ]);

  const handlePrediction = async () => {
    if (!inputText.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/cyberbullying/predict', {
        text: inputText
      });

      setPrediction(response.data);
      
      // Add to recent detections
      const newDetection = {
        id: Date.now(),
        text: inputText,
        prediction: response.data.prediction,
        confidence: response.data.confidence,
        timestamp: new Date().toISOString()
      };
      
      setRecentDetections(prev => [newDetection, ...prev.slice(0, 9)]);
      
    } catch (error) {
      toast.error('Error analyzing text: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-4">
        <div className="p-3 bg-red-500/20 rounded-lg">
          <ExclamationTriangleIcon className="h-8 w-8 text-red-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Cyberbullying Detection</h1>
          <p className="text-gray-400">Analyze text content for cyberbullying patterns</p>
        </div>
      </div>

      {/* Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Text Analysis</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Enter text to analyze:
              </label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type or paste the text you want to analyze for cyberbullying..."
                className="w-full h-32 p-4 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyber-500 focus:border-cyber-500 resize-none"
              />
            </div>
            
            <button
              onClick={handlePrediction}
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-3 px-4 rounded-lg font-medium hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
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

        {/* Results Section */}
        <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Analysis Results</h3>
          
          {prediction ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              {/* Prediction Result */}
              <div className={`p-4 rounded-lg border-2 ${
                prediction.prediction
                  ? 'bg-red-500/10 border-red-500/50 text-red-400'
                  : 'bg-green-500/10 border-green-500/50 text-green-400'
              }`}>
                <h4 className="font-semibold text-lg">
                  {prediction.prediction ? '⚠️ Cyberbullying Detected' : '✅ No Cyberbullying'}
                </h4>
                <p className="text-sm opacity-80">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </p>
              </div>

              {/* Confidence Meter */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Confidence Level</span>
                  <span className="text-white font-medium">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-dark-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-1000 ${
                      prediction.prediction ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${prediction.confidence * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Processing Time */}
              <div className="text-sm text-gray-400">
                Processing time: {prediction.processing_time?.toFixed(3) || '0.123'}s
              </div>
            </motion.div>
          ) : (
            <div className="flex items-center justify-center h-40 text-gray-400">
              <div className="text-center">
                <DocumentTextIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Enter text and click "Analyze Text" to see results</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Detections */}
      <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Recent Detections</h3>
        
        <div className="space-y-3">
          {recentDetections.map((detection, index) => (
            <motion.div
              key={detection.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-4 p-4 bg-dark-700/50 rounded-lg border border-dark-600"
            >
              <div className={`p-2 rounded-lg ${
                detection.prediction
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-green-500/20 text-green-400'
              }`}>
                <ExclamationTriangleIcon className="h-5 w-5" />
              </div>
              
              <div className="flex-1">
                <p className="text-white font-medium line-clamp-2">
                  {detection.text}
                </p>
                <div className="flex items-center space-x-4 mt-2">
                  <span className={`text-sm font-medium ${
                    detection.prediction ? 'text-red-400' : 'text-green-400'
                  }`}>
                    {detection.prediction ? 'Cyberbullying' : 'Safe'}
                  </span>
                  <span className="text-sm text-gray-400">
                    Confidence: {(detection.confidence * 100).toFixed(1)}%
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(detection.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Module Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6 text-center">
          <h4 className="text-2xl font-bold text-red-400">247</h4>
          <p className="text-gray-400">Total Detections</p>
        </div>
        
        <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6 text-center">
          <h4 className="text-2xl font-bold text-green-400">94.5%</h4>
          <p className="text-gray-400">Accuracy Rate</p>
        </div>
        
        <div className="bg-dark-800/50 backdrop-blur-lg border border-dark-700 rounded-xl p-6 text-center">
          <h4 className="text-2xl font-bold text-yellow-400">15</h4>
          <p className="text-gray-400">Today's Alerts</p>
        </div>
      </div>
    </motion.div>
  );
}

export default CyberbullyingModule;
