// Fixed Dashboard.js - Clean structure
import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Overview from './pages/Overview';
import CyberbullyingModule from './pages/CyberbullyingModule';
import FakeNewsModule from './pages/FakeNewsModule';
import EnhancedNetworkSecurityModule from './pages/EnhancedNetworkSecurityModule';
import WebSecurityModule from './pages/WebSecurityModule';
import PhishingModule from './pages/PhishingModule';
import Profile from './pages/Profile';
import RealTimeMonitoring from './pages/RealTimeMonitoring';

function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-dark-950 text-white">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      
      <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/cyberbullying" element={<CyberbullyingModule />} />
            <Route path="/fake-news" element={<FakeNewsModule />} />
            <Route path="/network-security" element={<EnhancedNetworkSecurityModule />} />
            <Route path="/web-security" element={<WebSecurityModule />} />
            <Route path="/phishing" element={<PhishingModule />} />
            <Route path="/real-time" element={<RealTimeMonitoring />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;