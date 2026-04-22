import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [password, setPassword] = useState('');
  const [totpToken, setTotpToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [require2FA, setRequire2FA] = useState(false);
  const { login, requireSetup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(password, totpToken || null);
    
    if (!result.success) {
      setError(result.error);
      // Check if 2FA is required
      if (result.error && result.error.includes('2FA')) {
        setRequire2FA(true);
      }
    }
    
    setLoading(false);
  };

  if (requireSetup) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Setup Required</h1>
            <p className="text-gray-400">Please complete the setup wizard first</p>
          </div>
          <a 
            href="http://localhost:5000/setup"
            className="block w-full bg-amber-500 hover:bg-amber-600 text-gray-900 font-semibold py-3 px-4 rounded-lg text-center transition-all duration-200"
          >
            Go to Setup Wizard
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
            👻
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">GhostOffice</h1>
          <p className="text-gray-400">Your private AI assistant for email, files & data</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-300 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
              placeholder="••••••••••••"
              required
              minLength={12}
            />
            <p className="text-xs text-gray-500 mt-1">Minimum 12 characters</p>
          </div>

          {require2FA && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                2FA Code
              </label>
              <input
                type="text"
                value={totpToken}
                onChange={(e) => setTotpToken(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
                placeholder="123456"
                maxLength={6}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber-500 hover:bg-amber-600 disabled:bg-amber-500/50 text-gray-900 font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-gray-900 border-t-transparent rounded-full animate-spin mr-2"></div>
                Signing in...
              </div>
            ) : (
              '🔓 Sign In'
            )}
          </button>
        </form>

        {/* Security Features */}
        <div className="mt-8 pt-6 border-t border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Security Features</h3>
          <ul className="space-y-2 text-xs text-gray-500">
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              AES-256 Encryption
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              100% Local Processing
            </li>
            <li className="flex items-center">
              <span className="text-green-400 mr-2">✓</span>
              Zero Data Sent to Cloud
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;