import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const Simple = () => {
  const [systemStatus, setSystemStatus] = useState({
    apiConnected: false,
    modelsLoaded: false,
    lastCheck: null,
    error: null
  });
  const [isChecking, setIsChecking] = useState(false);

  const checkSystemStatus = async () => {
    setIsChecking(true);
    try {
      // Test API connectivity
      const testResult = await ApiService.testConnection();
      setSystemStatus({
        apiConnected: true,
        modelsLoaded: testResult.models_loaded || false,
        lastCheck: new Date().toISOString(),
        error: null
      });
    } catch (error) {
      setSystemStatus({
        apiConnected: false,
        modelsLoaded: false,
        lastCheck: new Date().toISOString(),
        error: error.message
      });
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkSystemStatus();
  }, []);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">System Status</h3>
        <p className="text-gray-600">Check the status of MindBridge services</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* API Connection Status */}
        <div className="p-4 bg-white border rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">API Connection</h4>
              <p className="text-sm text-gray-500">Backend service connectivity</p>
            </div>
            <div className={`w-4 h-4 rounded-full ${systemStatus.apiConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          </div>
          {systemStatus.error && (
            <p className="text-xs text-red-600 mt-2">{systemStatus.error}</p>
          )}
        </div>

        {/* Models Status */}
        <div className="p-4 bg-white border rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">AI Models</h4>
              <p className="text-sm text-gray-500">Emotion detection models</p>
            </div>
            <div className={`w-4 h-4 rounded-full ${systemStatus.modelsLoaded ? 'bg-green-500' : 'bg-yellow-500'}`} />
          </div>
          <p className="text-xs text-gray-600 mt-2">
            {systemStatus.modelsLoaded ? 'Models loaded and ready' : 'Models loading...'}
          </p>
        </div>
      </div>

      {/* Last Check Time */}
      {systemStatus.lastCheck && (
        <div className="text-center text-sm text-gray-500">
          Last checked: {new Date(systemStatus.lastCheck).toLocaleTimeString()}
        </div>
      )}

      {/* Test Button */}
      <div className="text-center">
        <button
          onClick={checkSystemStatus}
          disabled={isChecking}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          {isChecking ? 'Checking...' : 'Check Status'}
        </button>
      </div>

      {/* System Information */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">System Information</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Frontend Version:</span>
            <span className="font-medium">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Browser:</span>
            <span className="font-medium">{navigator.userAgent.split(' ').pop()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Screen Resolution:</span>
            <span className="font-medium">{window.screen.width}x{window.screen.height}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Local Time:</span>
            <span className="font-medium">{new Date().toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Simple;
