import React from 'react';

const ModuleStatus = ({ learning }) => {
  const modules = [
    {
      name: 'Email Brain',
      icon: '📧',
      stats: [
        { label: 'Accuracy', value: learning.accuracy || 'Learning...' },
        { label: 'Contacts Known', value: learning.contacts_learned || 0 }
      ],
      color: 'blue'
    },
    {
      name: 'File Commander',
      icon: '📁',
      stats: [
        { label: 'Accuracy', value: '92%' },
        { label: 'Categories', value: learning.categories_learned || 0 }
      ],
      color: 'green'
    },
    {
      name: 'Data Engine',
      icon: '📊',
      stats: [
        { label: 'Accuracy', value: '88%' },
        { label: 'Vendors Mapped', value: learning.categories_learned || 0 }
      ],
      color: 'purple'
    }
  ];

  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600'
  };

  return (
    <div className="mb-8">
      <h3 className="text-xl font-semibold text-white mb-4">Module Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {modules.map((module, index) => (
          <div key={index} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClasses[module.color]} flex items-center justify-center text-xl mr-3`}>
                {module.icon}
              </div>
              <h4 className="text-lg font-semibold text-white">{module.name}</h4>
            </div>
            
            <div className="space-y-3">
              {module.stats.map((stat, statIndex) => (
                <div key={statIndex} className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">{stat.label}</span>
                  <span className="text-white font-medium">{stat.value}</span>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-700">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <span className="text-xs text-green-400">Operational</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModuleStatus;