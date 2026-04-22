import React from 'react';

const ActivityFeed = ({ activities }) => {
  const getCategoryIcon = (category) => {
    const icons = {
      email: '📧',
      file: '📁',
      data: '📊',
      security: '🔒',
      default: '⚙️'
    };
    return icons[category] || icons.default;
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
        <span className="mr-2">📋</span> Recent Activity
      </h3>
      
      {activities.length > 0 ? (
        <div className="space-y-3">
          {activities.map((activity, index) => (
            <div 
              key={index}
              className="bg-gray-750 rounded-lg p-4 border border-gray-600 hover:border-gray-500 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">
                  {formatTime(activity.timestamp)}
                </span>
                <span className="text-lg">
                  {getCategoryIcon(activity.category)}
                </span>
              </div>
              <p className="text-gray-300 text-sm">{activity.detail}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-400">GhostOffice is ready. Run your first cycle to see activity here.</p>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;