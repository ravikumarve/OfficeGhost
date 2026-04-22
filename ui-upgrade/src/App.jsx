import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import EmailBrain from './components/EmailBrain';
import FileCommander from './components/FileCommander';
import Learning from './components/Learning';
import Security from './components/Security';
import Assistant from './components/Assistant';
import Settings from './components/Settings';
import Login from './components/Login';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <Router>
          <div className="App min-h-screen bg-gray-900 text-white">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<Dashboard />} />
              <Route path="/email" element={<EmailBrain />} />
              <Route path="/files" element={<FileCommander />} />
              <Route path="/learning" element={<Learning />} />
              <Route path="/security" element={<Security />} />
              <Route path="/assistant" element={<Assistant />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </Router>
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;