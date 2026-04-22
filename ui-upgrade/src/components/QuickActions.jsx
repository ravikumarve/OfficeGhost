import React from 'react';

const QuickActions = ({ onScanEmails, onSortFiles, onExtractData, onRunCycle }) => {
  const actions = [
    {
      label: 'Scan Emails',
      icon: '📧',
      onClick: onScanEmails,
      color: 'blue'
    },
    {
      label: 'Sort Files',
      icon: '📁',
      onClick: onSortFiles,
      color: 'green'
    },
    {
      label: 'Extract Data',
      icon: '📊',
      onClick: onExtractData,
      color: 'purple'
    },
    {
      label: 'Run All',
      icon: '🔄',
      onClick: onRunCycle,
      color: 'amber'
    },
    {
      label: 'Assistant',
      icon: '🤖',
      onClick: () => window.location.href = '/assistant',
      color: 'gray'
    }
  ];

  const colorClasses = {
    blue: 'hover:bg-blue-500/20 hover:text-blue-300 hover:border-blue-500',
    green: 'hover:bg-green-500/20 hover:text-green-300 hover:border-green-500',
    purple: 'hover:bg-purple-500/20 hover:text-purple-300 hover:border-purple-500',
    amber: 'hover:bg-amber-500/20 hover:text-amber-300 hover:border-amber-500',
    gray: 'hover:bg-gray-500/20 hover:text-gray-300 hover:border-gray-500'
  };

  return (
    <div className="flex flex-wrap gap-3 mb-8">
      {actions.map((action, index) => (
        <button
          key={index}
          onClick={action.onClick}
          className={`flex items-center px-4 py-2 border border-gray-600 rounded-lg transition-all duration-200 transform hover:scale-105 ${colorClasses[action.color]}`}
        >
          <span className="text-lg mr-2">{action.icon}</span>
          <span className="text-sm font-medium">{action.label}</span>
        </button>
      ))}
    </div>
  );
};

export default QuickActions;