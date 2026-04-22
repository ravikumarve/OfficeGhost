import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import { apiCall } from '../hooks/useApi';

const EmailBrain = () => {
  const [emails, setEmails] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [showReplyModal, setShowReplyModal] = useState(false);

  useEffect(() => {
    const fetchEmailData = async () => {
      try {
        const data = await apiCall('/api/emails');
        setEmails(data.emails || []);
        setStats(data.stats || {});
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch email data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchEmailData();
  }, []);

  const handleScanEmails = async () => {
    try {
      await apiCall('/api/emails/scan', { method: 'POST' });
      // Refresh email data after scan
      const data = await apiCall('/api/emails');
      setEmails(data.emails || []);
      setStats(data.stats || {});
    } catch (err) {
      console.error('Failed to scan emails:', err);
      alert('Failed to scan emails: ' + err.message);
    }
  };

  const handleReply = (email) => {
    setSelectedEmail(email);
    setShowReplyModal(true);
  };

  const closeReplyModal = () => {
    setShowReplyModal(false);
    setSelectedEmail(null);
  };

  const sendReply = async (replyText) => {
    try {
      await apiCall('/api/emails/reply', {
        method: 'POST',
        body: JSON.stringify({
          email_id: selectedEmail.id,
          reply: replyText
        })
      });
      alert('Reply sent successfully');
      closeReplyModal();
    } catch (err) {
      console.error('Failed to send reply:', err);
      alert('Failed to send reply: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-900">
        <Sidebar />
        <main className="flex-1 p-6 ml-64 flex items-center justify-center">
          <div className="text-white text-xl">Loading email data...</div>
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

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar />
      
      <main className="flex-1 p-6 ml-64">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Email Brain</h1>
            <p className="text-gray-400">AI-powered email classification and smart replies</p>
          </div>
          <button 
            onClick={handleScanEmails}
            className="bg-amber-500 hover:bg-amber-600 text-gray-900 font-semibold px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            📧 Scan Emails
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">Total Processed</div>
              <div className="text-white text-2xl font-bold">{stats.total || 0}</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">URGENT</div>
              <div className="text-red-400 text-2xl font-bold">{stats.urgent || 0}</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">ROUTINE</div>
              <div className="text-blue-400 text-2xl font-bold">{stats.routine || 0}</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">MEETING</div>
              <div className="text-green-400 text-2xl font-bold">{stats.meeting || 0}</div>
            </div>
          </div>
        )}

        {/* Email List */}
        <div className="bg-gray-800 rounded-xl border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">Recent Emails</h2>
          </div>
          
          {emails.length > 0 ? (
            <div className="divide-y divide-gray-700">
              {emails.map((email, index) => (
                <div key={index} className="p-6 hover:bg-gray-750 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-white font-medium">{email.sender_name || email.sender}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          email.classification === 'URGENT' ? 'bg-red-500/20 text-red-400' :
                          email.classification === 'ROUTINE' ? 'bg-blue-500/20 text-blue-400' :
                          email.classification === 'MEETING' ? 'bg-green-500/20 text-green-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {email.classification}
                        </span>
                      </div>
                      <div className="text-gray-300 mb-2">{email.subject}</div>
                      <div className="text-gray-500 text-sm">{new Date(email.timestamp).toLocaleString()}</div>
                    </div>
                    <button 
                      onClick={() => handleReply(email)}
                      className="ml-4 bg-amber-500 hover:bg-amber-600 text-gray-900 font-medium px-4 py-2 rounded-lg transition-colors"
                    >
                      Reply
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-lg mb-4">📭 No emails processed yet</div>
              <button 
                onClick={handleScanEmails}
                className="bg-amber-500 hover:bg-amber-600 text-gray-900 font-semibold px-6 py-3 rounded-lg transition-all duration-200"
              >
                Scan Emails Now
              </button>
            </div>
          )}
        </div>

        {/* Reply Modal */}
        {showReplyModal && selectedEmail && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-xl p-6 w-full max-w-2xl border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-white">Reply to {selectedEmail.sender_name}</h3>
                <button 
                  onClick={closeReplyModal}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <div className="mb-4">
                <div className="text-gray-400 text-sm mb-2">Subject: {selectedEmail.subject}</div>
                <textarea
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-white min-h-[200px] focus:outline-none focus:border-amber-500"
                  placeholder="Type your reply..."
                  id="reply-text"
                />
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  onClick={closeReplyModal}
                  className="px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    const replyText = document.getElementById('reply-text').value;
                    if (replyText.trim()) {
                      sendReply(replyText);
                    }
                  }}
                  className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-gray-900 font-semibold transition-colors"
                >
                  Send Reply
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default EmailBrain;