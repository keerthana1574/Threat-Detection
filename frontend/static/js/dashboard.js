// Cybersecurity Dashboard JavaScript

class CybersecurityDashboard {
    constructor() {
        this.socket = io();
        this.charts = {};
        this.isMonitoring = false;
        this.currentModule = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.initializeCharts();
        this.updateTime();
        this.loadInitialData();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
        
        // Refresh data every 30 seconds
        setInterval(() => this.refreshData(), 30000);
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('start-monitoring').addEventListener('click', () => this.startMonitoring());
        document.getElementById('stop-monitoring').addEventListener('click', () => this.stopMonitoring());
        document.getElementById('refresh-data').addEventListener('click', () => this.refreshData());
        
        // Close modal
        window.closeModal = () => this.closeModal();
        
        // Test buttons (defined globally for HTML onclick)
        window.testCyberbullying = () => this.openTestModal('Cyberbullying Detection', 'cyberbullying');
        window.analyzeArticle = () => this.openTestModal('Fake News Detection', 'fake_news');
        window.testWebSecurity = () => this.openTestModal('Web Security Test', 'web_security');
        window.startNetworkMonitoring = () => this.startNetworkMonitoring();
        window.monitorTwitter = () => this.monitorTwitter();
        window.monitorNewsFeeds = () => this.monitorNewsFeeds();
        window.viewNetworkStats = () => this.viewNetworkStats();
        window.viewWafLogs = () => this.viewWafLogs();
    }
    
    setupWebSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateSystemStatus('Connected', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateSystemStatus('Disconnected', 'danger');
        });
        
        this.socket.on('status_update', (data) => {
            this.handleStatusUpdate(data);
        });
        
        this.socket.on('threat_alert', (data) => {
            this.handleThreatAlert(data);
        });
        
        this.socket.on('module_update', (data) => {
            this.handleModuleUpdate(data);
        });
    }
    
    initializeCharts() {
        // Threat Timeline Chart
        const timelineCtx = document.getElementById('threatTimelineChart').getContext('2d');
        this.charts.timeline = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Threats Detected',
                    data: [],
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
        
        // Threat Distribution Chart
        const distributionCtx = document.getElementById('threatDistributionChart').getContext('2d');
        this.charts.distribution = new Chart(distributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Cyberbullying', 'Fake News', 'DDoS', 'SQL Injection', 'XSS'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgb(147, 51, 234)',
                        'rgb(249, 115, 22)',
                        'rgb(239, 68, 68)',
                        'rgb(34, 197, 94)',
                        'rgb(59, 130, 246)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadInitialData() {
        try {
            // Load dashboard status
            const response = await axios.get('/api/dashboard/status');
            this.handleStatusUpdate(response.data);
            
            // Load analytics data
            const analyticsResponse = await axios.get('/api/dashboard/analytics');
            this.updateCharts(analyticsResponse.data);
            
            // Load recent alerts
            const alertsResponse = await axios.get('/api/dashboard/alerts');
            this.updateAlertsTable(alertsResponse.data.alerts);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading dashboard data', 'danger');
        }
    }
    
    async startMonitoring() {
        try {
            await axios.post('/api/dashboard/start_monitoring');
            this.isMonitoring = true;
            this.updateMonitoringState();
            this.showNotification('Monitoring started successfully', 'success');
        } catch (error) {
            console.error('Error starting monitoring:', error);
            this.showNotification('Failed to start monitoring', 'danger');
        }
    }
    
    async stopMonitoring() {
        try {
            await axios.post('/api/dashboard/stop_monitoring');
            this.isMonitoring = false;
            this.updateMonitoringState();
            this.showNotification('Monitoring stopped', 'warning');
        } catch (error) {
            console.error('Error stopping monitoring:', error);
            this.showNotification('Failed to stop monitoring', 'danger');
        }
    }
    
    async refreshData() {
        const button = document.getElementById('refresh-data');
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Refreshing...';
        button.disabled = true;
        
        try {
            await this.loadInitialData();
            this.showNotification('Data refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to refresh data', 'danger');
        } finally {
            button.innerHTML = '<i class="fas fa-refresh mr-2"></i>Refresh';
            button.disabled = false;
        }
    }
    
    updateMonitoringState() {
        const startBtn = document.getElementById('start-monitoring');
        const stopBtn = document.getElementById('stop-monitoring');
        const statusElement = document.getElementById('system-status');
        
        if (this.isMonitoring) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusElement.innerHTML = '<span class="w-3 h-3 bg-green-500 rounded-full mr-2 pulse-dot"></span><span>System Active</span>';
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            statusElement.innerHTML = '<span class="w-3 h-3 bg-red-500 rounded-full mr-2"></span><span>System Inactive</span>';
        }
    }
    
    handleStatusUpdate(data) {
        if (data.modules) {
            Object.keys(data.modules).forEach(module => {
                const moduleData = data.modules[module];
                this.updateModuleStatus(module, moduleData);
            });
        }
        
        if (data.monitoring_active !== undefined) {
            this.isMonitoring = data.monitoring_active;
            this.updateMonitoringState();
        }
    }
    
    updateModuleStatus(moduleName, moduleData) {
        const statusElement = document.getElementById(`${moduleName.replace('_', '-')}-status`);
        if (statusElement) {
            statusElement.textContent = moduleData.status;
            statusElement.className = `px-2 py-1 rounded text-sm ${moduleData.status === 'active' ? 'status-active' : 'status-inactive'}`;
        }
        
        // Update last check time
        const lastCheckElement = document.getElementById(`${moduleName.replace('_', '-')}-last-check`);
        if (lastCheckElement && moduleData.last_check) {
            const time = new Date(moduleData.last_check).toLocaleTimeString();
            lastCheckElement.textContent = time;
        }
    }
    
    updateCharts(analyticsData) {
        // Update timeline chart
        if (analyticsData.threats_timeline) {
            this.charts.timeline.data.labels = analyticsData.threats_timeline.map(item => item.hour);
            this.charts.timeline.data.datasets[0].data = analyticsData.threats_timeline.map(item => item.threats);
            this.charts.timeline.update();
        }
        
        // Update distribution chart
        if (analyticsData.threats_by_type) {
            const threatTypes = analyticsData.threats_by_type;
            this.charts.distribution.data.datasets[0].data = [
                threatTypes.cyberbullying || 0,
                threatTypes.fake_news || 0,
                threatTypes.ddos_attacks || 0,
                threatTypes.sql_injection || 0,
                threatTypes.xss_attacks || 0
            ];
            this.charts.distribution.update();
        }
        
        // Update statistics
        this.updateStatistics(analyticsData);
    }
    
    updateStatistics(analyticsData) {
        if (analyticsData.threats_by_type) {
            const totalThreats = Object.values(analyticsData.threats_by_type).reduce((sum, count) => sum + count, 0);
            document.getElementById('total-threats').textContent = totalThreats;
        }
        
        // Update individual module statistics
        if (analyticsData.threats_by_type) {
            const threats = analyticsData.threats_by_type;
            
            document.getElementById('cyberbullying-threats').textContent = threats.cyberbullying || 0;
            document.getElementById('fake-news-detected').textContent = threats.fake_news || 0;
            document.getElementById('ddos-attacks').textContent = threats.ddos_attacks || 0;
            document.getElementById('sql-injections').textContent = threats.sql_injection || 0;
            document.getElementById('xss-attempts').textContent = threats.xss_attacks || 0;
        }
    }
    
    updateAlertsTable(alerts) {
        const tbody = document.getElementById('alerts-table');
        tbody.innerHTML = '';
        
        if (!alerts || alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No recent alerts</td></tr>';
            return;
        }
        
        alerts.forEach(alert => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            
            const severityClass = {
                'High': 'bg-red-100 text-red-800',
                'Medium': 'bg-yellow-100 text-yellow-800',
                'Low': 'bg-blue-100 text-blue-800'
            }[alert.severity] || 'bg-gray-100 text-gray-800';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${new Date(alert.timestamp).toLocaleTimeString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${alert.type}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${severityClass}">
                        ${alert.severity}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${alert.source || 'N/A'}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${alert.description}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-indigo-600 hover:text-indigo-900" onclick="dashboard.viewAlertDetails('${alert.id}')">
                        View
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    openTestModal(title, module) {
        this.currentModule = module;
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('testInput').value = '';
        document.getElementById('testResults').classList.add('hidden');
        document.getElementById('testModal').classList.remove('hidden');
        
        // Setup test button
        const testBtn = document.getElementById('runTest');
        testBtn.onclick = () => this.runTest();
    }
    
    closeModal() {
        document.getElementById('testModal').classList.add('hidden');
        this.currentModule = null;
    }
    
    async runTest() {
        const input = document.getElementById('testInput').value.trim();
        if (!input) {
            this.showNotification('Please enter some text to test', 'warning');
            return;
        }
        
        const testBtn = document.getElementById('runTest');
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Testing...';
        testBtn.disabled = true;
        
        try {
            let endpoint;
            switch (this.currentModule) {
                case 'cyberbullying':
                    endpoint = '/api/cyberbullying/predict';
                    break;
                case 'fake_news':
                    endpoint = '/api/fake_news/predict';
                    break;
                case 'web_security':
                    endpoint = '/api/web_security/analyze/sql_injection';
                    break;
                default:
                    throw new Error('Unknown module');
            }
            
            const response = await axios.post(endpoint, { text: input, input: input });
            this.displayTestResults(response.data);
            
        } catch (error) {
            console.error('Test error:', error);
            this.showNotification('Test failed: ' + error.message, 'danger');
        } finally {
            testBtn.innerHTML = 'Test';
            testBtn.disabled = false;
        }
    }
    
    displayTestResults(results) {
        const resultsDiv = document.getElementById('testResultsContent');
        const resultsContainer = document.getElementById('testResults');
        
        let html = '';
        
        if (results.is_cyberbullying !== undefined) {
            html = `
                <div class="space-y-2">
                    <p><strong>Result:</strong> <span class="${results.is_cyberbullying ? 'text-red-600' : 'text-green-600'}">${results.is_cyberbullying ? 'Cyberbullying Detected' : 'Safe Content'}</span></p>
                    <p><strong>Confidence:</strong> ${(results.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Ensemble Probability:</strong> ${(results.ensemble_probability * 100).toFixed(1)}%</p>
                </div>
            `;
        } else if (results.is_fake !== undefined) {
            html = `
                <div class="space-y-2">
                    <p><strong>Result:</strong> <span class="${results.is_fake ? 'text-red-600' : 'text-green-600'}">${results.is_fake ? 'Fake News Detected' : 'Legitimate Content'}</span></p>
                    <p><strong>Confidence:</strong> ${(results.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Ensemble Probability:</strong> ${(results.ensemble_probability * 100).toFixed(1)}%</p>
                </div>
            `;
        } else if (results.final_prediction !== undefined) {
            html = `
                <div class="space-y-2">
                    <p><strong>Result:</strong> <span class="${results.final_prediction ? 'text-red-600' : 'text-green-600'}">${results.final_prediction ? 'Threat Detected' : 'Safe Input'}</span></p>
                    <p><strong>Confidence:</strong> ${(results.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Risk Score:</strong> ${results.rule_based?.risk_score || 0}</p>
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
        resultsContainer.classList.remove('hidden');
    }
    
    async startNetworkMonitoring() {
        try {
            await axios.post('/api/network_security/start_monitoring');
            this.showNotification('Network monitoring started', 'success');
        } catch (error) {
            this.showNotification('Failed to start network monitoring', 'danger');
        }
    }
    
    async monitorTwitter() {
        try {
            const response = await axios.post('/api/cyberbullying/monitor/twitter', {
                keywords: ['cyberbullying', 'harassment', 'bullying'],
                count: 50
            });
            this.showNotification(`Monitored ${response.data.total_tweets} tweets, found ${response.data.cyberbullying_detected} threats`, 'info');
        } catch (error) {
            this.showNotification('Failed to monitor Twitter', 'danger');
        }
    }
    
    async monitorNewsFeeds() {
        try {
            // This would integrate with news monitoring
            this.showNotification('News monitoring started', 'info');
        } catch (error) {
            this.showNotification('Failed to start news monitoring', 'danger');
        }
    }
    
    async viewNetworkStats() {
        try {
            const response = await axios.get('/api/network_security/network_stats');
            // Display network statistics
            console.log('Network stats:', response.data);
            this.showNotification('Network statistics loaded', 'info');
        } catch (error) {
            this.showNotification('Failed to load network statistics', 'danger');
        }
    }
    
    async viewWafLogs() {
        try {
            const response = await axios.get('/api/web_security/waf/attacks');
            console.log('WAF logs:', response.data);
            this.showNotification(`Loaded ${response.data.total} WAF log entries`, 'info');
        } catch (error) {
            this.showNotification('Failed to load WAF logs', 'danger');
        }
    }
    
    updateTime() {
        const now = new Date();
        document.getElementById('current-time').textContent = now.toLocaleTimeString();
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 max-w-sm w-full bg-white border-l-4 p-4 shadow-lg rounded z-50 ${
            type === 'success' ? 'border-green-500' :
            type === 'danger' ? 'border-red-500' :
            type === 'warning' ? 'border-yellow-500' :
            'border-blue-500'
        }`;
        
        notification.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <i class="fas ${
                        type === 'success' ? 'fa-check-circle text-green-400' :
                        type === 'danger' ? 'fa-exclamation-circle text-red-400' :
                        type === 'warning' ? 'fa-exclamation-triangle text-yellow-400' :
                        'fa-info-circle text-blue-400'
                    }"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-gray-700">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button class="text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    handleThreatAlert(alert) {
        this.showNotification(`New threat detected: ${alert.type}`, 'danger');
        // Refresh alerts table
        this.loadInitialData();
    }
    
    viewAlertDetails(alertId) {
        // Implementation for viewing alert details
        console.log('Viewing alert:', alertId);
        this.showNotification('Alert details feature coming soon', 'info');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new CybersecurityDashboard();
});