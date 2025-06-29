import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';
import './HRWellnessDashboard.css';

const HRWellnessDashboard = ({ userEmail, isHRUser = false }) => {
  const [wellnessData, setWellnessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [timeRange, setTimeRange] = useState(30);
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [riskLevel, setRiskLevel] = useState('all');
  const [viewMode, setViewMode] = useState('overview');

  useEffect(() => {
    if (isHRUser) {
      loadWellnessData();
    }
  }, [timeRange, filterDepartment, riskLevel, isHRUser]);

  const loadWellnessData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Call the actual API for HR wellness data
      const data = await ApiService.getHRWellnessData({
        user_id: userEmail,
        time_range: timeRange,
        department: filterDepartment,
        risk_level: riskLevel,
      });

      setWellnessData(data);
    } catch (err) {
      console.error('Failed to load wellness data:', err);
      setError('Failed to load wellness data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = score => {
    if (score >= 80) return '#EF4444'; // Red - High risk
    if (score >= 60) return '#F59E0B'; // Yellow - Medium risk
    return '#10B981'; // Green - Low risk
  };

  const getRiskLevel = score => {
    if (score >= 80) return 'High';
    if (score >= 60) return 'Medium';
    return 'Low';
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

  const formatDate = timestamp => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getInterventionStatusColor = status => {
    switch (status) {
      case 'completed':
        return '#10B981';
      case 'active':
        return '#3B82F6';
      case 'scheduled':
        return '#F59E0B';
      case 'pending':
        return '#6B7280';
      default:
        return '#9CA3AF';
    }
  };

  if (!isHRUser) {
    return null;
  }

  if (loading) {
    return (
      <div className="hr-wellness-dashboard">
        <div className="dashboard-header">
          <h2>🏢 HR Wellness Dashboard</h2>
          <p>Loading corporate wellness insights...</p>
        </div>
        <div className="loading-spinner">🔄</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="hr-wellness-dashboard">
        <div className="dashboard-header">
          <h2>🏢 HR Wellness Dashboard</h2>
          <p className="error-message">{error}</p>
          <button onClick={loadWellnessData} className="retry-button">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  if (!wellnessData) {
    return (
      <div className="hr-wellness-dashboard">
        <div className="dashboard-header">
          <h2>🏢 HR Wellness Dashboard</h2>
          <p>No wellness data available. Please check back later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="hr-wellness-dashboard">
      <div className="dashboard-header">
        <h2>🏢 HR Wellness Dashboard</h2>
        <div className="header-controls">
          <select
            value={timeRange}
            onChange={e => setTimeRange(Number(e.target.value))}
            className="time-range-select"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <select
            value={filterDepartment}
            onChange={e => setFilterDepartment(e.target.value)}
            className="department-select"
          >
            <option value="all">All Departments</option>
            {wellnessData.departments?.map(dept => (
              <option key={dept.name} value={dept.name}>
                {dept.name}
              </option>
            ))}
          </select>
          <select
            value={riskLevel}
            onChange={e => setRiskLevel(e.target.value)}
            className="risk-select"
          >
            <option value="all">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
          <button onClick={loadWellnessData} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="view-mode-tabs">
        <button
          className={`tab ${viewMode === 'overview' ? 'active' : ''}`}
          onClick={() => setViewMode('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`tab ${viewMode === 'details' ? 'active' : ''}`}
          onClick={() => setViewMode('details')}
        >
          👥 Employee Details
        </button>
        <button
          className={`tab ${viewMode === 'interventions' ? 'active' : ''}`}
          onClick={() => setViewMode('interventions')}
        >
          🎯 Interventions
        </button>
      </div>

      {viewMode === 'overview' && wellnessData.company_metrics && (
        <div className="overview-section">
          <div className="metrics-grid">
            <div className="metric-card primary">
              <h3>📈 Company Overview</h3>
              <div className="metric-stats">
                {wellnessData.company_metrics.total_employees && (
                  <div className="metric">
                    <span className="metric-label">Total Employees</span>
                    <span className="metric-value">
                      {wellnessData.company_metrics.total_employees}
                    </span>
                  </div>
                )}
                {wellnessData.company_metrics.participation_rate && (
                  <div className="metric">
                    <span className="metric-label">Participation Rate</span>
                    <span className="metric-value">
                      {wellnessData.company_metrics.participation_rate}%
                    </span>
                  </div>
                )}
                {wellnessData.company_metrics.avg_wellness_score && (
                  <div className="metric">
                    <span className="metric-label">Avg Wellness Score</span>
                    <span className="metric-value">
                      {wellnessData.company_metrics.avg_wellness_score}/100
                    </span>
                  </div>
                )}
                {wellnessData.company_metrics.burnout_risk_rate && (
                  <div className="metric">
                    <span className="metric-label">Burnout Risk Rate</span>
                    <span className="metric-value risk">
                      {wellnessData.company_metrics.burnout_risk_rate}%
                    </span>
                  </div>
                )}
              </div>
            </div>

            {wellnessData.company_metrics.high_risk_employees && (
              <div className="metric-card alert">
                <h3>🚨 High Priority Alerts</h3>
                <div className="alert-stats">
                  <div className="alert-item">
                    <span className="alert-label">High Risk Employees</span>
                    <span className="alert-value">
                      {wellnessData.company_metrics.high_risk_employees}
                    </span>
                  </div>
                  {wellnessData.company_metrics.interventions_needed && (
                    <div className="alert-item">
                      <span className="alert-label">Interventions Needed</span>
                      <span className="alert-value urgent">
                        {wellnessData.company_metrics.interventions_needed}
                      </span>
                    </div>
                  )}
                </div>
                <div className="alert-actions">
                  <button className="action-button primary">Review High Risk</button>
                  <button className="action-button secondary">Schedule Interventions</button>
                </div>
              </div>
            )}
          </div>

          {wellnessData.department_breakdown && (
            <div className="department-section">
              <h3>🏢 Department Breakdown</h3>
              <div className="department-grid">
                {wellnessData.department_breakdown.map(dept => (
                  <div key={dept.name} className="department-card">
                    <h4>{dept.name}</h4>
                    <div className="dept-stats">
                      {dept.avg_score && (
                        <div className="dept-stat">
                          <span className="stat-label">Avg Score</span>
                          <span className="stat-value">{dept.avg_score}/100</span>
                        </div>
                      )}
                      {dept.risk_rate && (
                        <div className="dept-stat">
                          <span className="stat-label">Risk Rate</span>
                          <span className="stat-value risk">{dept.risk_rate}%</span>
                        </div>
                      )}
                      {dept.high_risk && dept.employees && (
                        <div className="dept-stat">
                          <span className="stat-label">High Risk</span>
                          <span className="stat-value">
                            {dept.high_risk}/{dept.employees}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="dept-actions">
                      <button className="dept-action-btn">View Details</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {wellnessData.wellness_trends && (
            <div className="trends-section">
              <h3>📊 Wellness Trends</h3>
              <div className="trends-grid">
                {wellnessData.wellness_trends.weekly_data && (
                  <div className="trend-card">
                    <h4>Weekly Progress</h4>
                    <div className="trend-chart">
                      {wellnessData.wellness_trends.weekly_data.map((week, index) => (
                        <div key={week.week || index} className="trend-bar">
                          <div className="bar-label">{week.week}</div>
                          <div className="bar-container">
                            <div
                              className="bar"
                              style={{
                                height: `${week.avg_score}%`,
                                backgroundColor: getRiskColor(week.avg_score),
                              }}
                            ></div>
                          </div>
                          <div className="bar-value">{week.avg_score}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {wellnessData.wellness_trends.monthly_comparison && (
                  <div className="trend-card">
                    <h4>Monthly Comparison</h4>
                    <div className="comparison-stats">
                      <div className="comparison-item">
                        <span className="comparison-label">Current Month</span>
                        <span className="comparison-value">
                          {wellnessData.wellness_trends.monthly_comparison.current_month.avg_score}
                          /100
                        </span>
                      </div>
                      <div className="comparison-item">
                        <span className="comparison-label">Previous Month</span>
                        <span className="comparison-value">
                          {wellnessData.wellness_trends.monthly_comparison.previous_month.avg_score}
                          /100
                        </span>
                      </div>
                      <div className="comparison-change">
                        <span className="change-label">Change</span>
                        <span className="change-value positive">
                          +
                          {(
                            wellnessData.wellness_trends.monthly_comparison.current_month
                              .avg_score -
                            wellnessData.wellness_trends.monthly_comparison.previous_month.avg_score
                          ).toFixed(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {viewMode === 'details' && wellnessData.high_risk_employees && (
        <div className="details-section">
          <h3>👥 High Risk Employee Details</h3>
          <div className="employee-list">
            {wellnessData.high_risk_employees
              .filter(emp => filterDepartment === 'all' || emp.department === filterDepartment)
              .filter(emp => riskLevel === 'all' || emp.risk_level === riskLevel)
              .map(employee => (
                <div
                  key={employee.id}
                  className={`employee-card ${employee.risk_level}`}
                  onClick={() =>
                    setSelectedEmployee(selectedEmployee?.id === employee.id ? null : employee)
                  }
                >
                  <div className="employee-header">
                    <div className="employee-info">
                      <h4>{employee.name}</h4>
                      <p className="employee-details">
                        {employee.position} • {employee.department}
                      </p>
                      <p className="employee-email">{employee.email}</p>
                    </div>
                    <div className="employee-risk">
                      <div
                        className="risk-score"
                        style={{ color: getRiskColor(employee.risk_score) }}
                      >
                        {employee.risk_score}/100
                      </div>
                      <div className="risk-level">{getRiskLevel(employee.risk_score)} Risk</div>
                      {employee.trend && (
                        <div
                          className="trend-indicator"
                          style={{ color: getTrendColor(employee.trend) }}
                        >
                          {getTrendIcon(employee.trend)} {employee.trend}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="employee-metrics">
                    {employee.last_checkin && (
                      <div className="metric">
                        <span className="metric-label">Last Check-in</span>
                        <span className="metric-value">{formatDate(employee.last_checkin)}</span>
                      </div>
                    )}
                    {employee.symptoms && (
                      <div className="metric">
                        <span className="metric-label">Symptoms</span>
                        <span className="metric-value">{employee.symptoms.join(', ')}</span>
                      </div>
                    )}
                  </div>

                  {selectedEmployee?.id === employee.id && (
                    <div className="employee-details-expanded">
                      {employee.recommendations && employee.recommendations.length > 0 && (
                        <div className="details-section">
                          <h5>🎯 Recommendations</h5>
                          <ul className="recommendations-list">
                            {employee.recommendations.map((rec, index) => (
                              <li key={index} className="recommendation-item">
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {employee.interventions && employee.interventions.length > 0 && (
                        <div className="details-section">
                          <h5>📋 Interventions</h5>
                          <div className="interventions-list">
                            {employee.interventions.map((intervention, index) => (
                              <div key={index} className="intervention-item">
                                <div className="intervention-info">
                                  <span className="intervention-type">
                                    {intervention.type.replace('_', ' ')}
                                  </span>
                                  <span
                                    className="intervention-status"
                                    style={{
                                      color: getInterventionStatusColor(intervention.status),
                                    }}
                                  >
                                    {intervention.status}
                                  </span>
                                </div>
                                <div className="intervention-date">{intervention.date}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="action-buttons">
                        <button className="action-btn primary">Schedule Meeting</button>
                        <button className="action-btn secondary">Send Resources</button>
                        <button className="action-btn tertiary">Update Status</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {viewMode === 'interventions' && wellnessData.intervention_effectiveness && (
        <div className="interventions-section">
          <h3>🎯 Intervention Effectiveness</h3>
          <div className="interventions-grid">
            {wellnessData.intervention_effectiveness.map(intervention => (
              <div key={intervention.intervention} className="intervention-card">
                <h4>{intervention.intervention}</h4>
                <div className="intervention-stats">
                  <div className="intervention-stat">
                    <span className="stat-label">Success Rate</span>
                    <span className="stat-value success">{intervention.success_rate}%</span>
                  </div>
                  <div className="intervention-stat">
                    <span className="stat-label">Employees Helped</span>
                    <span className="stat-value">{intervention.employees_helped}</span>
                  </div>
                </div>
                <div className="intervention-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${intervention.success_rate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {wellnessData.intervention_insights && (
            <div className="intervention-insights">
              <h4>💡 Key Insights</h4>
              <div className="insights-grid">
                {wellnessData.intervention_insights.map((insight, index) => (
                  <div key={index} className="insight-card">
                    <h5>{insight.title}</h5>
                    <p>{insight.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HRWellnessDashboard;
