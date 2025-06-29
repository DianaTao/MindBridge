import React, { useState, useEffect } from 'react';
import { Mail, Lock, User, LogOut } from 'lucide-react';
import './EmailAuth.css';

const EmailAuth = ({ onAuthChange }) => {
  const [email, setEmail] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    // Check if user is already authenticated
    const savedEmail = localStorage.getItem('mindbridge_user_email');
    if (savedEmail) {
      setEmail(savedEmail);
      setIsAuthenticated(true);
      setUserProfile({ email: savedEmail });
      onAuthChange(savedEmail);
    }
  }, [onAuthChange]);

  const handleSignIn = async e => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Simple email validation and authentication
      // In a real app, you'd call an authentication service
      const userEmail = email.toLowerCase().trim();

      // Store email in localStorage
      localStorage.setItem('mindbridge_user_email', userEmail);
      localStorage.removeItem('mindbridge_user_id'); // Remove old random user ID

      setIsAuthenticated(true);
      setUserProfile({ email: userEmail });
      onAuthChange(userEmail);

      console.log('🆔 User authenticated with email:', userEmail);
    } catch (err) {
      console.error('❌ Authentication error:', err);
      setError('Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    // Clear authentication data
    localStorage.removeItem('mindbridge_user_email');
    localStorage.removeItem('mindbridge_user_id');

    setIsAuthenticated(false);
    setUserProfile(null);
    setEmail('');
    onAuthChange(null);

    console.log('👋 User signed out');
  };

  if (isAuthenticated) {
    return (
      <div className="email-auth-container">
        <div className="auth-card authenticated">
          <div className="auth-header">
            <User className="auth-icon" />
            <h3>Welcome Back!</h3>
          </div>

          <div className="user-info">
            <div className="user-email">
              <Mail className="email-icon" />
              <span>{userProfile?.email}</span>
            </div>
            <p className="user-status">✅ Authenticated</p>
          </div>

          <button onClick={handleSignOut} className="sign-out-button" disabled={loading}>
            <LogOut className="button-icon" />
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="email-auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <Mail className="auth-icon" />
          <h3>Sign In to MindBridge</h3>
          <p>Enter your email to access your mental health analytics</p>
        </div>

        <form onSubmit={handleSignIn} className="auth-form">
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" />
              <input
                type="email"
                id="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Enter your email address"
                required
                disabled={loading}
              />
            </div>
          </div>

          {error && <div className="error-message">❌ {error}</div>}

          <button type="submit" className="sign-in-button" disabled={loading || !email}>
            {loading ? (
              <>
                <div className="loading-spinner"></div>
                Signing In...
              </>
            ) : (
              <>
                <Lock className="button-icon" />
                Sign In
              </>
            )}
          </button>
        </form>

        <div className="auth-info">
          <p>🔒 Your email will be used as your unique identifier</p>
          <p>📊 All your mental health data will be linked to this email</p>
          <p>🛡️ No password required - simple and secure</p>
        </div>
      </div>
    </div>
  );
};

export default EmailAuth;
