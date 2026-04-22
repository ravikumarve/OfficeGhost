import React from 'react';

const StatusCard = ({ icon, title, value, detail, color = 'gray', progress }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    amber: 'from-amber-500 to-amber-600',
    gray: 'from-gray-500 to-gray-600'
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300 hover:scale-105">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center text-2xl`}>
          {icon}
        </div>
        
        {progress !== undefined && (
          <div className="text-right">
            <div className="w-16 h-2 bg-gray-600 rounded-full">
              <div 
                className="h-full rounded-full bg-gradient-to-r from-green-400 to-green-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <h3 className="text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <p className="text-2xl font-bold text-white mb-2">{value}</p>
      <p className="text-gray-400 text-sm">{detail}</p>
    </div>
  );
};

export default StatusCard;