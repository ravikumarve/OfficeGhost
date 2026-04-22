import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import StatusCard from './StatusCard';
import ActivityFeed from './ActivityFeed';
import QuickActions from './QuickActions';
import ModuleStatus from './ModuleStatus';
import DataFlowMonitor from './DataFlowMonitor';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';
import { apiCall } from '../hooks/useApi';

const Dashboard = () => {
  const { user } = useAuth();
  const { notifications } = useNotifications();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch system status from Flask API
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await apiCall('/api/status');
        setStatus(data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch status:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const runCycle = async () => {
    try {
      await apiCall('/run-cycle', { method: 'POST' });
      // Refresh status after running cycle
      const data = await apiCall('/api/status');
      setStatus(data);
    } catch (err) {
      console.error('Failed to run cycle:', err);
      alert('Failed to run cycle: ' + err.message);
    }
  };

  const startContinuous = async () => {
    try {
      await apiCall('/start-continuous', { method: 'POST' });
      alert('Continuous mode started');
    } catch (err) {
      console.error('Failed to start continuous mode:', err);
      alert('Failed to start continuous mode: ' + err.message);
    }
  };

  const scanEmails = async () => {
    try {
      await apiCall('/api/emails/scan', { method: 'POST' });
      alert('Email scan initiated');
    } catch (err) {
      console.error('Failed to scan emails:', err);
      alert('Failed to scan emails: ' + err.message);
    }
  };

  const sortFiles = async () => {
    try {
      await apiCall('/api/files/sort', { method: 'POST' });
      alert('File sorting initiated');
    } catch (err) {
      console.error('Failed to sort files:', err);
      alert('Failed to sort files: ' + err.message);
    }
  };

  const extractData = async () => {
    try {
      await apiCall('/api/data/extract', { method: 'POST' });
      alert('Data extraction initiated');
    } catch (err) {
      console.error('Failed to extract data:', err);
      alert('Failed to extract data: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-900">
        <Sidebar />
        <main className="flex-1 p-6 ml-64 flex items-center justify-center">
          <div className="text-white text-xl">Loading dashboard...</div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-gray-900">
        <Sidebar />
        <main className="flex-1 p-6 ml-64 flex items-center justify-center">
          <div className="text-red-400 text-xl">Error: {error}</div>
        </main>
      </div>
    );
  }

  // Extract data from status response
  const health = status?.health || {};
  const security = status?.security || {};
  const learning = status?.learning || {};
  const queue = status?.queue || {};
  const cyclesCompleted = status?.cycles_completed || 0;

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar />
      
      <main className="flex-1 p-6 ml-64">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-gray-400">Your AI office assistant is protecting your workflow</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={runCycle}
              className="bg-amber-500 hover:bg-amber-600 text-gray-900 font-semibold px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              ▶️ Run Cycle
            </button>
            <button 
              onClick={startContinuous}
              className="border border-gray-600 hover:border-gray-500 text-gray-300 hover:text-white font-medium px-6 py-3 rounded-lg transition-colors"
            >
              🔄 Start Continuous
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <QuickActions 
          onScanEmails={scanEmails}
          onSortFiles={sortFiles}
          onExtractData={extractData}
          onRunCycle={runCycle}
        />

        {/* Status Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            icon="💻"
            title="System"
            value={health.overall || 'Checking...'}
            detail={`RAM: ${health.ram?.percent || 0}% | Disk: ${health.disk?.free_gb || 0}GB free`}
            color="blue"
          />
          <StatusCard
            icon="🔒"
            title="Security"
            value={security.overall || 'Checking...'}
            detail={security.detail || 'Checking...'}
            color="green"
          />
          <StatusCard
            icon="🧠"
            title="Learning Score"
            value={`${learning.learning_score || 0}/100`}
            detail={`Accuracy: ${learning.accuracy || '0%'}`}
            color="purple"
            progress={learning.learning_score || 0}
          />
          <StatusCard
            icon="📊"
            title="Cycles"
            value={cyclesCompleted}
            detail={`${queue.completed || 0} tasks completed`}
            color="amber"
          />
        </div>

        {/* Module Status */}
        <ModuleStatus learning={learning} />

        {/* Data Flow Monitor */}
        <DataFlowMonitor />

      </main>
    </div>
  );
};

export default Dashboard;