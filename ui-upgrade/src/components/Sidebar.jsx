import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Email Brain', href: '/email', icon: '📧' },
    { name: 'File Commander', href: '/files', icon: '📁' },
    { name: 'Learning', href: '/learning', icon: '🧠' },
    { name: 'Security', href: '/security', icon: '🔒' },
    { name: 'Assistant', href: '/assistant', icon: '🤖' },
    { name: 'Settings', href: '/settings', icon: '⚙️' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-700 text-center">
        <div className="text-3xl mb-3">📊</div>
        <h2 className="text-xl font-bold text-white">GhostOffice</h2>
        <div className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded-full inline-block mt-1">
          v3.0
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => (
            <li key={item.name}>
              <Link
                to={item.href}
                className={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive(item.href)
                    ? 'bg-amber-500/20 text-amber-300 border-l-2 border-amber-500'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <span className="text-lg mr-3">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            <span className="text-xs text-green-400 font-mono">Encrypted & Local</span>
          </div>
        </div>
        
        <button className="w-full bg-gray-700 hover:bg-red-500 text-gray-300 hover:text-white py-2 px-4 rounded-lg text-sm transition-colors flex items-center justify-center">
          <span className="mr-2">🔐</span>
          Lock & Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;