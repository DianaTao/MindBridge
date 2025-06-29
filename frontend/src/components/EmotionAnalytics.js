import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';
import HRWellnessDashboard from './HRWellnessDashboard';
import './EmotionAnalytics.css';

const EmotionAnalytics = ({ userEmail }) => {
  const [checkins, setCheckins] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCheckin, setSelectedCheckin] = useState(null);
  const [timeRange, setTimeRange] = useState(30); // days
  const [isHRUser, setIsHRUser] = useState(false);
  const [showHRDashboard, setShowHRDashboard] = useState(false);

  // Use email as user identifier
  const userId = userEmail || 'anonymous';

  console.log('🔍 EmotionAnalytics using user email:', userId);

  useEffect(() => {
    loadCheckinData();
    checkUserRole();
  }, [timeRange, userId]);

  const checkUserRole = async () => {
    try {
      // Check if user has HR role based on email domain or specific email addresses
      const hrDomains = ['hr.', 'people.', 'talent.'];
      const hrEmails = ['hr@company.com', 'peopleops@company.com', 'talent@company.com'];

      const isHR =
        hrDomains.some(domain => userEmail?.includes(domain)) ||
        hrEmails.includes(userEmail?.toLowerCase());

      setIsHRUser(isHR);
    } catch (err) {
      console.error('Failed to check user role:', err);
      setIsHRUser(false);
    }
  };

  const loadCheckinData = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📊 Loading check-in data...');
      const data = await ApiService.getCheckinData({
        user_id: userId,
        days: timeRange,
        limit: 50,
      });

      console.log('✅ Check-in data loaded:', data);
      setCheckins(data.checkins || []);
      setAnalytics(data.analytics_summary || {});
    } catch (err) {
      console.error('❌ Failed to load check-in data:', err);
      setError('Failed to load check-in data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = timestamp => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMoodColor = score => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#F59E0B'; // Yellow
    if (score >= 40) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  const getTrendIcon = trend => {
    switch (trend) {
      case 'improving':
        return '📈';
      case 'declining':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '❓';
    }
  };

  const getTrendColor = trend => {
    switch (trend) {
      case 'improving':
        return '#10B981';
      case 'declining':
        return '#EF4444';
      case 'stable':
        return '#6B7280';
      default:
        return '#9CA3AF';
    }
  };

  if (loading) {
    return (
      <div className="emotion-analytics">
        <div className="analytics-header">
          <h2>🧠 Emotion Analytics</h2>
          <p>Loading your mental health insights...</p>
        </div>
        <div className="loading-spinner">🔄</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="emotion-analytics">
        <div className="analytics-header">
          <h2>🧠 Emotion Analytics</h2>
          <p className="error-message">{error}</p>
          <button onClick={loadCheckinData} className="retry-button">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="emotion-analytics">
      <div className="analytics-header">
        <h2>🧠 Emotion Analytics</h2>
        <div className="header-controls">
          {isHRUser && (
            <button
              onClick={() => setShowHRDashboard(!showHRDashboard)}
              className={`hr-toggle-button ${showHRDashboard ? 'active' : ''}`}
            >
              {showHRDashboard ? '👤 Personal View' : '🏢 HR Dashboard'}
            </button>
          )}
          <select
            value={timeRange}
            onChange={e => setTimeRange(Number(e.target.value))}
            className="time-range-select"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button onClick={loadCheckinData} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* HR Wellness Dashboard */}
      {isHRUser && showHRDashboard && (
        <HRWellnessDashboard userEmail={userEmail} isHRUser={isHRUser} />
      )}

      {/* Personal Analytics View */}
      {(!isHRUser || !showHRDashboard) && (
        <>
          {checkins.length === 0 ? (
            <div className="no-data">
              <div className="no-data-icon">📊</div>
              <h3>No Check-in Data Available</h3>
              <p>Complete your first mental health check-in to see analytics here.</p>
              <p>
                Your data will be stored securely and analyzed to provide personalized insights.
              </p>
            </div>
          ) : (
            <>
              {/* Analytics Summary */}
              {analytics && (
                <div className="analytics-summary">
                  <div className="summary-card">
                    <h3>📈 Overall Summary</h3>
                    <div className="summary-stats">
                      <div className="stat">
                        <span className="stat-label">Total Check-ins</span>
                        <span className="stat-value">{analytics.total_checkins}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Average Score</span>
                        <span
                          className="stat-value"
                          style={{ color: getMoodColor(analytics.average_score) }}
                        >
                          {analytics.average_score}/100
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Mood Trend</span>
                        <span
                          className="stat-value"
                          style={{ color: getTrendColor(analytics.mood_trend) }}
                        >
                          {getTrendIcon(analytics.mood_trend)} {analytics.mood_trend}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Common Emotion</span>
                        <span className="stat-value">{analytics.most_common_emotion}</span>
                      </div>
                    </div>
                    <div className="period-covered">Period: {analytics.period_covered}</div>
                  </div>

                  {/* Recommendations */}
                  {analytics.recommendations && analytics.recommendations.length > 0 && (
                    <div className="recommendations-card">
                      <h3>
                        💡 Personalized Recommendations
                        {analytics.has_llm_data && (
                          <span className="llm-badge">🤖 AI Generated</span>
                        )}
                      </h3>
                      <ul className="recommendations-list">
                        {analytics.recommendations.map((rec, index) => (
                          <li key={index} className="recommendation-item">
                            {rec}
                          </li>
                        ))}
                      </ul>

                      {/* LLM Insights Section */}
                      {analytics.llm_insights && analytics.llm_insights.length > 0 && (
                        <div className="llm-insights-section">
                          <h4>🧠 AI Insights</h4>
                          <ul className="insights-list">
                            {analytics.llm_insights.map((insight, index) => (
                              <li key={index} className="insight-item">
                                {insight}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Latest LLM Report Summary */}
                      {analytics.latest_llm_report && (
                        <div className="latest-llm-summary">
                          <h4>📊 Latest AI Analysis</h4>
                          <div className="llm-summary-content">
                            <p className="emotional-summary">
                              {analytics.latest_llm_report.emotional_summary}
                            </p>
                            <div className="llm-metrics">
                              <span className="metric">
                                Mood Score: {analytics.latest_llm_report.mood_score || 'N/A'}/10
                              </span>
                              <span className="metric">
                                Confidence: {analytics.latest_llm_report.confidence_level || 'N/A'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Check-in History */}
              <div className="checkin-history">
                <h3>📋 Check-in History</h3>
                <div className="checkin-list">
                  {checkins.map(checkin => (
                    <div
                      key={checkin.checkin_id}
                      className="checkin-item"
                      onClick={() =>
                        setSelectedCheckin(
                          selectedCheckin?.checkin_id === checkin.checkin_id ? null : checkin
                        )
                      }
                    >
                      <div className="checkin-header">
                        <div className="checkin-date">{formatDate(checkin.timestamp)}</div>
                        <div
                          className="checkin-score"
                          style={{ color: getMoodColor(checkin.overall_score || 50) }}
                        >
                          {checkin.overall_score || 50}/100
                        </div>
                      </div>

                      <div className="checkin-details">
                        <div className="detail">
                          <span className="detail-label">Duration:</span>
                          <span className="detail-value">{checkin.duration || 0}s</span>
                        </div>
                        {checkin.emotion_analysis?.dominant_emotion && (
                          <div className="detail">
                            <span className="detail-label">Emotion:</span>
                            <span className="detail-value">
                              {checkin.emotion_analysis.dominant_emotion}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Expanded LLM Report */}
                      {selectedCheckin?.checkin_id === checkin.checkin_id && checkin.llm_report && (
                        <div className="llm-report">
                          <h4>🤖 AI Analysis Report</h4>

                          {checkin.llm_report.emotional_summary && (
                            <div className="report-section">
                              <h5>Emotional Summary</h5>
                              <p>{checkin.llm_report.emotional_summary}</p>
                            </div>
                          )}

                          {checkin.llm_report.key_insights &&
                            checkin.llm_report.key_insights.length > 0 && (
                              <div className="report-section">
                                <h5>Key Insights</h5>
                                <ul>
                                  {checkin.llm_report.key_insights.map((insight, index) => (
                                    <li key={index}>{insight}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                          {checkin.llm_report.recommendations &&
                            checkin.llm_report.recommendations.length > 0 && (
                              <div className="report-section">
                                <h5>Recommendations</h5>
                                <ul>
                                  {checkin.llm_report.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                          {checkin.llm_report.trend_analysis && (
                            <div className="report-section">
                              <h5>Trend Analysis</h5>
                              <p>{checkin.llm_report.trend_analysis}</p>
                            </div>
                          )}

                          {checkin.llm_report.overall_assessment && (
                            <div className="report-section">
                              <h5>Overall Assessment</h5>
                              <p>{checkin.llm_report.overall_assessment}</p>
                            </div>
                          )}

                          <div className="report-meta">
                            <span>Mood Score: {checkin.llm_report.mood_score || 'N/A'}/10</span>
                            <span>Confidence: {checkin.llm_report.confidence_level || 'N/A'}</span>
                            {checkin.llm_report.fallback_generated && (
                              <span className="fallback-indicator">⚠️ Fallback Report</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default EmotionAnalytics;
