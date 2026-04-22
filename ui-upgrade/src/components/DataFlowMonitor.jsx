import React from 'react';

const DataFlowMonitor = () => {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Data Flow Monitor</h3>
      
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Local Machine */}
        <div className="flex-1 bg-gray-750 rounded-lg p-6 border border-gray-600 text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
            💻
          </div>
          <h4 className="text-white font-semibold mb-4">Your Machine</h4>
          
          <ul className="space-y-2 text-sm text-gray-300">
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              Emails processed locally
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              Files analyzed on-device
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              AI inference via Ollama
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              Data encrypted at rest
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              Zero external data transfer
            </li>
          </ul>
        </div>

        {/* Center Blocked Indicator */}
        <div className="flex flex-col items-center justify-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center text-2xl text-white mb-2">
            🚫
          </div>
          <div className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full text-xs font-semibold">
            BLOCKED
          </div>
        </div>

        {/* Internet */}
        <div className="flex-1 bg-gray-750 rounded-lg p-6 border border-gray-600 text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-gray-500 to-gray-600 rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
            🌐
          </div>
          <h4 className="text-white font-semibold mb-4">Internet</h4>
          
          <ul className="space-y-2 text-sm text-gray-400">
            <li className="flex items-center">
              <span className="text-red-400 mr-2">✗</span>
              Cloud API calls
            </li>
            <li className="flex items-center">
              <span className="text-red-400 mr-2">✗</span>
              External data uploads
            </li>
            <li className="flex items-center">
              <span className="text-red-400 mr-2">✗</span>
              Third-party sharing
            </li>
            <li className="flex items-center">
              <span className="text-red-400 mr-2">✗</span>
              Telemetry / analytics
            </li>
            <li className="flex items-center">
              <span className="text-red-400 mr-2">✗</span>
              Remote model hosting
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-gray-700">
        <div className="flex items-center justify-center">
          <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
          <span className="text-sm text-green-400 font-mono">100% Local Processing • AES-256 Encrypted • Zero Data Leakage</span>
        </div>
      </div>
    </div>
  );
};

export default DataFlowMonitor;