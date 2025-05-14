import React, { useState } from 'react';
import axios from 'axios';

interface PredictiveMaintenanceProps {
  filePath: string;
}

const PredictiveMaintenance: React.FC<PredictiveMaintenanceProps> = ({ filePath }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'anomaly' | 'forecast' | 'synthetic'>('anomaly');

  const runAnomalyDetection = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:5000/api/predictive/anomaly', {
        file_path: filePath,
        window_size: 10,
        forecast_horizon: 1
      });
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runForecasting = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:5000/api/predictive/forecast', {
        file_path: filePath,
        steps: 30
      });
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const generateSynthetic = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:5000/api/predictive/synthetic', {
        file_path: filePath,
        task: 'anomaly',
        anomaly_pct: 0.1,
        series_noise: 0.1
      });
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <div className="mb-4">
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => setActiveTab('anomaly')}
            className={`px-4 py-2 rounded ${
              activeTab === 'anomaly' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            Anomaly Detection
          </button>
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-4 py-2 rounded ${
              activeTab === 'forecast' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            Forecasting
          </button>
          <button
            onClick={() => setActiveTab('synthetic')}
            className={`px-4 py-2 rounded ${
              activeTab === 'synthetic' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            Synthetic Data
          </button>
        </div>

        {activeTab === 'anomaly' && (
          <div>
            <button
              onClick={runAnomalyDetection}
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
            >
              {loading ? 'Running...' : 'Run Anomaly Detection'}
            </button>
          </div>
        )}

        {activeTab === 'forecast' && (
          <div>
            <button
              onClick={runForecasting}
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
            >
              {loading ? 'Running...' : 'Run Forecasting'}
            </button>
          </div>
        )}

        {activeTab === 'synthetic' && (
          <div>
            <button
              onClick={generateSynthetic}
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
            >
              {loading ? 'Generating...' : 'Generate Synthetic Data'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {results && (
        <div className="mt-4">
          {results.summary && (
            <div className="mb-4 p-4 bg-gray-100 rounded">
              <h3 className="font-bold mb-2">Summary</h3>
              <p>{results.summary}</p>
            </div>
          )}

          {results.figures && results.figures.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.figures.map((figure: string, index: number) => (
                <div key={index} className="border rounded p-2">
                  <img
                    src={`data:image/png;base64,${figure}`}
                    alt={`Figure ${index + 1}`}
                    className="w-full"
                  />
                </div>
              ))}
            </div>
          )}

          {results.forecast && (
            <div className="mt-4">
              <h3 className="font-bold mb-2">Forecast Results</h3>
              <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
                {JSON.stringify(results.forecast, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PredictiveMaintenance; 