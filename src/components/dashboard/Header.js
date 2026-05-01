import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BellIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { useDashboard } from '../../contexts/DashboardContext';
import { toast } from 'react-toastify';

function Header({ toggleSidebar }) {
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();
  const { realTimeAlerts } = useDashboard();
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      localStorage.removeItem('authToken');
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  const handleSettingsClick = () => {
    navigate('/dashboard/profile');
  };

  const unreadAlerts = realTimeAlerts.filter(alert => !alert.read).length;

  return (
    <header className="bg-dark-800/50 backdrop-blur-lg border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-dark-700 transition-colors"
          >
            <Bars3Icon className="h-6 w-6 text-gray-400" />
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 bg-green-500/10 text-green-400 px-3 py-1 rounded-full">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">All Systems Operational</span>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-dark-700 transition-colors"
            >
              <BellIcon className="h-6 w-6 text-gray-400" />
              {unreadAlerts > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium"
                >
                  {unreadAlerts > 9 ? '9+' : unreadAlerts}
                </motion.span>
              )}
            </button>

            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute right-0 mt-2 w-80 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50"
              >
                <div className="p-4 border-b border-dark-700">
                  <h3 className="text-lg font-semibold text-white">Notifications</h3>
                  <p className="text-sm text-gray-400">{unreadAlerts} unread alerts</p>
                </div>
                
                <div className="max-h-80 overflow-y-auto">
                  {realTimeAlerts.slice(0, 5).map((alert, index) => (
                    <div
                      key={index}
                      className="p-4 border-b border-dark-700 hover:bg-dark-700/50 transition-colors"
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          alert.severity === 'high' ? 'bg-red-400' :
                          alert.severity === 'medium' ? 'bg-yellow-400' :
                          'bg-blue-400'
                        }`}></div>
                        <div className="flex-1">
                          <p className="text-white font-medium">{alert.type}</p>
                          <p className="text-gray-400 text-sm">{alert.message}</p>
                          <p className="text-gray-500 text-xs mt-1">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="p-4">
                  <button className="w-full text-cyber-400 hover:text-cyber-300 text-sm font-medium">
                    View All Notifications
                  </button>
                </div>
              </motion.div>
            )}
          </div>

          <button 
            onClick={handleSettingsClick}
            className="p-2 rounded-lg hover:bg-dark-700 transition-colors"
          >
            <Cog6ToothIcon className="h-6 w-6 text-gray-400" />
          </button>

          {/* User Profile Button - Redirects to Profile Page */}
          <button
            onClick={() => navigate('/dashboard/profile')}
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-dark-700 transition-colors"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-cyber-400 to-cyber-600 rounded-full flex items-center justify-center">
              <UserCircleIcon className="h-5 w-5 text-white" />
            </div>
            <div className="hidden md:block text-left">
              <p className="text-white text-sm font-medium">
                {currentUser?.displayName || 'User'}
              </p>
              <p className="text-gray-400 text-xs">Administrator</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;