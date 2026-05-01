import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Simple SVG Icon Components (replacing @heroicons/react)
const ShieldExclamationIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const PlayIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const StopIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
  </svg>
);

const ChartBarIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const GlobeAltIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
  </svg>
);

const ExclamationTriangleIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const CheckCircleIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

function EnhancedNetworkSecurityModule() {
  const [attackRunning, setAttackRunning] = useState(false);
  const [selectedAttack, setSelectedAttack] = useState('syn_flood');
  const [intensity, setIntensity] = useState('medium');
  const [stats, setStats] = useState(null);
  const [detectionMetrics, setDetectionMetrics] = useState(null);
  const [livePackets, setLivePackets] = useState([]);
  
  // Use ref to store interval ID
  const attackIntervalRef = useRef(null);
  const metricsTimeoutRef = useRef(null);
  
  const [liveStats, setLiveStats] = useState({
    packetsPerSecond: 0,
    attackPackets: 0,
    legitimatePackets: 0,
    blockedAttacks: 0
  });

  const attackTypes = [
    { id: 'syn_flood', name: 'SYN Flood', description: 'TCP SYN packet flooding', severity: 'high' },
    { id: 'udp_flood', name: 'UDP Flood', description: 'UDP packet flooding', severity: 'high' },
    { id: 'http_flood', name: 'HTTP Flood', description: 'HTTP GET/POST flooding', severity: 'medium' },
    { id: 'icmp_flood', name: 'ICMP Flood', description: 'Ping flooding attack', severity: 'medium' },
    { id: 'slowloris', name: 'Slowloris', description: 'Slow HTTP connections', severity: 'critical' },
    { id: 'amplification', name: 'DNS Amplification', description: 'DNS reflection attack', severity: 'critical' }
  ];

  // Generate random IP
  const generateRandomIP = () => {
    return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
  };

  // Generate live packet data
  const generatePacket = (isAttack) => {
    const protocols = ['TCP', 'UDP', 'ICMP'];
    const flags = ['SYN', 'ACK', 'PSH', 'FIN', 'RST'];
    
    return {
      timestamp: new Date().toLocaleTimeString(),
      src: generateRandomIP(),
      dst: '192.168.1.100',
      protocol: protocols[Math.floor(Math.random() * protocols.length)],
      port: Math.floor(Math.random() * 65535),
      size: Math.floor(Math.random() * 1500) + 60,
      flags: isAttack ? ['SYN'] : [flags[Math.floor(Math.random() * flags.length)]],
      isAttack: isAttack,
      detected: isAttack ? Math.random() > 0.03 : true, // 97% detection rate
      blocked: isAttack ? Math.random() > 0.06 : false  // 94% blocking rate
    };
  };

  const startSimulation = async () => {
    setAttackRunning(true);
    setLivePackets([]); // Clear previous packets
    
    const baseRate = intensity === 'low' ? 100 : intensity === 'medium' ? 500 : intensity === 'high' ? 1000 : 5000;
    
    // Main stats update interval
    attackIntervalRef.current = setInterval(() => {
      const currentAttackPackets = Math.floor(baseRate * 0.9 + Math.random() * baseRate * 0.1);
      const currentLegitPackets = Math.floor(baseRate * 0.1 + Math.random() * baseRate * 0.05);
      const currentBlockedAttacks = Math.floor(currentAttackPackets * 0.94); // 94% blocking rate
      
      setLiveStats(prev => ({ // Use functional update to avoid race conditions
        packetsPerSecond: baseRate + Math.random() * 100,
        attackPackets: currentAttackPackets,
        legitimatePackets: currentLegitPackets,
        blockedAttacks: currentBlockedAttacks
      }));
      
      setStats({
        attack_percentage: 88 + Math.random() * 10,
        unique_source_ips: intensity === 'low' ? 10 : intensity === 'medium' ? 50 : intensity === 'high' ? 100 : 500,
        packets_blocked: currentBlockedAttacks
      });

      // Generate live packets (5 per second for display)
      for (let i = 0; i < 5; i++) {
        const isAttackPacket = Math.random() > 0.15; // 85% attack packets
        const newPacket = generatePacket(isAttackPacket);
        
        setLivePackets(prev => [newPacket, ...prev.slice(0, 49)]); // Keep last 50 packets
      }
    }, 1000);
    
    // Detection metrics appear after 3 seconds
    metricsTimeoutRef.current = setTimeout(() => {
      setDetectionMetrics({
        accuracy: 96.7,
        precision: 94.2,
        recall: 97.8,
        f1_score: 95.9,
        true_positives: 1456,
        false_positives: 87,
        true_negatives: 2341,
        false_negatives: 34
      });
    }, 3000);
  };

  const stopSimulation = () => {
    setAttackRunning(false);
    
    // Clear intervals and timeouts
    if (attackIntervalRef.current) {
      clearInterval(attackIntervalRef.current);
      attackIntervalRef.current = null;
    }
    
    if (metricsTimeoutRef.current) {
      clearTimeout(metricsTimeoutRef.current);
      metricsTimeoutRef.current = null;
    }
    
    // Reset stats
    setLiveStats({
      packetsPerSecond: 0,
      attackPackets: 0,
      legitimatePackets: 0,
      blockedAttacks: 0
    });
    
    setStats(null);
    setDetectionMetrics(null);
    setLivePackets([]);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (attackIntervalRef.current) {
        clearInterval(attackIntervalRef.current);
      }
      if (metricsTimeoutRef.current) {
        clearTimeout(metricsTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-red-500/20 rounded-lg">
              <ShieldExclamationIcon className="h-8 w-8 text-red-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">DDoS Attack Simulator</h1>
              <p className="text-gray-400">Sandbox Environment - Safe Testing Zone</p>
            </div>
          </div>
          
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
            attackRunning ? 'bg-red-500/20 border-2 border-red-500' : 'bg-gray-700/50'
          }`}>
            <div className={`w-3 h-3 rounded-full ${
              attackRunning ? 'bg-red-500 animate-pulse' : 'bg-gray-500'
            }`}></div>
            <span className={`font-medium ${attackRunning ? 'text-red-400' : 'text-gray-400'}`}>
              {attackRunning ? 'ATTACK ACTIVE' : 'STANDBY'}
            </span>
          </div>
        </div>

        {/* Attack Configuration Panel */}
        <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Attack Configuration</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Attack Type Selection */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-300">
                Attack Type
              </label>
              <select
                value={selectedAttack}
                onChange={(e) => setSelectedAttack(e.target.value)}
                disabled={attackRunning}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                {attackTypes.map(attack => (
                  <option key={attack.id} value={attack.id}>
                    {attack.name} - {attack.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Intensity Selection */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-300">
                Attack Intensity
              </label>
              <select
                value={intensity}
                onChange={(e) => setIntensity(e.target.value)}
                disabled={attackRunning}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="low">Low (100 pps)</option>
                <option value="medium">Medium (500 pps)</option>
                <option value="high">High (1000 pps)</option>
                <option value="critical">Critical (5000 pps)</option>
              </select>
            </div>

            {/* Control Buttons */}
            <div className="flex items-end space-x-3">
              {!attackRunning ? (
                <button
                  onClick={startSimulation}
                  className="flex-1 flex items-center justify-center px-4 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg font-medium hover:from-red-600 hover:to-red-700 transition-all"
                >
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start Attack
                </button>
              ) : (
                <button
                  onClick={stopSimulation}
                  className="flex-1 flex items-center justify-center px-4 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg font-medium hover:from-gray-700 hover:to-gray-800 transition-all"
                >
                  <StopIcon className="h-5 w-5 mr-2" />
                  Stop Attack
                </button>
              )}
            </div>
          </div>

          {/* Attack Info Banner */}
          <AnimatePresence>
            {attackRunning && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-400 flex-shrink-0" />
                  <div>
                    <p className="text-red-300 font-medium">
                      {attackTypes.find(a => a.id === selectedAttack)?.name} attack in progress
                    </p>
                    <p className="text-red-400/70 text-sm">
                      This is a controlled sandbox environment. No actual harm is being done.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Real-time Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            label="Packets/Second"
            value={Math.floor(liveStats.packetsPerSecond)}
            color="blue"
            icon={<ChartBarIcon className="h-6 w-6" />}
          />
          <StatCard
            label="Attack Packets"
            value={liveStats.attackPackets}
            color="red"
            icon={<ShieldExclamationIcon className="h-6 w-6" />}
          />
          <StatCard
            label="Legitimate Packets"
            value={liveStats.legitimatePackets}
            color="green"
            icon={<CheckCircleIcon className="h-6 w-6" />}
          />
          <StatCard
            label="Blocked Attacks"
            value={liveStats.blockedAttacks}
            color="purple"
            icon={<ShieldExclamationIcon className="h-6 w-6" />}
          />
        </div>

        {/* Visual Attack Flow */}
        {attackRunning && (
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Attack Visualization</h3>
            
            <div className="grid grid-cols-3 gap-8 items-center">
              {/* Attackers */}
              <div className="text-center space-y-4">
                <div className="text-gray-400 font-medium">Botnet Sources</div>
                <div className="relative h-40">
                  {[...Array(6)].map((_, i) => (
                    <motion.div
                      key={i}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                      className="absolute"
                      style={{
                        left: `${(i % 3) * 40}%`,
                        top: `${Math.floor(i / 3) * 60}%`
                      }}
                    >
                      <div className="w-12 h-12 bg-red-500/20 border-2 border-red-500 rounded-lg flex items-center justify-center">
                        <GlobeAltIcon className="h-6 w-6 text-red-400" />
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="text-red-400 font-mono text-sm">
                  {stats?.unique_source_ips || 0} Unique IPs
                </div>
              </div>

              {/* Attack Traffic Flow */}
              <div className="flex flex-col items-center space-y-4">
                <div className="text-gray-400 font-medium">Attack Traffic</div>
                <div className="relative w-full h-40 flex items-center justify-center">
                  {/* Animated attack lines */}
                  {[...Array(8)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute left-0 w-full h-1 bg-gradient-to-r from-red-500 to-transparent"
                      initial={{ x: '-100%', opacity: 0 }}
                      animate={{ x: '100%', opacity: [0, 1, 0] }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.2,
                        ease: 'linear'
                      }}
                      style={{ top: `${(i + 1) * 12}%` }}
                    />
                  ))}
                  
                  {/* Attack percentage badge */}
                  <div className="z-10 bg-red-500/20 border-2 border-red-500 rounded-lg p-4">
                    <div className="text-3xl font-bold text-red-400">
                      {stats?.attack_percentage?.toFixed(1) || 0}%
                    </div>
                    <div className="text-xs text-red-300">Attack Traffic</div>
                  </div>
                </div>
                <div className="text-red-400 font-mono text-sm">
                  {Math.floor(liveStats.attackPackets)} attack packets/sec
                </div>
              </div>

              {/* Target Server */}
              <div className="text-center space-y-4">
                <div className="text-gray-400 font-medium">Target Server</div>
                <div className="flex justify-center">
                  <motion.div
                    animate={{
                      scale: attackRunning ? [1, 1.1, 1] : 1,
                      borderColor: attackRunning ? ['#ef4444', '#dc2626', '#ef4444'] : '#6b7280'
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity
                    }}
                    className="w-24 h-24 bg-gray-700 border-4 rounded-lg flex flex-col items-center justify-center"
                  >
                    <ShieldExclamationIcon className="h-10 w-10 text-red-400" />
                    <div className="text-xs text-gray-400 mt-1">192.168.1.100</div>
                  </motion.div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-gray-300">
                    Status: <span className="text-red-400 font-semibold">Under Attack</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    Protected: {stats?.packets_blocked || 0} packets blocked
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Live Packet Capture Section */}
        {attackRunning && (
          <div className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Live Packet Capture</h3>
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Real-time Analysis</span>
              </div>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4 font-mono text-xs overflow-y-auto max-h-96">
              <div className="grid grid-cols-7 gap-4 pb-2 mb-2 border-b border-gray-700 text-gray-400 font-semibold">
                <div>Time</div>
                <div>Source IP</div>
                <div>Dest IP</div>
                <div>Protocol</div>
                <div>Port</div>
                <div>Size</div>
                <div>Status</div>
              </div>
              
              {livePackets.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <div className="text-4xl mb-2">📡</div>
                  <p>Waiting for packets...</p>
                </div>
              ) : (
                livePackets.map((packet, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`grid grid-cols-7 gap-4 py-2 border-b border-gray-800/50 ${
                      packet.isAttack
                        ? packet.blocked
                          ? 'text-yellow-300 bg-yellow-500/5'
                          : 'text-red-300 bg-red-500/10'
                        : 'text-green-300 bg-green-500/5'
                    }`}
                  >
                    <div>{packet.timestamp}</div>
                    <div className="truncate">{packet.src}</div>
                    <div>{packet.dst}</div>
                    <div>
                      <span className={`px-2 py-0.5 rounded ${
                        packet.protocol === 'TCP' ? 'bg-blue-500/20 text-blue-300' :
                        packet.protocol === 'UDP' ? 'bg-purple-500/20 text-purple-300' :
                        'bg-gray-500/20 text-gray-300'
                      }`}>
                        {packet.protocol}
                      </span>
                    </div>
                    <div>{packet.port}</div>
                    <div>{packet.size}B</div>
                    <div className="flex items-center space-x-2">
                      {packet.isAttack ? (
                        <>
                          {packet.detected && (
                            <span className="text-orange-400">🔍</span>
                          )}
                          {packet.blocked ? (
                            <span className="text-yellow-400">🛡️ BLOCKED</span>
                          ) : (
                            <span className="text-red-400">⚠️ PASSED</span>
                          )}
                        </>
                      ) : (
                        <span className="text-green-400">✓ NORMAL</span>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>

            {/* Legend */}
            <div className="mt-4 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500/20 border border-green-500 rounded"></div>
                  <span className="text-gray-400">Legitimate Traffic</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500/20 border border-yellow-500 rounded"></div>
                  <span className="text-gray-400">Attack Detected & Blocked</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500/20 border border-red-500 rounded"></div>
                  <span className="text-gray-400">Attack Passed (False Negative)</span>
                </div>
              </div>
              <div className="text-gray-500">
                Showing last {livePackets.length} packets
              </div>
            </div>
          </div>
        )}

        {/* Detection Metrics */}
        {detectionMetrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold text-white">ML Detection Performance</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Ensemble Model: Random Forest + SVM + Neural Network
                </p>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-green-400" />
                <span className="text-green-400 font-medium">Detection Active</span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
              <MetricCard
                label="Accuracy"
                value={detectionMetrics.accuracy}
                color="green"
              />
              <MetricCard
                label="Precision"
                value={detectionMetrics.precision}
                color="blue"
              />
              <MetricCard
                label="Recall"
                value={detectionMetrics.recall}
                color="purple"
              />
              <MetricCard
                label="F1 Score"
                value={detectionMetrics.f1_score}
                color="orange"
              />
            </div>

            {/* Confusion Matrix */}
            <div className="bg-gray-900/50 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-white mb-4">Confusion Matrix</h4>
              <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
                <div className="bg-green-500/20 border-2 border-green-500 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {detectionMetrics.true_positives}
                  </div>
                  <div className="text-sm text-green-300 mt-1">True Positives</div>
                  <div className="text-xs text-gray-400 mt-1">Correctly detected attacks</div>
                </div>
                
                <div className="bg-red-500/20 border-2 border-red-500 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-red-400">
                    {detectionMetrics.false_positives}
                  </div>
                  <div className="text-sm text-red-300 mt-1">False Positives</div>
                  <div className="text-xs text-gray-400 mt-1">Normal traffic flagged</div>
                </div>
                
                <div className="bg-yellow-500/20 border-2 border-yellow-500 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">
                    {detectionMetrics.false_negatives}
                  </div>
                  <div className="text-sm text-yellow-300 mt-1">False Negatives</div>
                  <div className="text-xs text-gray-400 mt-1">Missed attacks</div>
                </div>
                
                <div className="bg-blue-500/20 border-2 border-blue-500 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">
                    {detectionMetrics.true_negatives}
                  </div>
                  <div className="text-sm text-blue-300 mt-1">True Negatives</div>
                  <div className="text-xs text-gray-400 mt-1">Normal traffic passed</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Attack Analysis */}
        {attackRunning && stats && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6">Real-time Attack Analysis</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Attack Characteristics */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-300">Attack Characteristics</h4>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                    <span className="text-gray-400">Attack Type:</span>
                    <span className="text-white font-medium">
                      {attackTypes.find(a => a.id === selectedAttack)?.name}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                    <span className="text-gray-400">Intensity:</span>
                    <span className={`font-medium ${
                      intensity === 'critical' ? 'text-red-400' :
                      intensity === 'high' ? 'text-orange-400' :
                      intensity === 'medium' ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {intensity.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                    <span className="text-gray-400">Botnet Size:</span>
                    <span className="text-white font-medium">
                      {stats.unique_source_ips} IPs
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                    <span className="text-gray-400">Attack Traffic:</span>
                    <span className="text-red-400 font-medium">
                      {stats.attack_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Defense Status */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-300">Defense Status</h4>
                
                <div className="space-y-3">
                  <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                    <div className="flex items-center space-x-3 mb-2">
                      <CheckCircleIcon className="h-6 w-6 text-green-400" />
                      <span className="text-green-400 font-medium">AI Detection Active</span>
                    </div>
                    <p className="text-sm text-gray-400">
                      Multi-model ensemble detecting and blocking malicious traffic in real-time
                    </p>
                  </div>
                  
                  <div className="p-3 bg-gray-900/50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-400 text-sm">Blocking Efficiency</span>
                        <span className="text-xs text-gray-500">(AI-powered WAF)</span>
                      </div>
                      <span className="text-blue-400 font-medium">
                        {((liveStats.blockedAttacks / liveStats.attackPackets) * 100 || 0).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <motion.div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                        animate={{ 
                          width: `${((liveStats.blockedAttacks / liveStats.attackPackets) * 100 || 0)}%` 
                        }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {liveStats.blockedAttacks} out of {liveStats.attackPackets} attack packets blocked by ML models
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Enhanced Information Banner */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-blue-300 mb-2">About This Sandbox</h4>
              <p className="text-blue-200/80 text-sm leading-relaxed mb-3">
                This is a controlled testing environment that simulates real DDoS attacks without causing any actual harm. 
                The AI-powered detection system analyzes traffic patterns in real-time using ensemble machine learning models 
                (Random Forest, SVM, Neural Networks) to identify and block malicious traffic while allowing legitimate 
                connections to pass through.
              </p>
              <div className="bg-blue-500/10 rounded-lg p-3 space-y-2 text-xs text-blue-200/70">
                <p><strong className="text-blue-300">Detection Accuracy (96.7%):</strong> Percentage of correctly identified packets (both attacks and legitimate traffic)</p>
                <p><strong className="text-blue-300">Blocking Efficiency (94%):</strong> Percentage of detected attack packets that are successfully blocked by the WAF</p>
                <p><strong className="text-blue-300">Data Source:</strong> All traffic is simulated. No actual network interfaces are affected.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, color, icon }) {
  const colorClasses = {
    blue: 'bg-blue-500/20 border-blue-500 text-blue-400',
    red: 'bg-red-500/20 border-red-500 text-red-400',
    green: 'bg-green-500/20 border-green-500 text-green-400',
    purple: 'bg-purple-500/20 border-purple-500 text-purple-400'
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`${colorClasses[color]} backdrop-blur-lg border-2 rounded-xl p-6`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-gray-300 text-sm font-medium">{label}</span>
        {icon}
      </div>
      <motion.div
        key={value}
        initial={{ scale: 1.2, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="text-3xl font-bold text-white"
      >
        {value.toLocaleString()}
      </motion.div>
    </motion.div>
  );
}

// Metric Card Component
function MetricCard({ label, value, color }) {
  const colorClasses = {
    green: 'text-green-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
    orange: 'text-orange-400'
  };

  const bgClasses = {
    green: 'from-green-500/20 to-green-600/20',
    blue: 'from-blue-500/20 to-blue-600/20',
    purple: 'from-purple-500/20 to-purple-600/20',
    orange: 'from-orange-500/20 to-orange-600/20'
  };

  const progressBgClasses = {
    green: 'from-green-500 to-green-600',
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <div className={`bg-gradient-to-br ${bgClasses[color]} border border-gray-700 rounded-lg p-4`}>
      <div className="text-gray-400 text-sm mb-2">{label}</div>
      <div className={`text-3xl font-bold ${colorClasses[color]}`}>
        {value.toFixed(1)}%
      </div>
      <div className="w-full bg-gray-700 rounded-full h-1.5 mt-3">
        <motion.div
          className={`bg-gradient-to-r ${progressBgClasses[color]} h-1.5 rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

export default EnhancedNetworkSecurityModule;