import React, { useState, useEffect } from 'react';
import { Activity, Users, Mail, TrendingUp, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';

interface DashboardStats {
  totalSearches: number;
  emailsVerified: number;
  emailsGenerated: number;
  companiesAnalyzed: number;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalSearches: 0,
    emailsVerified: 0,
    emailsGenerated: 0,
    companiesAnalyzed: 0
  });
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  useEffect(() => {
    checkSystemHealth();
    // Load stats from localStorage or API
    const savedStats = localStorage.getItem('dashboardStats');
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    }
  }, []);

  const checkSystemHealth = async () => {
    try {
      await apiService.healthCheck();
      setSystemStatus('online');
    } catch (error) {
      console.warn('Backend health check failed:', error);
      setSystemStatus('offline');
    }
  };

  const updateStats = (type: keyof DashboardStats) => {
    const newStats = { ...stats, [type]: stats[type] + 1 };
    setStats(newStats);
    localStorage.setItem('dashboardStats', JSON.stringify(newStats));
  };

  const resetStats = () => {
    const resetStats = {
      totalSearches: 0,
      emailsVerified: 0,
      emailsGenerated: 0,
      companiesAnalyzed: 0
    };
    setStats(resetStats);
    localStorage.setItem('dashboardStats', JSON.stringify(resetStats));
    toast.success('Stats reset successfully');
  };

  const statCards = [
    {
      title: 'Total Searches',
      value: stats.totalSearches,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      change: '+12% from last week'
    },
    {
      title: 'Emails Verified',
      value: stats.emailsVerified,
      icon: Mail,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      change: '+8% from last week'
    },
    {
      title: 'Emails Generated',
      value: stats.emailsGenerated,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      change: '+15% from last week'
    },
    {
      title: 'Companies Analyzed',
      value: stats.companiesAnalyzed,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      change: '+5% from last week'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor your sales AI agent performance</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* System Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus === 'online' ? 'bg-green-500' :
              systemStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
            }`}></div>
            <span className="text-sm text-gray-600">
              System {systemStatus === 'checking' ? 'Checking...' : systemStatus}
            </span>
          </div>
          
          <button
            onClick={resetStats}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
          >
            Reset Stats
          </button>
        </div>
      </div>

      {/* System Status Alert */}
      {systemStatus === 'offline' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
          <div>
            <h3 className="font-semibold text-red-800">Backend Service Offline</h3>
            <p className="text-red-700 text-sm">
              The backend API is not responding. Please ensure the Python FastAPI server is running on port 8000.
            </p>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${card.bgColor}`}>
                  <Icon className={`w-6 h-6 ${card.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-green-600 font-medium">{card.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <h3 className="font-medium text-gray-900 mb-2">Find New Leads</h3>
            <p className="text-sm text-gray-600 mb-3">Search for potential customers using advanced AI</p>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
              Start Search →
            </button>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <h3 className="font-medium text-gray-900 mb-2">Verify Emails</h3>
            <p className="text-sm text-gray-600 mb-3">Validate email addresses before outreach</p>
            <button className="text-green-600 hover:text-green-800 text-sm font-medium">
              Verify Now →
            </button>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <h3 className="font-medium text-gray-900 mb-2">Generate Emails</h3>
            <p className="text-sm text-gray-600 mb-3">Create personalized outreach messages</p>
            <button className="text-purple-600 hover:text-purple-800 text-sm font-medium">
              Generate →
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[
            { action: 'Searched for "VP Sales at SaaS companies"', time: '2 minutes ago', type: 'search' },
            { action: 'Verified email john.doe@techcorp.com', time: '5 minutes ago', type: 'verify' },
            { action: 'Generated email for Microsoft decision maker', time: '10 minutes ago', type: 'generate' },
            { action: 'Analyzed Google company profile', time: '15 minutes ago', type: 'analyze' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 py-2">
              <div className={`w-2 h-2 rounded-full ${
                activity.type === 'search' ? 'bg-blue-500' :
                activity.type === 'verify' ? 'bg-green-500' :
                activity.type === 'generate' ? 'bg-purple-500' : 'bg-orange-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">{activity.action}</p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};