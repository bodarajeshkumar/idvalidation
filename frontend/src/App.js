import React, { useState, useEffect } from 'react';
import {
  Content,
  Theme,
  Grid,
  Column,
  DatePicker,
  DatePickerInput,
  Button,
  InlineNotification,
  ProgressBar,
  Tile,
  SkeletonText,
  Tag
} from '@carbon/react';
import { Renew, CheckmarkFilled, ErrorFilled, InProgress, StopFilled } from '@carbon/icons-react';
import axios from 'axios';
import './App.scss';

const API_BASE_URL = window.RUNTIME_CONFIG?.API_URL || process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
  const [startDate, setStartDate] = useState('01/01/2023');
  const [endDate, setEndDate] = useState('12/31/2024');
  const [status, setStatus] = useState('not_started');
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);
  const [history, setHistory] = useState([]);

  // Fetch history on mount and when status changes to finished/cancelled/error
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/history`);
        setHistory(response.data.history || []);
      } catch (err) {
        console.error('Error fetching history:', err);
      }
    };

    fetchHistory();

    // Refetch when retrieval completes
    if (status === 'finished' || status === 'cancelled' || status === 'error') {
      setTimeout(fetchHistory, 1000); // Small delay to ensure backend saved history
    }
  }, [status]);

  // Poll status every 2 seconds when processing
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/status`);
        setStatusData(response.data);
        setStatus(response.data.status);
      } catch (err) {
        console.error('Error fetching status:', err);
      }
    };

    fetchStatus(); // Initial fetch

    const interval = setInterval(() => {
      fetchStatus();
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, []);

  const handleStartRetrieval = async () => {
    setLoading(true);
    setError(null);
    setNotification(null);

    try {
      // Convert MM/DD/YYYY to YYYY-MM-DD
      const formatDate = (dateStr) => {
        const [month, day, year] = dateStr.split('/');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
      };

      const response = await axios.post(`${API_BASE_URL}/api/retrieve`, {
        start_date: formatDate(startDate),
        end_date: formatDate(endDate)
      });

      setNotification({
        kind: 'success',
        title: 'Success',
        subtitle: response.data.message
      });
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message;
      setError(errorMsg);
      setNotification({
        kind: 'error',
        title: 'Error',
        subtitle: errorMsg
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStopRetrieval = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/stop`);
      setNotification({
        kind: 'warning',
        title: 'Stopping',
        subtitle: response.data.message
      });
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message;
      setNotification({
        kind: 'error',
        title: 'Error',
        subtitle: errorMsg
      });
    }
  };

  const handleReset = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/reset`);
      setNotification({
        kind: 'info',
        title: 'Reset',
        subtitle: 'Status has been reset'
      });
    } catch (err) {
      console.error('Error resetting:', err);
    }
  };

  const getStatusTag = () => {
    switch (status) {
      case 'not_started':
        return <Tag type="gray">Not Started</Tag>;
      case 'processing':
        return <Tag type="blue" renderIcon={InProgress}>Processing</Tag>;
      case 'finished':
        return <Tag type="green" renderIcon={CheckmarkFilled}>Finished</Tag>;
      case 'cancelled':
        return <Tag type="magenta" renderIcon={StopFilled}>Cancelled</Tag>;
      case 'error':
        return <Tag type="red" renderIcon={ErrorFilled}>Error</Tag>;
      default:
        return <Tag type="gray">Unknown</Tag>;
    }
  };

  const isButtonDisabled = status === 'processing' || loading;

  return (
    <Theme theme="g100">
      <Content className="app-content">
        <Grid className="app-grid">
          <Column lg={16} md={8} sm={4}>
            <div className="app-header">
              <h1>Data Retrieval System</h1>
              <p>Retrieve data from Cloudant database by date range</p>
            </div>
          </Column>

          {notification && (
            <Column lg={16} md={8} sm={4}>
              <InlineNotification
                kind={notification.kind}
                title={notification.title}
                subtitle={notification.subtitle}
                onCloseButtonClick={() => setNotification(null)}
                lowContrast
              />
            </Column>
          )}

          <Column lg={16} md={8} sm={4}>
            <Tile className="status-tile">
              <div className="status-header">
                <h3>Current Status</h3>
                {getStatusTag()}
              </div>

              {statusData && (
                <div className="status-details">
                  {status === 'processing' && (
                    <>
                      <div className="status-row">
                        <span className="label">Progress:</span>
                        <span className="value">
                          {statusData.progress.completed_months} / {statusData.progress.total_months} months
                        </span>
                      </div>
                      <div className="status-row">
                        <span className="label">Records Retrieved:</span>
                        <span className="value">
                          {statusData.progress.total_records.toLocaleString()}
                        </span>
                      </div>
                      {statusData.start_time && (
                        <div className="status-row">
                          <span className="label">Elapsed Time:</span>
                          <span className="value">
                            {(() => {
                              const start = new Date(statusData.start_time);
                              const now = new Date();
                              const diffMs = now - start;
                              const diffMins = Math.floor(diffMs / 60000);
                              const diffSecs = Math.floor((diffMs % 60000) / 1000);
                              return `${diffMins}m ${diffSecs}s`;
                            })()}
                          </span>
                        </div>
                      )}
                      <ProgressBar
                        label="Retrieval Progress"
                        value={statusData.progress.percentage || 0}
                        max={100}
                        helperText={
                          statusData.progress.percentage > 0
                            ? `${statusData.progress.percentage.toFixed(2)}% complete`
                            : 'Processing... (progress updates when months complete)'
                        }
                      />
                    </>
                  )}

                  {status === 'finished' && statusData.stats && (
                    <>
                      <div className="success-banner">
                        <CheckmarkFilled size={32} />
                        <div className="success-content">
                          <h4>✅ Retrieval Completed Successfully!</h4>
                          <p>All data has been retrieved and saved to the output directory.</p>
                        </div>
                      </div>
                      
                      <div className="status-row highlight">
                        <span className="label">Total Records Retrieved:</span>
                        <span className="value">
                          {statusData.stats.total_records.toLocaleString()}
                        </span>
                      </div>
                      <div className="status-row highlight">
                        <span className="label">Total Time Taken:</span>
                        <span className="value">
                          {(() => {
                            const minutes = Math.floor(statusData.stats.duration_seconds / 60);
                            const seconds = Math.floor(statusData.stats.duration_seconds % 60);
                            const hours = Math.floor(minutes / 60);
                            const mins = minutes % 60;
                            
                            if (hours > 0) {
                              return `${hours}h ${mins}m ${seconds}s`;
                            } else if (minutes > 0) {
                              return `${minutes}m ${seconds}s`;
                            } else {
                              return `${seconds}s`;
                            }
                          })()}
                        </span>
                      </div>
                      <div className="status-row">
                        <span className="label">Retrieval Speed:</span>
                        <span className="value">
                          {statusData.stats.records_per_second.toFixed(0)} records/sec
                        </span>
                      </div>
                      <div className="status-row">
                        <span className="label">Months Processed:</span>
                        <span className="value">
                          {statusData.stats.completed_months} / {statusData.stats.total_months}
                        </span>
                      </div>
                      <div className="status-row">
                        <span className="label">Output Location:</span>
                        <span className="value">
                          ./output/ directory
                        </span>
                      </div>
                    </>
                  )}

                  {status === 'error' && (
                    <div className="error-message">
                      <ErrorFilled size={20} />
                      <span>{statusData.error}</span>
                    </div>
                  )}

                  {status === 'cancelled' && (
                    <div className="cancelled-message">
                      <StopFilled size={20} />
                      <span>Retrieval was cancelled by user</span>
                    </div>
                  )}

                  {status === 'not_started' && (
                    <p className="info-text">
                      No retrieval in progress. Configure date range and click "Start Retrieval" to begin.
                    </p>
                  )}
                </div>
              )}

              {!statusData && <SkeletonText />}
            </Tile>
          </Column>

          <Column lg={16} md={8} sm={4}>
            <Tile className="control-tile">
              <h3>Date Range Selection</h3>
              <p className="helper-text">
                Select the start and end dates for data retrieval
              </p>

              <div className="date-picker-container">
                <DatePicker
                  datePickerType="single"
                  dateFormat="m/d/Y"
                  onChange={(dates) => {
                    if (dates && dates.length > 0) {
                      const date = dates[0];
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const day = String(date.getDate()).padStart(2, '0');
                      const year = date.getFullYear();
                      setStartDate(`${month}/${day}/${year}`);
                    }
                  }}
                >
                  <DatePickerInput
                    id="start-date"
                    placeholder="mm/dd/yyyy"
                    labelText="Start Date"
                    size="lg"
                    disabled={isButtonDisabled}
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </DatePicker>

                <DatePicker
                  datePickerType="single"
                  dateFormat="m/d/Y"
                  onChange={(dates) => {
                    if (dates && dates.length > 0) {
                      const date = dates[0];
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const day = String(date.getDate()).padStart(2, '0');
                      const year = date.getFullYear();
                      setEndDate(`${month}/${day}/${year}`);
                    }
                  }}
                >
                  <DatePickerInput
                    id="end-date"
                    placeholder="mm/dd/yyyy"
                    labelText="End Date"
                    size="lg"
                    disabled={isButtonDisabled}
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </DatePicker>
              </div>

              <div className="button-group">
                <Button
                  kind="primary"
                  size="lg"
                  onClick={handleStartRetrieval}
                  disabled={isButtonDisabled}
                  renderIcon={Renew}
                >
                  {loading ? 'Starting...' : 'Start Retrieval'}
                </Button>

                {status === 'processing' && (
                  <Button
                    kind="danger"
                    size="lg"
                    onClick={handleStopRetrieval}
                    renderIcon={StopFilled}
                  >
                    Stop Retrieval
                  </Button>
                )}

                {(status === 'finished' || status === 'error' || status === 'cancelled') && (
                  <Button
                    kind="secondary"
                    size="lg"
                    onClick={handleReset}
                  >
                    Reset
                  </Button>
                )}
              </div>

              {isButtonDisabled && status === 'processing' && (
                <p className="warning-text">
                  ⚠️ Retrieval in progress. Button is disabled until process completes.
                </p>
              )}
            </Tile>
          </Column>

          <Column lg={16} md={8} sm={4}>
            <Tile className="info-tile">
              <h4>System Information</h4>
              <ul>
                <li><strong>Database:</strong> Cloudant (IBM Cloud)</li>
                <li><strong>Total Records in DB:</strong> ~21.18 million</li>
                <li><strong>Selected Date Range:</strong> {startDate} to {endDate}</li>
                <li><strong>Output Format:</strong> JSONL (JSON Lines)</li>
                <li><strong>Output Directory:</strong> ./output/</li>
                <li><strong>Concurrent Processing:</strong> 3 months (default)</li>
                <li><strong>Page Size:</strong> 5,000 records per request</li>
                <li><strong>Rate Limit:</strong> 10 requests/second (default)</li>
              </ul>
              <p className="info-note">
                <strong>Note:</strong> Using default rate limiting and concurrency with optimized 5K page size.
                The system runs at natural API speed for reliable retrieval.
              </p>
            </Tile>
          </Column>

          {history.length > 0 && (
            <Column lg={16} md={8} sm={4}>
              <Tile className="history-tile">
                <h3>Retrieval History</h3>
                <p className="helper-text">Past retrieval operations with date ranges and performance metrics</p>
                
                <div className="history-table">
                  <div className="history-header">
                    <div className="history-col">Date Range</div>
                    <div className="history-col">Status</div>
                    <div className="history-col">Records</div>
                    <div className="history-col">Duration</div>
                    <div className="history-col">Speed</div>
                    <div className="history-col">Timestamp</div>
                  </div>
                  
                  {history.map((entry, index) => (
                    <div key={index} className="history-row">
                      <div className="history-col">
                        {entry.start_date} to {entry.end_date}
                      </div>
                      <div className="history-col">
                        {entry.status === 'finished' && (
                          <Tag type="green" size="sm" renderIcon={CheckmarkFilled}>Finished</Tag>
                        )}
                        {entry.status === 'cancelled' && (
                          <Tag type="magenta" size="sm" renderIcon={StopFilled}>Cancelled</Tag>
                        )}
                        {entry.status === 'error' && (
                          <Tag type="red" size="sm" renderIcon={ErrorFilled}>Error</Tag>
                        )}
                      </div>
                      <div className="history-col">
                        {entry.records.toLocaleString()}
                      </div>
                      <div className="history-col">
                        {entry.duration}
                      </div>
                      <div className="history-col">
                        {entry.records_per_second > 0
                          ? `${entry.records_per_second.toFixed(0)} rec/s`
                          : 'N/A'}
                      </div>
                      <div className="history-col history-timestamp">
                        {new Date(entry.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </Tile>
            </Column>
          )}
        </Grid>
      </Content>
    </Theme>
  );
}

export default App;

// Made with Bob
